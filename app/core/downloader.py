"""Downloads installers to the user's Downloads folder. Never executes them.

Supports pause/resume: pausing keeps the .part file and the transfer is
later continued with an HTTP Range request (servers that ignore Range are
restarted from scratch automatically).

Downloads whose official source publishes a SHA-256 checksum (winget
manifests, GitHub release assets, VideoLAN) are VERIFIED before the file
becomes visible in the download folder - a mismatched file is deleted,
never kept.

EVERY finished download is validated BEFORE being renamed into place:
  1. completeness - the byte count must match the server's Content-Length
     (a connection cut mid-stream by a congested/middleboxed route used to
     silently produce a truncated installer that Windows refuses to run);
  2. official SHA-256 when published;
  3. file-signature (magic bytes) + Windows PE header for .exe - a server,
     CDN or censoring box that answers HTTP 200 with an HTML error/block
     page can no longer reach the user as "app-setup.exe".
Each transient failure (connection drop, truncation, timeout) is retried
automatically - the first attempt resumes the .part file via Range, the
last starts from scratch. Bad files are deleted and a clear error is
raised instead.
"""

from __future__ import annotations
from __future__ import annotations

import hashlib
import os
import re
import time
from urllib.parse import unquote, urlparse

from ..i18n import tr
from .win_info import is_windows


class DownloadPaused(Exception):
    """Raised when the pause flag stops an in-flight download.

    The .part file is kept on disk; ``done_bytes`` says how much of the
    file has already been saved so the download can be resumed.
    """

    def __init__(self, done_bytes: int):
        super().__init__("paused")
        self.done_bytes = int(done_bytes)


class _Incomplete(Exception):
    """Internal: the stream ended but the announced byte count is short
    (connection cut mid-transfer). Treated as a transient failure."""


class _BadContent(RuntimeError):
    """Internal: the server answered 200 with something that can never be
    the installer (an HTML/plain-text error or censoring page). NOT retried
    on the same URL - but the caller immediately tries the next official
    mirror instead."""


def format_size(num: float) -> str:
    """Human-readable size: 78412377 -> '74.8 MB', 20480 -> '20 KB'."""
    try:
        n = float(num)
    except (TypeError, ValueError):
        return "0 B"
    if n < 0:
        n = 0.0
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024.0 or unit == "GB":
            if unit == "B":
                return f"{int(n)} B"
            text = f"{n:.1f}"
            if text.endswith(".0"):
                text = text[:-2]
            return f"{text} {unit}"
        n /= 1024.0
    return f"{n:.1f} GB"


def format_speed(bytes_per_second: float) -> str:
    """Human-readable speed: 2516582.4 -> '2.4 MB/s'. <= 0 -> ''."""
    if not bytes_per_second or bytes_per_second <= 0:
        return ""
    return format_size(bytes_per_second) + "/s"


# User-chosen download folder (Settings). None = default (%USERPROFILE%
# Downloads\SoftUpdater). A module variable (not QSettings) so worker threads
# can read it safely without touching Qt from a background thread.
_custom_dir: str | None = None


def set_custom_download_dir(path: str | None) -> None:
    """Use a user-chosen folder for downloads. Empty/None resets to default."""
    global _custom_dir
    _custom_dir = (path or "").strip() or None


def download_dir() -> str:
    if _custom_dir and os.path.isdir(_custom_dir):
        return _custom_dir
    if is_windows():
        base = os.path.join(os.path.expanduser("~"), "Downloads")
    else:
        base = os.path.join("/tmp", "SoftUpdater")
    target = os.path.join(base, "SoftUpdater")
    os.makedirs(target, exist_ok=True)
    return target


def _safe_filename(name: str) -> str:
    name = unquote(name or "installer")
    name = os.path.basename(name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(". ")
    return name[:120] or "installer"


def filename_for_url(url: str, app_name: str = "") -> str:
    """Derive a clean filename from the installer URL."""
    path = urlparse(url).path
    base = _safe_filename(path.split("/")[-1])
    if not base or base.lower() in ("download", "latest", "installer"):
        from .version_utils import normalize_name

        base = _safe_filename(normalize_name(app_name).replace(" ", "_") or "installer") + ".exe"
    return base


def unique_path(directory: str, filename: str) -> str:
    candidate = os.path.join(directory, filename)
    if not os.path.exists(candidate):
        return candidate
    stem, ext = os.path.splitext(filename)
    for i in range(1, 1000):
        candidate = os.path.join(directory, f"{stem} ({i}){ext}")
        if not os.path.exists(candidate):
            return candidate
    return candidate


_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
       "AppleWebKit/537.36 (KHTML, like Gecko) "
       "Chrome/126.0.0.0 Safari/537.36 "
       "SoftDownloader/2.0")


