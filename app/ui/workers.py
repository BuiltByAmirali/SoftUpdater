"""Background workers (QThread). All UI updates happen via queued signals,
so the UI thread is never touched from worker threads - this fixes the crash
that occurred when checking updates after maximizing the window."""
from __future__ import annotations

import dataclasses
import threading

from PySide6.QtCore import QThread, Signal

from ..i18n import tr
from ..core.downloader import DownloadPaused, download
from ..core.installed_apps import (
    InstalledApp,
    build_fresh_index,
    match_fresh_version,
)
from ..core.update_checker import CheckResult, UpdateChecker


class CheckWorker(QThread):
    """Checks a list of installed apps one by one, emitting a result each.

    rescan_versions (default True): before checking, ONE fresh registry scan
    runs in this worker thread and every app is matched by registry-key
    identity (winget-style) with a strict normalized-name fallback - so if
    the user installed a downloaded update, the row's version refreshes to
    the ACTUAL installed one and the honest "Up to date" shows up without
    re-checking the whole list. Same-name-but-different-product entries
    (e.g. VC++ 2005 vs 2015-2022) can never cross-contaminate.
    """

    app_checked = Signal(object)          # CheckResult
    app_version_refreshed = Signal(str, str)  # old key "name|ver", fresh version
    progress = Signal(int, int)           # done, total
    finished_all = Signal(int, int, int)  # updates_found, failed, total

    def __init__(self, apps: list[InstalledApp], parent=None,
                 rescan_versions: bool = True):
        super().__init__(parent)
        self.apps = apps
        self.rescan_versions = bool(rescan_versions)
        self._cancel = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()

    def run(self) -> None:  # runs in worker thread
        total = len(self.apps)
        updates = failed = 0
        try:
            checker = UpdateChecker()
        except Exception as exc:
            for app in self.apps:
                res = CheckResult(app_name=app.name, installed_version=app.version)
                res.status = "failed"
                res.set_note("note.init_error", cls=exc.__class__.__name__)
                self.app_checked.emit(res)
            self.finished_all.emit(0, len(self.apps), total)
            return
        # Fresh registry scan (worker thread - the UI never blocks).
        index: dict = {}
        if self.rescan_versions:
            index = build_fresh_index()
        for i, app in enumerate(self.apps, 1):
            if self._cancel.is_set():
                break
            target = app
            if self.rescan_versions:
                try:
                    fresh = match_fresh_version(app, index)
                except Exception:
                    fresh = ""
                if fresh:
                    try:
                        target = dataclasses.replace(app, version=fresh)
                    except Exception:
                        target = app
                    self.app_version_refreshed.emit(
                        f"{app.name}|{app.version}", fresh)
            try:
                res = checker.check_app(target)
            except Exception as exc:  # never let a single app kill the run
                res = CheckResult(app_name=app.name,
                                  installed_version=target.version)
                res.status = "failed"
                res.set_note("note.unexpected_error", cls=exc.__class__.__name__)
            if res.status == "update":
                updates += 1
            elif res.status == "failed":
                failed += 1
            self.app_checked.emit(res)
            self.progress.emit(i, total)
        self.finished_all.emit(updates, failed, total)


class VersionWatchWorker(QThread):
    """ONE local registry re-scan (NO network) for the post-install watcher.

    After the user downloads an update and installs it, the main window
    polls the registry every few seconds (this worker) so the updated app's
    row can flip to the honest 'Up to date' BY ITSELF - no manual
    'Re-check this app' click needed anymore.

    Change detection reuses match_fresh_version (registry-key identity
    first, strictly disambiguated name fallback), the exact same machinery
    a manual re-check uses - so same-name-but-different-product entries
    (VC++ 2005 vs 2015-2022) can never cross-contaminate and the watcher
    can never "detect" an install that did not happen. Every changed app
    is reported once as a (name, old_version, fresh_version) tuple.
    """

    fresh_versions = Signal(object)  # list[(name, old_version, fresh_version)]

    def __init__(self, apps: list, parent=None):
        super().__init__(parent)
        self.apps = list(apps)
        self._cancel = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()

    def run(self) -> None:  # runs in worker thread
        changed: list = []
        index = None
        try:
            index = build_fresh_index()
        except Exception:
            index = None  # scan failed - report "no change" this round
        for app in self.apps:
            if self._cancel.is_set():
                break
            fresh = ""
            if index is not None:
                try:
                    fresh = match_fresh_version(app, index) or ""
                except Exception:
                    fresh = ""
            if fresh:
                changed.append((app.name, app.version or "", fresh))
        # ALWAYS emitted (even empty / cancelled) as the LAST statement, so
        # the receiving slot can retire this thread exactly once.
        self.fresh_versions.emit(changed)


