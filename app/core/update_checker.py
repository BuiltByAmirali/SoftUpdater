"""Official-source update checker.

For each installed app this module resolves the app to an official source
(curated catalog, or GitHub auto-search fallback), fetches the latest version
and picks the correct installer for the OS architecture.

Statuses returned:
  update        - newer version found
  latest        - already up to date
  no_installer  - version found but no installer for this OS architecture
  vendor        - known vendor-managed app (self-updating or driver);
                  honest explanation instead of a fake "unavailable"
  no_source     - no official source could be resolved (honest, with reason)
  failed        - network/server error while checking
"""

from __future__ import annotations
from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass, field
from functools import cmp_to_key
from typing import Any, Callable
from urllib.parse import quote, unquote

from ..i18n import tr
from . import catalog
from . import winget_bridge
from .installed_apps import InstalledApp
from .version_utils import compare_versions, normalize_name, prefix_equal
from .win_info import os_bitness

USER_AGENT = "SoftUpdater/2.0 (Windows update checker; +official sources)"

# microsoft/winget-pkgs - the SAME official manifest repository the
# `winget upgrade` command resolves VC++ Redistributables, WebView2 and
# .NET runtimes from. InstallerUrls inside the manifests point at
# Microsoft's own download servers.
WINGET_API = "https://api.github.com/repos/microsoft/winget-pkgs/contents/"
WINGET_RAW = "https://raw.githubusercontent.com/microsoft/winget-pkgs/master/"

# --- anti "Check failed" constants -----------------------------------------
# api.github.com allows only ~60 unauthenticated requests per hour per IP
# (less on shared CGNAT addresses). UniGetUI never relies on it in the hot
# path - its winget backend talks to Microsoft's own catalog service. We do
# the same: the primary release-discovery route is github.com itself (the
# /releases/latest redirect + releases.atom + expanded_assets fragments -
# all unauthenticated, no meaningful quota), and api.github.com is only the
# last-resort fallback.
GITHUB_WEB = "https://github.com"
_LOCATION_TAG_RE = re.compile(r"/releases/tag/([^/?#\s]+)")
# Release tags that are NOT stable builds (rc/beta/test/nightly...): the
# atom feed lists them by date, so 'latest' must skip them.
_PRERELEASE_RE = re.compile(
    r"(?i)(?:^|[^a-z])"
    r"(rc|alpha|beta|pre|preview|dev|nightly|canary|insider|test|unstable|snapshot)"
    r"(?:[^a-z]|$|\d)")
# Transient HTTP statuses that deserve a retry (CDN blips, throttling).
_RETRY_STATUS = (429, 500, 502, 503, 504)
# Delays between the retry attempts (1st->2nd, 2nd->3rd) + jitter. Kept
# module-level so tests can shorten them.
_RETRY_DELIMS = (1.2, 2.8)
_CONNECT_TIMEOUT = 10
_READ_TIMEOUT = 30

X64_KEYS = ("x64", "win64", "64-bit", "64bit", "amd64", "x86_64", "_64")
X86_KEYS_RE = re.compile(r"(?i)(win32|\bi386\b|\bi686\b|\bx86\b|32-bit|32bit|\b_86\b)")
DEFAULT_EXCLUDE = (
    "macos", "darwin", "linux", "appx", "msix", "symbols", "debug",
    "source", "sha256", "checksums", "blockmap", ".sig", ".asc",
    ".md5", ".sha1", ".sha256",
)
# ARM builds: exclude plain "arm" and ARM64-only assets, but KEEP combined
# installers that also contain x64/x86 (e.g. ViGEmBus_1.22.0_x64_x86_arm64.exe).
_ARM_RE = re.compile(r"(?i)(?<![a-z0-9])arm(?!64)")
EXTS = (".exe", ".msi", ".zip")

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore[assignment]


@dataclass
class CheckResult:
    app_name: str
    installed_version: str = ""
    latest_version: str = ""
    status: str = "no_source"          # update|latest|no_installer|vendor|no_source|failed
    installer_url: str = ""            # chosen for THIS machine's architecture
    source_label: str = ""             # e.g. "GitHub - owner/repo"
    source_url: str = ""               # human-checkable page
    note: str = ""                     # PLAIN note text (legacy/tests/logs).
                                       # Prefer set_note()/add_note(): notes
                                       # stored canonically re-translate
                                       # themselves in EVERY language the
                                       # moment they are displayed.
    note_parts: list = field(default_factory=list)  # canonical [(key, args)]
    arch: str = "x64"                  # installer architecture actually chosen
    size_bytes: int = 0                # exact download size of the new installer (0 = unknown)
    sha256: str = ""                   # official checksum when the source publishes one
    alt_urls: tuple = ()               # OFFICIAL alternate download locations
                                       # (same file, different vendor host) -
                                       # the downloader tries them in order when
                                       # the primary mirror is broken/blocked

    def set_note(self, key: str, **args) -> None:
        """Store the note as a translation KEY (+ format args) so it is
        rendered in the CURRENT language every time it is displayed -
        switching the UI language re-translates every row's note live."""
        self.note_parts = [(key, dict(args))]

    def add_note(self, key: str, **args) -> None:
        """Append one canonical note segment (e.g. the 'last known state
        kept' tail after a failed re-check). A legacy plain note is kept."""
        if self.note and not self.note_parts:
            self.note_parts.append(("", self.note))
        self.note_parts.append((key, dict(args)))

    def clear_note(self) -> None:
        self.note_parts = []
        self.note = ""

    def note_key(self) -> str:
        """First canonical key, or '' for plain/legacy notes."""
        return self.note_parts[0][0] if self.note_parts else ""

    def note_text(self) -> str:
        """The note IN THE CURRENT LANGUAGE (live re-translation)."""
        if not self.note_parts:
            return self.note
        texts = []
        for key, args in self.note_parts:
            try:
                # key == "" means a legacy literal kept in the key slot
                texts.append(key if not key else tr(key, **args))
            except Exception:
                texts.append(key)
        return " - ".join(t for t in texts if t)

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["note"] = self.note_text()  # human-readable for any JSON consumer
        return d


# Notes that mean "no installer exists for this architecture" - when the
# installed version turns out to EQUAL the latest one, that complaint is
# replaced by the honest 'Already on the latest version'.
_NO_INSTALLER_NOTE_KEYS = frozenset((
    "note.no_installer_url", "note.winget_installer_missing",
    "note.winget_no_arch", "note.github_no_arch", "note.vendor_no_arch",
    "note.vendor_arch_installer_missing", "note.vlc_no_installer",
    "note.blender_64bit_only", "note.no_windows_installer_folder",
))


def _extract_version(text: str) -> str:
    m = re.search(r"\d+(?:\.\d+)+", text or "")
    return m.group(0) if m else ""


def _tag_sort_key(tag: str):
    """Comparator key so max()/sorted() use the REAL version comparator
    ('1.10' beats '1.9', numeric segments, prefix tolerance)."""
    return cmp_to_key(compare_versions)(tag)