def file_sha256(path: str) -> str:
    """Lowercase hex SHA-256 of a file, streamed (never loads it whole)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha_matches(path: str, expected: str) -> bool:
    expected = (expected or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        return False  # malformed hash: caller should not have asked
    try:
        return file_sha256(path) == expected
    except Exception:
        return False


# File signatures (magic bytes) that identify a REAL installer. Anything
# else (HTML error/block pages, JSON, plain text) arrives when a mirror,
# CDN or network middlebox answers with HTTP 200 + an error page.
_MSI_MAGIC = bytes.fromhex("d0cf11e0a1b11ae1")   # OLE compound (MSI)
_ZIP_MAGIC = b"PK\x03\x04"                        # zip container (msix/appx/zip)

# A real installer is never tiny. Floors stop truncated/garbage files that
# happen to begin with the right magic bytes from being renamed into place.
_MIN_INSTALLER_BYTES = {"exe": 64 * 1024, "msi": 64 * 1024,
                        "zip": 8 * 1024, "msix": 8 * 1024, "appx": 8 * 1024}


def _pe_header_present(path: str) -> bool:
    """True when the file carries the Windows PE header ('PE\\0\\0' at the
    MZ-stub's e_lfanew offset) - every real .exe/.dll does. When the offset
    points beyond our 64 KB read window we accept (do not guess) - the size
    floor and SHA-256 cover the rest."""
    try:
        with open(path, "rb") as f:
            head = f.read(65536)
    except OSError:
        return False
    if len(head) < 0x40:
        return False
    try:
        lfa = int.from_bytes(head[0x3C:0x40], "little")
    except Exception:
        return False
    if lfa <= 0 or lfa + 4 > len(head):
        return True
    return head[lfa:lfa + 4] == b"PE\x00\x00"


def installer_signature_error(path: str, ext: str = "") -> str:
    """Why the file at `path` is NOT a valid installer of type `ext`, or ""
    when it looks right (or the type is one we cannot verify).

    `ext` is the FINAL file's extension (with dot), needed because callers
    validate a "<name>.part" temp file whose own extension is meaningless.
    Checks the real file header, so an HTML/text error page saved as
    "vlc-...-win64.exe" is rejected before it can reach the user.
    """
    try:
        ext = (ext or os.path.splitext(path)[1]).lower().lstrip(".")
        with open(path, "rb") as f:
            head = f.read(8)
        if len(head) < 4:
            return "the downloaded file is empty or truncated"
        if ext == "exe":
            if head[:2] != b"MZ":
                return ("it does not start with a Windows executable (MZ) "
                        "signature")
            if not _pe_header_present(path):
                return "it is not a valid Windows executable (no PE header)"
        elif ext == "msi":
            if head[:8] != _MSI_MAGIC:
                return "it is not a valid MSI package"
        elif ext in ("zip", "msix", "appx"):
            if head[:4] != _ZIP_MAGIC:
                return "it is not a valid zip package"
        else:
            return ""  # unknown type: nothing we can judge
        floor = _MIN_INSTALLER_BYTES.get(ext, 0)
        if floor:
            try:
                actual = os.path.getsize(path)
            except OSError:
                return "the file could not be measured"
            if actual < floor:
                return (f"the file is implausibly small "
                        f"({actual} bytes) for an installer")
        return ""
    except OSError as exc:
        return f"the file could not be read ({exc.__class__.__name__})"


def _transfer(url: str, dest: str, app_name: str, sha256: str,
              expected_size: int,
              progress_cb=None, cancel_flag=None, pause_flag=None) -> None:
    """One FULL download attempt chain for ONE URL into dest+'.part'.

    Runs up to 3 attempts; the retry RESUMES the .part file via HTTP Range
    (a stale .part -> HTTP 416 -> clean restart, a server that ignores
    Range -> clean restart). Validates completeness + checksum + installer
    signature before renaming into place. Raises on any failure; raises
    DownloadPaused (keeping the .part) when the pause flag is set.
    """
    import random

    import requests
    from requests.exceptions import RequestException

    tmp = dest + ".part"
    attempts = 3
    speed = 0.0
    start = time.monotonic()
    last_t = start
    last_done = 0
    cancelled = False
    completed = False
    last_error = "the connection kept failing"

    for attempt in range(attempts):
        # resume from whatever is already in the .part file (0 on the very
        # first attempt, after a pause, or after a mid-stream disconnect)
        try:
            done = os.path.getsize(tmp) if os.path.exists(tmp) else 0
        except OSError:
            done = 0
        if done < 0:
            done = 0
        headers = {"User-Agent": _UA,
                   # never let a middlebox negotiate compression: the byte
                   # counts must be the file's real ones for completeness
                   # verification to mean anything.
                   "Accept-Encoding": "identity"}
        mode = "wb"
        if done > 0:
            headers["Range"] = f"bytes={done}-"
            mode = "ab"  # append to the kept .part file

        last_done = done
        total = 0
        try:
            with requests.get(url, headers=headers, stream=True,
                              timeout=(15, 60), allow_redirects=True) as r:
                # Fast-fail on block/error pages: an HTML or plain-text
                # body can never be the installer, so do not stream 45 MB
                # of garbage - fail THIS URL immediately (the caller then
                # tries the next official mirror). Rare legit servers send
                # installers with text/* content types; every major one
                # (VideoLAN, GitHub, Microsoft, winget targets) does not.
                ctype = (r.headers.get("Content-Type") or "").split(";")[0]\
                    .strip().lower()
                if (ctype in ("text/html", "application/xhtml+xml",
                              "text/plain")
                        and os.path.splitext(dest)[1].lower()
                        in (".exe", ".msi")):
                    raise _BadContent(
                        "the server answered with an HTML page instead of "
                        "the installer (blocked or error page)")
                if done > 0 and r.status_code == 416:
                    # our resume point is beyond the file's end - the .part
                    # is stale; discard it and restart cleanly
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass
                    last_error = "the resume data was no longer valid"
                    continue
                if r.status_code >= 400:
                    raise RuntimeError(tr("dlerr.http", code=r.status_code))
                if done > 0 and r.status_code != 206:
                    # server ignored the Range header - restart cleanly
                    done = 0
                    mode = "wb"
                total = int(r.headers.get("Content-Length") or 0)
                if done > 0 and total:
                    total += done
                with open(tmp, mode) as f:
                    # 16 KB: snappy Cancel/Pause response even on very slow
                    # streams (a 64 KB buffer can hold several seconds of a
                    # throttled transfer before the flag is ever seen)
                    for chunk in r.iter_content(chunk_size=16384):
                        if cancel_flag is not None and cancel_flag.is_set():
                            cancelled = True
                            raise RuntimeError(tr("dlerr.cancelled"))
                        if pause_flag is not None and pause_flag.is_set():
                            raise DownloadPaused(done)
                        if not chunk:
                            continue
                        f.write(chunk)
                        done += len(chunk)
                        now = time.monotonic()
                        if now - last_t >= 0.4:
                            inst = (done - last_done) / max(now - last_t, 0.001)
                            speed = inst if speed <= 0 else (speed * 0.6 + inst * 0.4)
                            last_t = now
                            last_done = done
                        if progress_cb:
                            progress_cb(done, total, speed)
            # The stream ended CLEANLY - now prove it is COMPLETE before
            # trusting it: (1) the announced byte count, or (2) when the
            # server sent no length, the size the source announced at check
            # time (2% tolerance - that one is a rounded human value).
            if total and done != total:
                raise _Incomplete(
                    f"connection closed early ({done} of {total} bytes)")
            # expected_size is a ROUNDED value parsed at check time and a
            # block page can also be tiny - only trust it as a net when it
            # is at least a plausible installer size.
            if (not total and expected_size >= 512 * 1024 and done
                    and abs(done - expected_size) / expected_size > 0.02):
                raise _Incomplete(
                    f"received {done} bytes but the source announced "
                    f"about {expected_size}")
            completed = True
            break  # complete - leave the retry loop for validation
        except DownloadPaused:
            raise  # keep the .part file for the resume
        except _BadContent:
            raise  # never retry the same URL for a block page
        except RuntimeError:
            if cancelled:
                try:
                    os.remove(tmp)
                except OSError:
                    pass
            raise
        except (_Incomplete, RequestException, OSError) as exc:
            last_error = str(exc) or exc.__class__.__name__
            if attempt >= attempts - 1:
                break
            time.sleep(min(1.5 * (attempt + 1), 4.0) +
                       random.uniform(0.0, 0.4))
            # loop: the next attempt resumes the .part file via Range

    # every attempt failed with a transient error -> give up honestly
    if not completed:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise RuntimeError(tr("dlerr.give_up", err=last_error))

    _validate_and_commit(url, tmp, dest, app_name, sha256)


def _validate_and_commit(url: str, tmp: str, dest: str, app_name: str,
                         sha256: str) -> None:
    """Checksum + signature validation, then rename tmp into dest.

    Shared by every URL of the fallback chain: a file that fails here is
    DELETED (a bad installer must never reach the user's folder) and a
    clear RuntimeError is raised so the caller can try the next official
    mirror.
    """
    from . import applog

    # Content validation BEFORE the file becomes visible/usable:
    # 1) official checksum when the source publishes one (strongest check)
    if sha256 and not _sha_matches(tmp, sha256):
        try:
            os.remove(tmp)
        except OSError:
            pass

        applog.error(
            f"SHA-256 MISMATCH for {app_name}: expected {sha256}, "
            f"got a different hash - file deleted (source URL: {url})")
        raise RuntimeError(tr("dlerr.sha_mismatch"))
    # 2) installer file-signature for EVERY download (catches HTML error or
    #    block pages served with HTTP 200 - the "Unsupported 16-bit
    #    application" Windows bug the user hit with VLC). NOTE: the check
    #    must use the FINAL file's extension - the temp file ends .part.
    sig_error = installer_signature_error(tmp, os.path.splitext(dest)[1])
    if sig_error:
        try:
            with open(tmp, "rb") as f:
                head_hex = f.read(16).hex()
        except OSError:
            head_hex = "?"
        try:
            os.remove(tmp)
        except OSError:
            pass

        applog.error(
            f"INVALID INSTALLER for {app_name}: {sig_error} - file deleted "
            f"(first bytes: {head_hex}; source URL: {url})")
        raise RuntimeError(tr("dlerr.not_installer"))
    os.replace(tmp, dest)
    # 3) paranoia: re-validate the RENAMED file (cheap - reads 64 KB) so a
    #    rename/write race can never leave a broken installer behind.
    final_error = installer_signature_error(dest)
    if final_error:
        try:
            os.remove(dest)
        except OSError:
            pass

        applog.error(
            f"INVALID INSTALLER after rename for {app_name}: {final_error} "
            f"(source URL: {url})")
        raise RuntimeError(tr("dlerr.final_validation"))
    if sha256:
        applog.event(f"SHA-256 verified OK: {os.path.basename(dest)}")


def download(url: str, app_name: str, progress_cb=None, cancel_flag=None,
             pause_flag=None, resume_from: int = 0,
             sha256: str = "", expected_size: int = 0,
             alt_urls: tuple = ()) -> str:
    """Stream the file to disk. Returns the final path.

    progress_cb(done_bytes, total_bytes, speed_bps) is called periodically
    (total_bytes is 0 when the server does not announce a length).
    cancel_flag / pause_flag: objects with .is_set() to abort or pause.
    Pausing raises DownloadPaused and KEEPS the .part file; call again with
    resume_from=<bytes already on disk> to continue via HTTP Range (a server
    that ignores Range simply restarts the file).
    sha256: when the official source publishes the installer's checksum the
    finished file is verified BEFORE being renamed into place; on mismatch
    the file is deleted and RuntimeError is raised.
    expected_size: size announced by the source at check time - used ONLY
    as a sanity net when the server sends no Content-Length (a middlebox
    stripped it) and never with a hard equality (sizes parsed from HTML are
    rounded), so honest downloads can never fail because of it.
    alt_urls: OFFICIAL alternate download locations for the same file (e.g.
    the vendor's canonical server next to the geo mirror). They are tried
    IN ORDER whenever the previous location fails - a broken or blocked
    mirror can no longer make the whole download fail when another official
    server still works (the "downloaded but the installer never opens"
    class of bug).
    Transient failures (connection reset, truncation, timeout) are retried
    up to 2 more times per URL: the retry RESUMES the .part file via HTTP
    Range and falls back to a fresh start when the server will not
    cooperate. Raises RuntimeError on failure or cancellation.
    """
    if not url:
        raise RuntimeError(tr("dlerr.no_url"))
    if cancel_flag is not None and cancel_flag.is_set():
        raise RuntimeError(tr("dlerr.cancelled"))
    dest = unique_path(download_dir(), filename_for_url(url, app_name))
    tmp = dest + ".part"

    urls = [url]
    for u in (alt_urls or ()):
        u = (u or "").strip()
        if u and u != url and u not in urls:
            urls.append(u)

    from . import applog

    failures: list[str] = []
    for i, u in enumerate(urls):
        if i:
            # a different official host: the old .part (if any) belongs to
            # the previous transfer - discard it so resume offsets from a
            # different server can never corrupt this one.
            try:
                os.remove(tmp)
            except OSError:
                pass
            applog.event(
                f"Download retry on alternate official server "
                f"({i + 1}/{len(urls)}) for {app_name}: {u}")
        try:
            _transfer(u, dest, app_name, sha256, expected_size,
                      progress_cb=progress_cb, cancel_flag=cancel_flag,
                      pause_flag=pause_flag)
            return dest
        except DownloadPaused:
            raise  # user paused: keep the .part, do NOT switch servers
        except _BadContent as exc:
            failures.append(str(exc))
            continue
        except RuntimeError as exc:
            if cancel_flag is not None and cancel_flag.is_set():
                raise  # user pressed Cancel - surface it immediately
            failures.append(str(exc) or exc.__class__.__name__)
            continue

    detail = failures[-1] if failures else "the connection kept failing"
    if len(urls) > 1:
        raise RuntimeError(tr("dlerr.all_locations", n=len(urls), err=detail))
    raise RuntimeError(tr("dlerr.failed_one", err=detail))