class IconWorker(QThread):
    """Extracts every app's icon (shell icon of its DisplayIcon exe/ico)
    OFF the UI thread - UniGetUI's IconStore idea: per-app disk cache keyed
    by the icon source identity, extraction in the background, PNG bytes
    delivered per app via queued signals. The main thread never blocks, and
    a second launch is instant because the cache is hit first.

    online_icons: when True, apps whose icon cannot be found ANYWHERE local
    (registry DisplayIcon, Start-Menu shortcut, install folder, Program
    Files) additionally try the UniGetUI community icon database as a last
    resort (downloaded once, cached on disk for days, each image validated
    before use). Direct callers (tests, details dialog) stay offline by
    default so nothing ever waits on the network implicitly.
    """

    icon_ready = Signal(str, str, object)   # name, key, png bytes
    finished_all = Signal(int)              # icons delivered

    def __init__(self, apps: list, parent=None, online_icons: bool = False):
        super().__init__(parent)
        self.apps = apps
        self._online = bool(online_icons)
        self._cancel = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()

    def run(self) -> None:  # runs in worker thread
        from . import app_icons

        if self._online:
            # a fresh worker run gets one fresh shot at the icon database
            app_icons.reset_online_state()
        delivered = 0
        for app in self.apps:
            if self._cancel.is_set():
                break
            try:
                png = app_icons.icon_png_for_app(
                    app, allow_online=self._online)
            except Exception:
                png = app_icons.letter_tile_png(app.name) \
                    if not self._cancel.is_set() else b""
            if not png:
                continue
            delivered += 1
            self.icon_ready.emit(app.name,
                                 f"{app.name}|{app.version}", png)
        self.finished_all.emit(delivered)


class DownloadWorker(QThread):
    """Downloads installers sequentially with pause/resume support."""

    item_progress = Signal(str, int, int, int, float)  # name, pct(-1=indeterminate), done, total, speed
    item_state = Signal(str, str)                      # name, "downloading" | "paused"
    item_done = Signal(str, bool, str, str)            # name, success, path/error, sha state
    finished_all = Signal(int, int)                    # succeeded, failed

    def __init__(self, jobs: list, parent=None):
        super().__init__(parent)
        # jobs: list of (app_name, installer_url) or
        #       (app_name, installer_url, expected_sha256) or
        #       (app_name, installer_url, expected_sha256, expected_size) or
        #       (app_name, installer_url, expected_sha256, expected_size,
        #        alt_urls) - alt_urls are OFFICIAL fallback locations.
        self.jobs = jobs
        self._cancel = threading.Event()
        self._pause = threading.Event()
        self._resume_ev = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()
        self._resume_ev.set()  # wake a paused transfer so it can exit

    def pause(self) -> None:
        self._pause.set()

    def resume(self) -> None:
        self._pause.clear()
        self._resume_ev.set()

    def run(self) -> None:  # runs in worker thread
        ok = fail = 0
        for job in self.jobs:
            if self._cancel.is_set():
                break
            name = job[0]
            url = job[1]
            sha = job[2] if len(job) > 2 else ""
            size = int(job[3]) if len(job) > 3 and job[3] else 0
            alts = tuple(job[4]) if len(job) > 4 and job[4] else ()
            o, f = self._run_one(name, url, sha, size, alts)
            ok += o
            fail += f
        self.finished_all.emit(ok, fail)

    def _run_one(self, name: str, url: str, sha: str = "",
                 expected_size: int = 0,
                 alt_urls: tuple = ()) -> tuple[int, int]:
        """Download one file, honouring pause/resume. Returns (ok, fail) counts
        (0, 0 when the job was cancelled)."""
        done = 0
        self.item_state.emit(name, "downloading")
        while True:
            if self._cancel.is_set():
                return (0, 0)
            try:
                path = download(
                    url,
                    name,
                    progress_cb=lambda d, t, s, _n=name: self.item_progress.emit(
                        _n, int(d * 100 / t) if t else -1, d, t, s),
                    cancel_flag=self._cancel,
                    pause_flag=self._pause,
                    resume_from=done,
                    sha256=sha,
                    expected_size=expected_size,
                    alt_urls=alt_urls,
                )
                self.item_done.emit(
                    name, True, path, "verified" if sha else "unchecked")
                return (1, 0)
            except DownloadPaused as p:
                done = p.done_bytes
                self.item_state.emit(name, "paused")
                self._resume_ev.wait()
                self._resume_ev.clear()
            except RuntimeError as exc:
                msg = str(exc) or exc.__class__.__name__
                self.item_done.emit(name, False, msg, "failed")
                return (0, 1)
            except Exception as exc:
                # requests.ConnectionError/Timeout and friends are OSError
                # subclasses - without this they would kill the thread
                # silently and the UI would wait forever for a done signal.
                from ..core import applog

                applog.error(
                    f"Download worker error for {name}: "
                    f"{exc.__class__.__name__}: {exc}")
                self.item_done.emit(name, False,
                                    f"{exc.__class__.__name__}", "failed")
                return (0, 1)