def _latest_stable_tag_from_atom(text: str) -> str:
    """Newest STABLE release tag from a releases.atom feed (pure function).

    Atom lists the newest releases BY DATE and includes rc/beta/test tags,
    so unstable tags are filtered out first and the rest ranked by the real
    version comparator - never by feed order. Falls back to all tags when
    ONLY pre-releases exist (still better than no answer).
    """
    tags = [unquote(t) for t in
            re.findall(r"/releases/tag/([^\"<\s]+)", text or "")]
    if not tags:
        return ""
    stable = [t for t in tags if not _PRERELEASE_RE.search(t)]
    pool = stable or tags
    return max(pool, key=_tag_sort_key)


def _assets_from_expanded_html(html: str, repo: str) -> list[dict]:
    """Parse the expanded_assets HTML fragment into API-shaped assets
    (pure function, unit-tested against the real page structure).

    Each asset contributes one '/OWNER/REPO/releases/download/<tag>/<name>'
    link followed (later in the same block) by its sha256 digest and
    human-readable size. Source-code zipball/tarball links live under
    /archive/ and never match, so no extra filtering is needed. Sizes are
    the values GitHub itself displays (e.g. '152 MB') -> approximate bytes;
    the display formats identically to the API's exact sizes.
    """
    assets: list[dict] = []
    prefix = f"/{repo}/releases/download/"
    # GitHub renders the fragment with the repo path in ITS canonical
    # casing, which can differ from the catalog's spelling (e.g.
    # 'Notepad-plus-plus' vs 'notepad-plus-plus') - split case-insensitively.
    chunks = re.split(re.escape(prefix), html or "", flags=re.IGNORECASE)[1:]
    for chunk in chunks:
        m = re.match(r"([^\"'?#]+)", chunk)
        if not m or "/" not in m.group(1):
            continue
        name = m.group(1).rsplit("/", 1)[-1]
        if not name:
            continue
        sm = re.search(r"sha256:([0-9a-fA-F]{64})", chunk)
        zm = re.search(r"([0-9]+(?:\.[0-9]+)?)\s?(B|KB|MB|GB)\s*<", chunk)
        size = 0
        if zm:
            mult = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3}[zm.group(2)]
            try:
                size = int(float(zm.group(1)) * mult)
            except ValueError:
                size = 0
        assets.append({
            "name": name,
            "browser_download_url": f"{GITHUB_WEB}{prefix}{m.group(1)}",
            "size": size,
            "digest": (f"sha256:{sm.group(1)}" if sm else ""),
        })
    return assets


def _dig(obj: Any, path: str) -> Any:
    """Resolve a dotted path with numeric indexes, e.g. 'versions.0.version'."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
                continue
            except (ValueError, IndexError):
                return None
        if isinstance(cur, dict):
            if part in cur:
                cur = cur[part]
                continue
            # tolerate case differences
            for k in cur:
                if k.lower() == part.lower():
                    cur = cur[k]
                    break
            else:
                return None
        else:
            return None
    return cur


def _classify_asset(name: str) -> str:
    low = name.lower()
    if any(k in low for k in X64_KEYS):
        return "x64"
    if X86_KEYS_RE.search(low):
        return "x86"
    return "neutral"


def _version_token(v: str, parts: int) -> str:
    nums = re.findall(r"\d+", v)
    return ".".join(nums[:parts]) if len(nums) >= parts else v


class UpdateChecker:
    """Checks apps against official sources. Reusable; caches HTTP etags."""

    def __init__(self, cache_dir: str | None = None, allow_github_search: bool = True):
        self.bitness = os_bitness()
        self.allow_github_search = allow_github_search
        self._searches_done = 0
        self._search_blocked = False          # set when search API is rate-limited
        self._github_blocked = False          # set when core API limit hit
        self._memory_cache: dict[str, Any] = {}
        self._winget_cache: dict[str, tuple] = {}   # per-run manifest memo
        self.cache_dir = cache_dir or self._default_cache_dir()
        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache_file = os.path.join(self.cache_dir, "http_cache.json")
        self._disk_cache = self._load_cache()
        self.session = self._make_session()

    # -- session / cache ---------------------------------------------------
    @staticmethod
    def _default_cache_dir() -> str:
        if os.name == "nt":
            base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
            return os.path.join(base, "SoftUpdater", "cache")
        return os.path.join("/tmp", "SoftUpdater_cache")

    @staticmethod
    def _make_session():
        import requests  # local import; module may be absent in selftest

        s = requests.Session()
        # Browser-like UA: some vendor pages (keepass.info, voidtools) block
        # non-browser user agents with HTTP 403.
        s.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/126.0.0.0 Safari/537.36 SoftUpdater/2.0"),
            "Accept": "application/json, text/html, */*",
        })
        return s

    def _load_cache(self) -> dict:
        try:
            with open(self._cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self) -> None:
        try:
            tmp = self._cache_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._disk_cache, f)
            os.replace(tmp, self._cache_file)
        except Exception:
            pass

    def _get(self, url: str, timeout: int = 12, want_json: bool = False,
             etag_cache: bool = False):
        """GET with optional etag caching. Returns (data, status_code) or
        (None, code). Transport resilience (retries, backoff, Retry-After,
        rate-limit flags) lives in _http."""
        return self._http(url, timeout=timeout, want_json=want_json,
                          etag_key=url if etag_cache else "")

    def _http(self, url: str, timeout=None, headers: dict | None = None,
              want_json: bool = False, allow_redirects: bool = True,
              etag_key: str = ""):
        """Resilient GET on the shared session - the anti-"check failed"
        layer (UniGetUI-grade transport hygiene for every request):

        * up to 3 attempts with escalating backoff + jitter for connection
          resets / timeouts / 429 / 5xx - routine on congested international
          routes, previously enough to fail a whole check run;
        * Retry-After honoured (capped at 10 s);
        * (connect, read) timeouts instead of one scalar;
        * optional etag cache: a 304 Not Modified is served from disk and
          GitHub does not charge its rate limit for conditional 304s;
        * GitHub rate-limit detection (flags gate only the API fallback,
          never the authless github.com routes).

        Returns (data, status_code); data is parsed JSON when want_json else
        response text. (None, code) on failure; (None, 0) when every attempt
        died on the network layer.
        """
        if timeout is None:
            timeout = (_CONNECT_TIMEOUT, _READ_TIMEOUT)
        headers = dict(headers or {})
        if etag_key and etag_key in self._disk_cache and \
                "etag" in self._disk_cache[etag_key]:
            headers["If-None-Match"] = self._disk_cache[etag_key]["etag"]
        last_code = 0
        for attempt in range(3):
            try:
                resp = self.session.get(url, timeout=timeout, headers=headers,
                                        allow_redirects=allow_redirects)
            except Exception:
                if attempt >= 2:
                    return None, 0
                time.sleep(_RETRY_DELIMS[min(attempt, 1)] +
                           random.uniform(0.0, 0.4))
                continue
            code = resp.status_code
            if code == 304 and etag_key and etag_key in self._disk_cache:
                data = self._disk_cache[etag_key].get("data")
                if want_json:
                    return data, 200
                return self._disk_cache[etag_key].get("text", ""), 200
            if code == 200:
                if etag_key:
                    entry = {"etag": resp.headers.get("ETag", ""),
                             "ts": time.time()}
                    if want_json:
                        try:
                            entry["data"] = resp.json()
                        except ValueError:
                            return None, 200
                    else:
                        entry["text"] = resp.text
                    self._disk_cache[etag_key] = entry
                    self._save_cache()
                if want_json:
                    try:
                        return resp.json(), 200
                    except ValueError:
                        return None, 200
                return resp.text, 200
            if code in _RETRY_STATUS and attempt < 2:
                ra = (resp.headers.get("Retry-After") or "").strip()
                try:
                    delay = float(ra) if ra else _RETRY_DELIMS[attempt]
                except ValueError:
                    delay = _RETRY_DELIMS[attempt]
                time.sleep(min(delay, 10.0) + random.uniform(0.0, 0.4))
                continue
            if code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
                if "search/" in url:
                    self._search_blocked = True
                elif "api.github.com" in url:
                    self._github_blocked = True
            return None, code
        return None, last_code

    # -- authless GitHub release discovery ------------------------------------
    def _releases_payload_authless(self, repo: str) -> dict | None:
        """Build an API-shaped release payload WITHOUT api.github.com.

        Tag from the /releases/latest web redirect (or the releases.atom
        feed when no release is marked 'latest'), assets from the
        expanded_assets HTML fragment - which also publishes each asset's
        sha256 digest and human-readable size. Returns None whenever ANY
        step is untrustworthy so the caller falls back to the (rate
        limited) REST API. Authless endpoints have no 60/hour quota - the
        root cause of intermittent "Check failed" runs.
        """
        try:
            tag = self._latest_tag_via_redirect(repo)
            if not tag:
                tag = self._latest_tag_via_atom(repo)
            if not tag:
                return None
            assets = self._assets_authless(repo, tag)
            if assets is None:
                return None
            return {
                "tag_name": tag,
                "assets": assets,
                "html_url": f"{GITHUB_WEB}/{repo}/releases/tag/{quote(tag)}",
            }
        except Exception:
            return None

    def _latest_tag_via_redirect(self, repo: str) -> str:
        """Tag from the 302 of https://github.com/OWNER/REPO/releases/latest
        ('.../releases/tag/<tag>'). Empty when the repo marks no 'latest'
        release (Location stays '.../releases') or the request fails - the
        atom feed covers both cases."""
        try:
            r = self.session.get(f"{GITHUB_WEB}/{repo}/releases/latest",
                                 timeout=(_CONNECT_TIMEOUT, 20),
                                 allow_redirects=False)
            if r.status_code in (301, 302, 303, 307, 308):
                m = _LOCATION_TAG_RE.search(r.headers.get("Location") or "")
                if m:
                    return unquote(m.group(1))
        except Exception:
            pass
        return ""

    def _latest_tag_via_atom(self, repo: str) -> str:
        text, code = self._http(f"{GITHUB_WEB}/{repo}/releases.atom",
                                timeout=(_CONNECT_TIMEOUT, 20))
        if code != 200 or not text:
            return ""
        return _latest_stable_tag_from_atom(text)

    def _assets_authless(self, repo: str, tag: str) -> list | None:
        text, code = self._http(
            f"{GITHUB_WEB}/{repo}/releases/expanded_assets/{quote(tag)}",
            timeout=(_CONNECT_TIMEOUT, 20))
        if code != 200 or not text:
            return None
        return _assets_from_expanded_html(text, repo)

    # -- public API ----------------------------------------------------------
    def check_app(self, app: InstalledApp) -> CheckResult:
        res = CheckResult(app_name=app.name, installed_version=app.version.strip(),
                          arch="x64" if self.bitness == 64 else "x86")
        normalized = normalize_name(app.name)

        # 1) System runtimes tracked by winget-pkgs (VC++ Redistributables,
        #    WebView2, .NET runtimes) are checked from their official
        #    manifests - exactly what `winget upgrade` does.
        winget_src = catalog.winget_package_for(app.name, os_bitness=self.bitness)
        blocked_key = None
        if winget_src is not None:
            src = {"type": "winget", **winget_src}
        else:
            blocked_key = catalog.blocked_reason_key(
                normalized, normalize_name(app.publisher or ""))

            # 2) curated catalog (hand-verified official sources)
            entry = self.resolve_curated(normalized)
            if entry is not None:
                src = entry["source"]
            else:
                # 3) UniGetUI technique: ask the winget CLI which official
                #    catalog package this installed app belongs to, then
                #    check that package's official manifest. This rescues
                #    vendor-managed AND unknown apps whenever winget knows
                #    them, and it CANNOT be rate-limited - so it runs BEFORE
                #    any GitHub name search now (the old order burned the
                #    search quota and could junk-match before winget spoke).
                wid, hint = winget_bridge.lookup_with_hint(app.name)
                if not wid:
                    wid, hint = winget_bridge.search_by_name(app.name)
                if wid:
                    src = {"type": "winget", "package_id": wid,
                           "arch": "x64" if self.bitness == 64 else "x86",
                           "hint_version": hint}
                else:
                    # 4) GitHub auto-search as the LAST fallback
                    entry = self._github_search_source(normalized)
                    if entry is not None:
                        src = entry["source"]
                    elif blocked_key:
                        res.status = "vendor"
                        res.set_note(blocked_key)
                        res.source_label = "Vendor-managed"
                        return res
                    else:
                        res.status = "no_source"
                        res.set_note("note.no_source")
                        return res

        try:
            handler = getattr(self, f"_check_{src['type']}")
            handler(src, res)
        except Exception as exc:  # network bugs must never crash the app
            res.status = "failed"
            res.set_note("note.check_error", cls=exc.__class__.__name__)

        # A GitHub release without an installer for this OS (or no release
        # at all) is not the final word: the winget catalog often carries
        # the same app with a proper installer (UniGetUI never trusts ONE
        # source either). Rescue before concluding, memoized per package.
        if (winget_src is None and src.get("type") == "github" and
                res.status in ("no_source", "no_installer") and
                not res.installer_url):
            wid, hint = winget_bridge.lookup_with_hint(app.name)
            if not wid:
                wid, hint = winget_bridge.search_by_name(app.name)
            if wid:
                prev_parts = res.note_parts
                prev_plain = res.note
                for f in ("latest_version", "installer_url", "source_label",
                          "source_url", "sha256", "note"):
                    setattr(res, f, "")
                res.note_parts = []
                res.size_bytes = 0
                try:
                    self._check_winget(
                        {"type": "winget", "package_id": wid,
                         "arch": "x64" if self.bitness == 64 else "x86",
                         "hint_version": hint}, res)
                except Exception:
                    res.status = "no_installer"
                    res.note_parts = prev_parts
                    res.note = prev_plain

        # The winget manifest route failed for a KNOWN vendor-managed app:
        # the vendor explanation is the more honest answer (e.g. winget
        # does not track driver bundles, and a missing arch installer in a
        # manifest is not the same as 'nothing manages this app').
        if (blocked_key and winget_src is None and
                res.status in ("no_source", "no_installer") and
                not res.installer_url):
            res.status = "vendor"
            res.set_note(blocked_key)
            res.source_label = "Vendor-managed"
            res.source_url = ""
        return self._probe_size(self._finalize(res))

    def _probe_size(self, res: CheckResult) -> CheckResult:
        """Attach the exact download size (bytes) of the installer when an
        update will actually be offered. Best effort - 0 means 'unknown'."""
        if (res.status != "update" or not res.installer_url
                or res.size_bytes > 0):
            return res
        try:
            # 1) cheap HEAD request first
            r = self.session.head(res.installer_url, timeout=15,
                                  allow_redirects=True)
            if r.status_code < 400:
                cl = (r.headers.get("Content-Length") or "").strip()
                if cl.isdigit():
                    res.size_bytes = int(cl)
                    return res
            # 2) fallback: 1-byte ranged GET (some servers refuse HEAD)
            with self.session.get(res.installer_url, timeout=20, stream=True,
                                  headers={"Range": "bytes=0-0"}) as r2:
                if r2.status_code == 206:
                    total = (r2.headers.get("Content-Range") or
                             "").rsplit("/", 1)
                    if len(total) == 2 and total[1].strip().isdigit():
                        res.size_bytes = int(total[1])
                elif r2.status_code == 200:
                    cl = (r2.headers.get("Content-Length") or "").strip()
                    if cl.isdigit():
                        res.size_bytes = int(cl)
        except Exception:
            pass  # size stays unknown; everything else is unaffected
        return res

    @staticmethod
    def _finalize(res: CheckResult) -> CheckResult:
        """Make the status honest with respect to the installed version.

        Key rule: if the installed version EQUALS the latest one the app is
        'Up to date' - even when the release ships no installer for this OS
        (there is simply nothing to download).
        """
        if res.status not in ("update", "latest", "no_installer"):
            return res
        cmp = compare_versions(res.installed_version, res.latest_version)
        if res.installed_version and cmp == 0 and res.status != "latest":
            res.status = "latest"
            if (res.note_key() in _NO_INSTALLER_NOTE_KEYS
                    or "installer" in res.note_text().lower()):
                res.set_note("note.latest")
        elif (res.installed_version and res.latest_version and cmp > 0
              and res.status == "no_installer"):
            # installed is NEWER than the latest public release (beta channel)
            res.status = "latest"
            res.set_note("note.newer_than_latest")
        elif not res.installed_version and res.status in ("update", "latest"):
            res.status = "update"
            if not res.note_text():
                res.set_note("note.version_unknown")
        elif cmp < 0 and res.status == "latest":
            res.status = "update"
        return res

    # -- winget-pkgs manifest checking ---------------------------------------
    @staticmethod
    def _winget_path(pkg_id: str) -> str:
        """Package ID -> manifest path, e.g.
        Microsoft.VCRedist.2015+.x64 -> manifests/m/Microsoft/VCRedist/2015+/x64."""
        return f"manifests/{pkg_id[0].lower()}/" + pkg_id.replace(".", "/")

    @staticmethod
    def _installer_entries(text: str) -> list[dict]:
        """All installer entries of a winget installer manifest, regex-parsed
        (no YAML dependency): [{'arch','locale','url','sha256'}, ...]."""
        m = re.search(r"(?ms)^Installers:\s*\n(.*?)(?=^[A-Za-z]|\Z)", text)
        section = m.group(1) if m else text
        entries_out: list[dict] = []
        for e in re.split(r"(?m)^\s*-\s+", section)[1:]:
            um = re.search(r"(?m)^\s*InstallerUrl:\s*(\S+)", e)
            if not um:
                continue
            am = re.search(r"(?m)^\s*Architecture:\s*([A-Za-z0-9]+)", e)
            sm = re.search(r"(?m)^\s*InstallerSha256:\s*([0-9A-Fa-f]+)", e)
            entries_out.append({
                "arch": (am.group(1).lower() if am else "neutral"),
                "locale": bool(re.search(r"(?m)^\s*InstallerLocale:", e)),
                "url": um.group(1),
                "sha256": (sm.group(1).lower() if sm else ""),
            })
        return entries_out

    @staticmethod
    def _pick_installer(text: str, want: str) -> tuple[str, str]:
        """(InstallerUrl, InstallerSha256) for the `want` architecture.
        Prefers entries WITHOUT an InstallerLocale (the English/neutral
        build) over localised re-uploads."""
        cands = UpdateChecker._installer_entries(text)
        exact = [c for c in cands if c["arch"] == want]
        pool = exact or [c for c in cands if c["arch"] == "neutral"]
        if not pool:
            return "", ""
        pool.sort(key=lambda c: c["locale"])   # non-localised first
        return pool[0]["url"], pool[0]["sha256"]

    @staticmethod
    def _parse_installer_yaml(text: str, want: str) -> str:
        """Pick the official InstallerUrl for `want` architecture from a
        winget installer manifest (kept for compatibility with callers and
        the self-test; new code uses _pick_installer)."""
        url, _sha = UpdateChecker._pick_installer(text, want)
        return url

    @staticmethod
    def _version_sort_key(v: str) -> list[int]:
        nums = [int(x) for x in re.findall(r"\d+", v)[:5]]
        return nums if nums else [0]

    def _winget_manifest_at(self, pkg: str, want: str, version: str):
        """Installer manifest for ONE exact version -> (version, url, sha256),
        or None on any failure (caller falls through to the next source
        layer). Only used by the hint/CLI paths; the API path keeps its own
        exact status messages."""
        try:
            path = self._winget_path(pkg)
            yaml_text, ycode = self._get(
                f"{WINGET_RAW}{quote(path)}/{quote(version)}/{quote(pkg)}.installer.yaml")
        except Exception:
            return None
        if ycode != 200 or not yaml_text:
            return None
        url, sha = self._pick_installer(yaml_text, want)
        if not url:
            return None
        return (version, url, sha)

    def _winget_latest_via_api(self, pkg: str, want: str, res: CheckResult):
        """Last-resort winget version listing via the GitHub contents API
        (etag-cached). Returns the cached (latest, url, sha) tuple or None
        after writing an honest failure status into `res`."""
        if self._github_blocked:
            res.status = "failed"
            res.set_note("note.rate_limited")
            return None
        path = self._winget_path(pkg)
        data, code = self._get(WINGET_API + quote(path), want_json=True,
                               etag_cache=True)
        if code == 404:
            res.status = "no_source"
            res.set_note("note.no_winget_manifest")
            return None
        if code != 200 or not isinstance(data, list):
            res.status = "failed"
            res.set_note("note.winget_list_error", code=code or 'network')
            return None
        versions = [e.get("name", "") for e in data
                    if isinstance(e, dict) and e.get("type") == "dir"]
        versions = [v for v in versions if re.search(r"\d", v)]
        if not versions:
            res.status = "no_source"
            res.set_note("note.no_winget_versions")
            return None
        latest = max(versions, key=self._version_sort_key)
        yaml_text, ycode = self._get(
            f"{WINGET_RAW}{quote(path)}/{quote(latest)}/{quote(pkg)}.installer.yaml")
        if ycode == 404:
            res.status = "no_source"
            res.set_note("note.winget_installer_missing")
            return None
        if ycode != 200 or not yaml_text:
            res.status = "failed"
            res.set_note("note.winget_installer_error", code=ycode)
            return None
        url, sha = self._pick_installer(yaml_text, want)
        return (latest, url, sha)

    def _check_winget(self, src: dict, res: CheckResult) -> None:
        """Check a system runtime against its official winget-pkgs manifest
        (the same data source the `winget upgrade` command uses).

        Version honesty rules for these MSI/burn installers:
        * "12.0.40664" installed vs "12.0.40664.0" manifest -> SAME build
          (zero-padded equality) - the row shows 'Up to date', never a
          phantom update that reinstalling could never resolve;
        * installed NEWER than the manifest (winget-pkgs sometimes lags) ->
          'Up to date', never a downgrade.

        Version discovery is layered so a GitHub API outage can never fail
        the check (UniGetUI pattern - its winget backend never scrapes
        api.github.com either):
          1. the winget source's OWN hint (the 'Available' column of
             `winget list` or the catalog-search version) -> manifest for
             that exact version, zero listing requests;
          2. `winget show --id X --versions` (winget CLI, no GitHub quota);
          3. api.github.com contents listing (etag-cached) as last resort.
        """
        pkg = src["package_id"]
        want = src.get("arch") or "x64"
        hint = str(src.get("hint_version") or "").strip()

        cached = self._winget_cache.get((pkg, want))
        if cached is None:
            # several rows share one package (VC++ x86/x64 across years) -
            # resolution runs once per package+arch per run.
            if hint and re.search(r"\d", hint):
                cached = self._winget_manifest_at(pkg, want, hint)
            if cached is None:
                versions = [v for v in winget_bridge.package_versions(pkg)
                            if re.search(r"\d", v)]
                if versions:
                    latest = max(versions, key=self._version_sort_key)
                    cached = self._winget_manifest_at(pkg, want, latest)
            if cached is None:
                cached = self._winget_latest_via_api(pkg, want, res)
                if cached is None:
                    return  # honest failure status already written
            self._winget_cache[(pkg, want)] = cached
        latest, url, sha = cached

        res.latest_version = latest
        res.arch = want
        res.source_label = "Winget official manifest"
        res.sha256 = sha
        res.source_url = ("https://github.com/microsoft/winget-pkgs/tree/master/"
                          + quote(self._winget_path(pkg)) + "/" + quote(latest))
        if not url:
            res.status = "no_installer"
            res.set_note("note.winget_no_arch", arch=want)
            return
        if res.installed_version:
            cmp = compare_versions(res.installed_version, latest)
            if cmp == 0 or prefix_equal(res.installed_version, latest):
                res.status = "latest"
                res.set_note("note.latest")
                return
            if cmp > 0:
                res.status = "latest"
                res.set_note("note.newer_than_latest")
                return
        res.installer_url = url
        res.status = "update"
        if not res.installed_version:
            res.set_note("note.version_unknown")

    # -- source resolution ----------------------------------------------------
    def resolve_curated(self, normalized_name: str) -> dict | None:
        """Best curated-catalog entry for a normalized app name, or None.
        (GitHub auto-search is deliberately NOT part of this - it is tried
        only after the winget bridge, which cannot be rate-limited.)"""
        best, best_score = None, 0
        name_tokens = set(normalized_name.split())
        for e in catalog.entries():
            if any(x and x in normalized_name for x in e["exclude_match"]):
                continue
            score = 0
            for pattern in e["match"]:
                pat_tokens = set(pattern.split())
                if not pat_tokens or any(len(t) < 2 for t in pat_tokens):
                    continue
                if normalized_name == pattern:
                    score = max(score, 3)
                elif pat_tokens.issubset(name_tokens):
                    score = max(score, 2)
                elif pattern and pattern in normalized_name and len(pattern) >= 4:
                    score = max(score, 1)
            if score > best_score:
                best, best_score = e, score
        return best

    def resolve_source(self, normalized_name: str) -> dict | None:
        """Curated entry first, then the GitHub auto-search fallback
        (kept for compatibility with existing callers/tests)."""
        best = self.resolve_curated(normalized_name)
        if best is not None:
            return best
        return self._github_search_source(normalized_name)

    @staticmethod
    def _auto_match_ok(repo: dict, normalized_name: str) -> bool:
        """Confidence gate for GitHub auto-matching.

        Random personal repos with a matching name produced false updates
        (e.g. an unrelated 'spotplayer' project). Accept a repo only when it
        belongs to an Organization or is reasonably popular (>= 100 stars).
        """
        repo_name = normalize_name(repo.get("name", ""))
        if not repo_name or len(repo_name) < 3:
            return False
        if repo_name != normalized_name and not normalized_name.startswith(repo_name):
            return False
        owner = (repo.get("owner") or {}).get("type", "")
        try:
            stars = int(repo.get("stargazers_count") or 0)
        except (TypeError, ValueError):
            stars = 0
        return owner == "Organization" or stars >= 100

    def _github_search_source(self, normalized_name: str) -> dict | None:
        """Fallback: find a likely official GitHub repo by name."""
        if (not self.allow_github_search or self._search_blocked
                or self._github_blocked or self._searches_done >= 15):
            return None
        junk = ("microsoft ", "runtime", "redistributable", "driver", "sdk",
                "plugin", "add-in", "add-on", "component", "visual c++",
                "update ", "language pack", "tooltip", "shell extension")
        if len(normalized_name) < 3 or any(j in normalized_name for j in junk):
            return None
        try:
            time.sleep(0.4)  # be gentle with the search API
            self._searches_done += 1
            q = quote(f'"{normalized_name}" in:name fork:false')
            data, code = self._get(
                f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=5",
                want_json=True,
            )
            if code != 200 or not data:
                return None
            for repo in data.get("items", []):
                if not self._auto_match_ok(repo, normalized_name):
                    continue
                return {
                        "name": normalized_name,
                        "match": (),
                        "exclude_match": (),
                        "source": {
                            "type": "github",
                            "repo": repo["full_name"],
                            "auto": True,
                        },
                    }
        except Exception:
            return None
        return None

    # -- handlers --------------------------------------------------------------
    @staticmethod
    def _asset_excluded(low: str) -> bool:
        if any(x in low for x in DEFAULT_EXCLUDE):
            return True
        if _ARM_RE.search(low):  # plain ARM build
            return True
        if "arm64" in low and not any(k in low for k in X64_KEYS):
            return True  # arm64-only build (no x64 variant inside)
        return False

    def _pick_asset(self, src: dict, assets: list[dict], res: CheckResult) -> str:
        """Pick the best Windows asset for this machine's bitness. Returns URL."""
        want = "x64" if self.bitness == 64 else "x86"
        cands = []
        for a in assets:
            name = a.get("name", "")
            low = name.lower()
            if not low.endswith(EXTS):
                continue
            if src.get("exclude") and any(x in low for x in src["exclude"]):
                continue
            if self._asset_excluded(low):
                continue
            rx = src.get(want)
            if rx and not re.search(rx, name):
                continue
            cands.append(name)
        if not cands:
            return ""

        def score(n: str) -> tuple:
            cls = _classify_asset(n)
            if want == "x64":
                arch_score = 2 if cls == "x64" else (1 if cls == "neutral" else 0)
            else:
                arch_score = 2 if cls == "x86" else (1 if cls == "neutral" else 0)
            setup = 2 if re.search(r"(?i)setup|installer|install", n) else 0
            ext_score = 2 if n.lower().endswith(".exe") else (1 if n.lower().endswith(".msi") else 0)
            return (arch_score * 100 + setup * 10 + ext_score, arch_score)

        ranked = sorted(cands, key=score, reverse=True)
        best_cls = _classify_asset(ranked[0])
        if want == "x86" and best_cls == "x64":
            return ""  # cannot install a 64-bit build on 32-bit Windows
        res.arch = want if best_cls == "neutral" else best_cls
        return next(a["browser_download_url"] for a in assets if a.get("name") == ranked[0])

    def _check_github(self, src: dict, res: CheckResult) -> None:
        repo = src["repo"]
        # Primary: the authless web route (redirect + atom + expanded_assets).
        # api.github.com is only the fallback - its ~60 req/hour unauth
        # limit was the root cause of intermittent "Check failed" runs.
        data = self._releases_payload_authless(repo)
        if data is None:
            if self._github_blocked:
                res.status = "failed"
                res.set_note("note.rate_limited")
                return
            data, code = self._get(f"https://api.github.com/repos/{repo}/releases/latest",
                                   want_json=True, etag_cache=True)
            if code == 404:
                res.status = "no_source"
                res.set_note("note.repo_not_found")
                return
            if code != 200 or not data:
                res.status = "failed"
                res.set_note("note.github_error", code=code or 'network')
                return
        res.latest_version = _extract_version(data.get("tag_name", "") or "")
        if (src.get("auto") and res.installed_version and res.latest_version
                and compare_versions(res.installed_version, res.latest_version) > 0):
            # auto-matched repo is OLDER than what is installed -> junk match
            res.status = "no_source"
            res.set_note("note.auto_match_unrelated")
            res.source_label = ""
            res.source_url = ""
            return
        assets = data.get("assets", []) or []
        url = self._pick_asset(src, assets, res)
        # GitHub API reports the exact asset size for free - no extra request.
        picked = next((a for a in assets
                       if a.get("browser_download_url") == url), None)
        res.size_bytes = int(picked.get("size") or 0) if picked else 0
        digest = str(picked.get("digest") or "") if picked else ""
        if digest.startswith("sha256:"):
            res.sha256 = digest.split(":", 1)[1].strip().lower()
        if src.get("auto"):
            res.source_label = f"GitHub (auto-matched) - {repo}"
            if not res.note_text():
                res.set_note("note.matched_by_name")
        else:
            res.source_label = f"GitHub - {repo}"
        res.source_url = data.get("html_url", f"https://github.com/{repo}/releases")
        if not url:
            res.status = "no_installer"
            if not res.note:
                res.set_note("note.github_no_arch")
            return
        res.installer_url = url
        res.status = "update"

    @staticmethod
    def _template_candidates(template: str, version: str) -> list[str]:
        """Expand a URL template. {v} = version, {vv} = v-prefixed version,
        {vd} = version digits joined without dots (7.23 -> 723, rarlab style).

        Yields the primary form plus a fallback variant without the v prefix,
        because servers differ (nodejs.org uses v-prefixed paths, python.org
        does not).
        """
        vv = version if version.startswith("v") else "v" + version
        vd = "".join(re.findall(r"\d+", version))
        primary = (template.replace("{vv}", vv).replace("{v}", version)
                   .replace("{vd}", vd))
        fallback = (template.replace("{vv}", version).replace("{v}", version)
                    .replace("{vd}", vd))
        out = [primary]
        if fallback != primary:
            out.append(fallback)
        return out

    def _check_json(self, src: dict, res: CheckResult) -> None:
        data, code = self._get(src["url"], want_json=True, etag_cache=True)
        if code != 200 or data is None:
            res.status = "failed"
            res.set_note("note.feed_error", code=code)
            return
        version = None
        if src.get("items_path") is not None or isinstance(data, list):
            # list feed: optionally filter and pick the max version
            items = _dig(data, src["items_path"]) if src.get("items_path") else data
            if isinstance(items, list) and items:
                # plain list of strings (e.g. VS Code releases API)
                if all(isinstance(x, str) for x in items[:10]):
                    cands = [x.strip() for x in items if isinstance(x, str) and x.strip()]
                    if cands:
                        if src.get("take") == "first":
                            version = cands[0]
                        else:
                            version = sorted(cands, key=lambda s: [
                                int(x) for x in re.findall(r"\d+", s)[:4] or [0]
                            ])[-1]
                else:
                    prefix = src.get("filter_name_prefix", "")
                    skip_pre = src.get("filter_pre_release", False)
                    vrx = src.get("version_extract_regex")
                    candidates = []
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        if skip_pre and item.get("pre_release") in (True, "True", "true"):
                            continue
                        raw = _dig(item, src.get("version_path", ""))
                        if not isinstance(raw, str) or not raw:
                            continue
                        if prefix and not raw.startswith(prefix):
                            continue
                        v = raw
                        if vrx:
                            m = re.search(vrx, raw)
                            if not m:
                                continue
                            v = m.group(1)
                        candidates.append(v)
                    if candidates:
                        def vkey(v: str):
                            return [int(x) for x in re.findall(r"\d+", v)[:4]]
                        version = sorted(candidates, key=vkey)[-1]
        else:
            for path in src.get("version_paths", []):
                v = _dig(data, path)
                if isinstance(v, str) and re.search(r"\d", v):
                    version = v.lstrip("v")
                    break
        if not version:
            res.status = "failed"
            res.set_note("note.feed_parse")
            return
        res.latest_version = version.lstrip("v")
        want = "x64" if self.bitness == 64 else "x86"
        assets = src.get("assets", {})
        url = assets.get(want) or assets.get("any") or ""
        if not url:
            templates = src.get("url_templates", {}).get(want) or []
            if src.get("verify") is False:
                url = (self._template_candidates(templates[0], version)[0]
                       if templates else "")
            else:
                urls: list[str] = []
                for t in templates:
                    urls.extend(self._template_candidates(t, version))
                url = self._first_working(urls)
        res.source_label = "Official version feed"
        if not url:
            res.status = "no_installer"
            if not res.note_text():
                res.set_note("note.no_installer_url")
            return
        res.installer_url = url
        res.status = "update"

    def _check_plain(self, src: dict, res: CheckResult) -> None:
        text, code = self._get(src["url"])
        if code != 200 or not text:
            res.status = "failed"
            res.set_note("note.feed_error", code=code)
            return
        m = re.search(src["version_regex"], text)
        if not m:
            res.status = "failed"
            res.set_note("note.feed_parse")
            return
        res.latest_version = m.group(1)
        want = "x64" if self.bitness == 64 else "x86"
        templates = src.get("url_templates", {}).get(want) or []
        urls: list[str] = []
        for t in templates:
            urls.extend(self._template_candidates(t, m.group(1)))
        url = self._first_working(urls)
        res.source_label = "Official version feed"
        if not url:
            res.status = "no_installer"
            if not res.note_text():
                res.set_note("note.no_installer_url")
            return
        res.installer_url = url
        res.status = "update"

    def _check_html(self, src: dict, res: CheckResult) -> None:
        text, code = self._get(src["url"])
        if code != 200 or not text:
            res.status = "failed"
            res.set_note("note.vendor_page_error", code=code)
            return
        want = "x64" if self.bitness == 64 else "x86"
        variant = src.get(want) if want in ("x64", "x86") else None
        if isinstance(variant, dict) and variant.get("no_installer"):
            # vendor explicitly publishes nothing for this architecture
            res.latest_version = res.latest_version or ""
            res.status = "no_installer"
            res.set_note(variant["note"] if variant.get("note")
            else "note.vendor_arch_installer_missing")
            return
        source = variant or src
        take = source.get("take", src.get("take", "first"))
        url = version = ""
        if source.get("url_regex"):
            matches = re.findall(source["url_regex"], text)
            if matches and isinstance(matches[0], tuple):
                matches = [m[0] for m in matches]
            base_origin = ""
            m_org = re.match(r"(https?://[^/]+)", src["url"])
            if m_org:
                base_origin = m_org.group(1)
            fixed = []
            for u in matches:
                if u.startswith("//"):
                    u = "https:" + u
                elif u.startswith("/") and base_origin:
                    u = base_origin + u
                elif not u.startswith("http") and base_origin:
                    u = base_origin + "/" + u
                if u.startswith("http"):
                    fixed.append(u)
            matches = fixed
            if matches:
                if take == "max" and len(matches) > 1:
                    matches.sort(key=lambda u: [int(x) for x in re.findall(r"\d+", u)[:3]])
                    url = matches[-1]
                else:
                    url = matches[0]
                # Prefer the explicit version capture group over scanning the URL
                if source.get("url_regex").count("(") >= 2:
                    m2 = re.search(source["url_regex"], url)
                    if m2:
                        try:
                            g2 = m2.group(2)
                            if g2:
                                version = g2
                        except (IndexError, re.error):
                            pass
                version = version or _extract_version(url)
        elif source.get("version_regex"):
            matches = re.findall(source["version_regex"], text)
            if matches:
                if take == "max" and len(matches) > 1:
                    def vkey(v: str):
                        return [int(x) for x in re.findall(r"\d+", v)[:4]]
                    matches.sort(key=vkey)
                    version = matches[-1]
                elif take == "last":
                    version = matches[-1]
                else:
                    version = matches[0]
        if not version:
            res.status = "failed"
            res.set_note("note.vendor_latest_unknown")
            return
        res.latest_version = version
        if not url:
            templates = (src.get("url_templates") or {}).get(want) or []
            if src.get("verify") is False:
                url = (self._template_candidates(templates[0], version)[0]
                       if templates else "")
            else:
                urls: list[str] = []
                for t in templates:
                    urls.extend(
                        self._template_candidates(
                            t.replace("{v:1.2}", _version_token(version, 2)), version
                        )
                    )
                url = self._first_working(urls)
        res.source_label = "Official website"
        if not url:
            res.status = "no_installer"
            if not res.note_text():
                res.set_note("note.vendor_no_arch")
            return
        res.installer_url = url
        res.status = "update"

    def _check_mozilla(self, src: dict, res: CheckResult) -> None:
        data, code = self._get(src["json_url"], want_json=True, etag_cache=True)
        if code != 200 or not data:
            res.status = "failed"
            res.set_note("note.mozilla_feed_error", code=code)
            return
        version = (data.get(src["version_key"]) or "").strip()
        if not version:
            res.status = "failed"
            res.set_note("note.mozilla_parse")
            return
        res.latest_version = version.lstrip("v")
        res.installer_url = src["url64"] if self.bitness == 64 else src["url32"]
        res.arch = "x64" if self.bitness == 64 else "x86"
        res.source_label = "Mozilla official download"
        res.source_url = "https://www.mozilla.org/"
        res.status = "update"

    def _check_videolan(self, src: dict, res: CheckResult) -> None:
        """VLC version + installer discovery on BOTH official VideoLAN hosts.

        get.videolan.org is the geo redirector (fast, but the mirror it picks
        can be broken or intercepted - on some routes the transfer dies or a
        block page arrives). download.videolan.org is VideoLAN's OWN canonical
        server that serves the same files directly. The checker reads both and
        the result carries the second host as an OFFICIAL FALLBACK URL, so the
        downloader can switch servers when the first one misbehaves instead of
        leaving the user with a failed download and no installer to open.
        """
        folder = "win64" if self.bitness == 64 else "win32"
        text, code = self._get(f"https://get.videolan.org/vlc/last/{folder}/")
        if code != 200 or not text or "vlc-" not in text:
            # the redirector failed - its canonical twin serves the same tree
            text, code = self._get(
                f"https://download.videolan.org/pub/videolan/vlc/last/{folder}/")
        if code != 200 or not text:
            res.status = "failed"
            res.set_note("note.vlc_server_error", code=code)
            return
        m = re.search(rf"vlc-([0-9.]+)-{folder}\.exe", text)
        if not m:
            res.status = "no_installer"
            res.set_note("note.vlc_no_installer")
            return
        ver = m.group(1)
        res.latest_version = ver
        res.installer_url = (f"https://get.videolan.org/vlc/last/{folder}/"
                             f"vlc-{ver}-{folder}.exe")
        res.alt_urls = (f"https://download.videolan.org/pub/videolan/vlc/"
                        f"{ver}/{folder}/vlc-{ver}-{folder}.exe",)
        res.arch = "x64" if folder == "win64" else "x86"
        res.source_label = "VideoLAN official mirror"
        res.source_url = "https://www.videolan.org/vlc/"
        res.status = "update"
        # VideoLAN publishes "<installer>.sha256" next to every download.
        # Fetch it so the downloader can verify the file byte-for-byte -
        # some mirrors (or network middleboxes) answer with error pages,
        # which previously reached the user as a corrupt installer.
        # CAUTION (live-reproduced): an HTML page can arrive with HTTP 200
        # on either host - a random 64-hex string inside that page must
        # NEVER become the expected checksum (it would delete a perfectly
        # good download). A checksum payload is tiny and STARTS with the
        # hash; anything else is treated as "no checksum" and the next
        # host's .sha256 is tried.
        for sha_url in (res.installer_url + ".sha256",) + tuple(
                u + ".sha256" for u in res.alt_urls):
            try:
                sha_text, sha_code = self._get(sha_url)
            except Exception:
                continue  # checksum stays empty; signature checks still run
            if sha_code == 200 and sha_text:
                text = sha_text.strip()
                if len(text) <= 512:
                    sm = re.match(r"([0-9a-fA-F]{64})\b", text)
                    if sm:
                        res.sha256 = sm.group(1).lower()
                        break

    def _check_edge(self, src: dict, res: CheckResult) -> None:
        data, code = self._get("https://edgeupdates.microsoft.com/api/products",
                               want_json=True, etag_cache=True)
        if code != 200 or not data:
            res.status = "failed"
            res.set_note("note.edge_feed_error", code=code)
            return
        want = "x64" if self.bitness == 64 else "x86"
        best = None
        for product in data:
            if product.get("Product") != "Stable":
                continue
            for rel in product.get("Releases", []):
                if rel.get("Platform") != "Windows" or rel.get("Architecture") != want:
                    continue
                if best is None or (rel.get("ReleaseId") or 0) > (best.get("ReleaseId") or 0):
                    best = rel
        if not best:
            res.status = "no_installer"
            res.set_note("note.edge_no_stable")
            return
        res.latest_version = best.get("ProductVersion", "")
        locs = [a.get("Location", "") for a in best.get("Artifacts", [])]
        msi = [u for u in locs if u.lower().endswith(".msi")]
        exe = [u for u in locs if u.lower().endswith(".exe")]
        res.installer_url = (msi or exe or [""])[0]
        res.arch = want
        res.source_label = "Microsoft Edge official updates"
        res.source_url = "https://www.microsoft.com/edge/download"
        if not res.installer_url:
            res.status = "no_installer"
            return
        res.status = "update"

    def _check_discord(self, src: dict, res: CheckResult) -> None:
        want = "x64" if self.bitness == 64 else "x86"
        data, code = self._get(
            f"https://discord.com/api/updates/distributions/app/manifests/latest"
            f"?channel=stable&platform=win&arch={want}",
            want_json=True,
        )
        version = ""
        if code == 200 and data:
            found = self._find_host_version(data)
            if found:
                version = ".".join(str(x) for x in found)
        if not version:
            # fall back: still allow download of the always-latest installer
            res.latest_version = ""
            res.installer_url = (
                "https://discord.com/api/downloads/distributions/app/installers/latest"
                f"?channel=stable&platform=win&arch={want}"
            )
            res.arch = want
            res.source_label = "Discord official download"
            res.status = "update"
            if not res.note_text():
                res.set_note("note.discord_no_version")
            return
        res.latest_version = version
        res.installer_url = (
            "https://discord.com/api/downloads/distributions/app/installers/latest"
            f"?channel=stable&platform=win&arch={want}"
        )
        res.arch = want
        res.source_label = "Discord official download"
        res.status = "update"

    @staticmethod
    def _find_host_version(obj: Any, depth: int = 0) -> list | None:
        if depth > 6:
            return None
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "host_version" and isinstance(v, list) and v:
                    return v
                got = UpdateChecker._find_host_version(v, depth + 1)
                if got:
                    return got
        elif isinstance(obj, list):
            for item in obj:
                got = UpdateChecker._find_host_version(item, depth + 1)
                if got:
                    return got
        return None

    def _check_dir_download(self, src: dict, res: CheckResult) -> None:
        text, code = self._get(src["base"])
        if code != 200 or not text:
            res.status = "failed"
            res.set_note("note.dl_server_error", code=code)
            return
        dirs = re.findall(src["dir_regex"], text)
        if not dirs:
            res.status = "failed"
            res.set_note("note.dl_list_error")
            return

        def vkey(v: str):
            return [int(x) for x in re.findall(r"\d+", v)[:3]]

        dirs = sorted(set(dirs), key=vkey)
        latest_dir = dirs[-1]
        sub = src["base"].rstrip("/") + "/Blender" + latest_dir + "/"
        text2, code2 = self._get(sub)
        if code2 != 200 or not text2:
            res.status = "failed"
            res.set_note("note.dl_server_error", code=code2)
            return
        if self.bitness != 64:
            res.status = "no_installer"
            res.set_note("note.blender_64bit_only")
            return
        file_rx = src["file_regex"].replace("{d}", re.escape(latest_dir) + r"\.?")
        files = re.findall(file_rx, text2)
        files = [f for f in files if isinstance(f, str)]
        if not files:
            res.status = "no_installer"
            res.set_note("note.no_windows_installer_folder")
            return
        files = sorted(set(files), key=vkey)
        fname = files[-1]
        res.latest_version = _extract_version(fname)
        res.installer_url = sub + fname
        res.arch = "x64"
        res.source_label = "Official download server"
        res.source_url = "https://www.blender.org/download/"
        res.status = "update"

    # -- helpers ---------------------------------------------------------------
    def _first_working(self, urls) -> str:
        for url in urls:
            if not url:
                continue
            if self._url_exists(url):
                return url
        return ""

    def _url_exists(self, url: str) -> bool:
        try:
            r = self.session.head(url, timeout=10, allow_redirects=True)
            if r.status_code < 400:
                return True
            # some servers reject HEAD
            r = self.session.get(url, timeout=10, stream=True,
                                 headers={"Range": "bytes=0-0"})
            ok = r.status_code in (200, 206) or (r.status_code < 400 and r.status_code != 404)
            try:
                r.close()
            except Exception:
                pass
            return ok
        except Exception:
            return False


def check_apps(apps: list[InstalledApp], progress: Callable[[int, int], None] | None = None,
               cache_dir: str | None = None) -> list[CheckResult]:
    """Convenience wrapper used by the worker thread."""
    checker = UpdateChecker(cache_dir=cache_dir)
    results = []
    total = len(apps)
    for i, app in enumerate(apps, 1):
        results.append(checker.check_app(app))
        if progress:
            progress(i, total)
    return results
