"""Per-app icon engine (UniGetUI's IconStore idea, adapted).

UniGetUI resolves one icon per package from several sources and caches it
on disk keyed by an identity hash, so the list never waits on the network
and an updated package simply gets a new cache entry. Our engine mirrors
that with an OFFLINE-FIRST pipeline (the user's list must never depend on
the network for something the machine already knows):

  Tier 1 - local, in priority order (installed_apps registry facts):
    1. DisplayIcon (exe/dll/ico the vendor registered)
    2. Start-Menu / Desktop shortcut (.lnk): its own IconLocation (what the
       shortcut actually displays) or the exe it points at - this is what
       rescues per-user installs (Chrome, Discord, Epic, ...) whose ARP
       DisplayIcon is empty or stale
    3. the app's InstallLocation folder: best-matching exe/ico
    4. well-known roots (Program Files / LocalAppData) scanned for a folder
       named after the app, same best-match walk inside
  Tier 2 - online, ONLY for rows where every local strategy failed and only
    when the caller opted in (the background IconWorker): UniGetUI's own
    community icon database (one JSON, cached on disk for days) is searched
    by slug and the matched image is downloaded once, magic-byte validated
    and cached (e.g. LAV Filters, which ships no exe icon at all).
  Fallback - a themed letter tile drawn with QPainter so EVERY row shows
    something clean instead of a broken image.

Extraction happens in a background QThread (QFileIconProvider = the Windows
shell icon); PNG bytes travel to the main thread over a queued signal.
"""

from __future__ import annotations
from __future__ import annotations

import hashlib
import os
import re
import time

# Extraction at 48 px: crisp at our ~20 px table size and usable in the
# details dialog without a second extraction pass.
_EXTRACT_PX = 48

try:
    from PySide6.QtCore import QBuffer, QByteArray, QFileInfo, QRectF, Qt
    from PySide6.QtGui import (QColor, QFont, QIcon, QImage, QPainter,
                               QPainterPath)
    from PySide6.QtWidgets import QFileIconProvider

    _QT_OK = True
except Exception:  # pragma: no cover - headless import guard
    _QT_OK = False


def icons_dir() -> str:
    """Disk cache directory for extracted app icons."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = "/tmp"
    return os.path.join(base, "SoftUpdater", "icons")


def _web_icons_dir() -> str:
    return os.path.join(icons_dir(), "web")


def cache_key(path: str) -> str:
    """Identity of one icon source file: path + size + mtime.

    Reinstalling/updating the app changes size or mtime -> new key -> the
    fresh icon is extracted instead of serving a stale cached one.
    """
    try:
        st = os.stat(path)
        ident = f"{os.path.normpath(path).lower()}|{st.st_size}|{int(st.st_mtime)}"
    except OSError:
        ident = f"{os.path.normpath(path or '?').lower()}|missing"
    return hashlib.sha1(ident.encode("utf-8", "replace")).hexdigest()[:12] + ".png"


def cached_icon_file(path: str) -> str:
    """Full cache path for an icon source, existing or not."""
    return os.path.join(icons_dir(), cache_key(path))


def _qimage_png_bytes(img) -> bytes:
    """Encode a QImage to PNG bytes ('' on any failure)."""
    if not _QT_OK or img is None or img.isNull():
        return ""
    buf = QBuffer()
    if not buf.open(QBuffer.OpenModeFlag.WriteOnly):
        return ""
    if not img.save(buf, "PNG"):
        return ""
    return bytes(buf.data())


def extract_icon_png(path: str) -> bytes:
    """Extract the icon embedded in `path` (exe/dll/ico) as PNG bytes.

    Uses QFileIconProvider (the Windows shell icon extraction). Runs inside
    the IconWorker thread; on Windows the underlying GDI calls are
    thread-safe, and every failure simply returns '' (the caller falls back
    to the letter tile).
    """
    if not _QT_OK or not path:
        return ""
    try:
        from PySide6.QtWidgets import QApplication

        if QApplication.instance() is None:
            return ""  # no GUI app context (defensive; worker runs inside one)
        icon = QFileIconProvider().icon(QFileInfo(path))
        if icon is None or icon.isNull():
            return ""
        pm = icon.pixmap(_EXTRACT_PX, _EXTRACT_PX)
        if pm is None or pm.isNull() or pm.width() < 8:
            return ""
        return _qimage_png_bytes(pm.toImage())
    except Exception:
        return ""


def letter_tile_png(name: str, size: int = _EXTRACT_PX) -> bytes:
    """Themed fallback tile: dark glass circle, accent ring, initial letter.

    Drawn programmatically (same visual language as the tray icon) so rows
    without a discoverable icon still look intentional and clean.
    """
    if not _QT_OK:
        return ""
    try:
        from PySide6.QtWidgets import QApplication

        if QApplication.instance() is None:
            return ""  # never touch QFont/QPainter without a GUI app
        from . import theme

        img = QImage(size, size, QImage.Format.Format_ARGB32)
        img.fill(0)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(1.5, 1.5, size - 3.0, size - 3.0)
        path = QPainterPath()
        path.addEllipse(rect)
        p.fillPath(path, QColor("#1c2733"))
        ring = theme.ACCENT
        p.setPen(QColor(ring))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(rect.adjusted(1.0, 1.0, -1.0, -1.0))
        letter = (name or "?").strip()[:1].upper() or "?"
        f = QFont()
        f.setPixelSize(max(10, int(size * 0.46)))
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(theme.TEXT))
        p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, letter)
        p.end()
        return _qimage_png_bytes(img)
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Tier 1: local icon-source discovery
# ---------------------------------------------------------------------------

# Generic words that never identify an app (tokens ignored for matching).
_GENERIC_TOKENS = frozenset((
    "media", "player", "update", "bit", "bits", "x64", "x86", "amd64",
    "win64", "win32", "windows", "microsoft", "soft", "software", "app",
    "application", "free", "the", "and", "for", "with", "edition",
    "version", "build", "setup", "installer", "install", "uninstall",
    "redistributable", "runtime", "package", "kit", "development",
    "environment", "se", "jdk", "jre", "client", "manager", "suite",
    "system", "corporation", "limited", "gmbh", "inc", "llc",
))

# exe names that are never the app's icon carrier.
_JUNK_STEMS = ("unins", "uninst", "setup", "bootstrapp", "crashpad",
               "crashreport", "updater", "sendrpt", "minidump")

_ICO_EXTS = (".exe", ".ico")


def _tokens(text: str) -> list[str]:
    """Distinctive lowercase tokens of a name (generic words/numbers gone)."""
    raw = [t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if t]
    return [t for t in raw
            if t not in _GENERIC_TOKENS and not t.isdigit() and len(t) >= 2]


def _best_in_dir(root: str, toks: list[str], max_depth: int = 3,
                 max_files: int = 600) -> list[str]:
    """Best-matching exe/ico files inside `root` (depth-capped walk).

    Scoring: file stem EQUAL to a name token wins, a prefix/containment
    match (javaw for Java) ranks lower, bigger files break ties. Junk
    names (unins*, setup*, updater...) never win. Returns at most 2 paths.
    """
    out: list[tuple[int, int, str]] = []
    root_depth = os.path.normpath(root).rstrip("\\/").count(os.sep)
    seen = 0
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            depth = os.path.normpath(dirpath).rstrip("\\/")\
                .count(os.sep) - root_depth
            if depth >= max_depth:
                dirnames[:] = []
            for fn in filenames:
                seen += 1
                if seen > max_files:
                    return _ranked(out)
                stem, ext = os.path.splitext(fn)
                if ext.lower() not in _ICO_EXTS:
                    continue
                low = fn.lower()
                if any(low.startswith(j) for j in _JUNK_STEMS):
                    continue
                score = 0
                for t in toks:
                    if stem.lower() == t:
                        score += 100
                    elif len(t) >= 3 and (stem.lower().startswith(t)
                                          or t in stem.lower()):
                        score += 40
                if not score:
                    continue
                try:
                    size = os.path.getsize(os.path.join(dirpath, fn))
                except OSError:
                    size = 0
                out.append((score, size, os.path.join(dirpath, fn)))
    except OSError:
        return _ranked(out)
    return _ranked(out)


def _ranked(items: list[tuple[int, int, str]]) -> list[str]:
    items.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [p for _s, _z, p in items[:2]]


def _shortcut_roots() -> list[str]:
    """Where users' app shortcuts live (Start Menu trees + Desktops)."""
    roots = []
    for env, sub in (
            ("ProgramData", r"Microsoft\Windows\Start Menu\Programs"),
            ("APPDATA", r"Microsoft\Windows\Start Menu\Programs"),
            ("USERPROFILE", "Desktop"),
            ("PUBLIC", "Desktop"),
    ):
        base = os.environ.get(env)
        if base:
            p = os.path.join(base, sub.replace("\\", os.sep))
            if os.path.isdir(p):
                roots.append(p)
    return roots


def _common_roots() -> list[str]:
    """Well-known install roots scanned as the LAST local strategy."""
    if os.name != "nt":
        return []  # dev/tests: monkeypatch this to inject a fake tree
    roots = []
    for env in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData"):
        p = os.environ.get(env)
        if p and os.path.isdir(p):
            roots.append(p)
    return roots


# ---------------------------------------------------------------------------
# .lnk (shell shortcut) parsing - MS-SHLLINK, pure bytes, no COM needed.
# ---------------------------------------------------------------------------

_LNK_CLSID = bytes((0x01, 0x14, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46))
_SIG_ICON_ENV = 0xA0000005


def _lnk_strings(data: bytes) -> dict:
    """Parse one .lnk's strings: target path + icon location (pure function).

    Returns {'target': str, 'icon': str} (either may be ''). Handles the
    ANSI and Unicode string variants, the LinkInfo LocalBasePath (incl. the
    unicode ex-header offset) and the IconEnvironmentDataBlock (icon paths
    stored as '%var%\\...'). Never raises.
    """
    out = {"target": "", "icon": ""}
    try:
        if len(data) < 0x4C or data[4:20] != _LNK_CLSID:
            return out
        flags = int.from_bytes(data[0x14:0x18], "little")
        is_uni = bool(flags & 0x80)

        def u16(off: int) -> int:
            return int.from_bytes(data[off:off + 2], "little")

        def u32(buf: bytes, off: int) -> int:
            return int.from_bytes(buf[off:off + 4], "little")

        def zstr(buf: bytes, off: int, uni: bool) -> str:
            if uni:
                end = off
                while end + 2 <= len(buf):
                    if buf[end] == 0 and buf[end + 1] == 0:
                        break
                    end += 2
                return buf[off:end].decode("utf-16-le", "replace")
            end = off
            while end < len(buf) and buf[end] != 0:
                end += 1
            return buf[off:end].decode("cp1252", "replace")

        off = 0x4C
        if flags & 0x1:                       # HasLinkTargetIDList
            if off + 2 > len(data):
                return out
            off += 2 + u16(off)
        if flags & 0x2:                       # HasLinkInfo
            if off + 4 > len(data):
                return out
            li_size = u32(data, off)
            li = data[off:off + max(4, li_size)]
            if len(li) >= 0x18 and (u32(li, 8) & 0x1):
                lbp = u32(li, 0x10)
                hsize = u32(li, 4)
                lbpw = u32(li, 0x1C) if (hsize >= 0x24 and len(li) >= 0x20) else 0
                if lbpw and lbpw < len(li):
                    out["target"] = zstr(li, lbpw, True)
                if not out["target"] and 0x14 <= lbp < len(li):
                    out["target"] = zstr(li, lbp, False)
            off += max(4, li_size)

        def read_string() -> str:
            nonlocal off
            if off + 2 > len(data):
                return ""
            n = u16(off)
            off += 2
            if n <= 0:
                return ""
            if is_uni:
                raw = data[off:off + n * 2]
                off += n * 2
                return raw.decode("utf-16-le", "replace").rstrip("\x00")
            raw = data[off:off + n]
            off += n
            return raw.decode("cp1252", "replace").rstrip("\x00")

        if flags & 0x4:                       # HasName (title)
            read_string()
        if flags & 0x8:                       # HasRelativePath
            read_string()
        if flags & 0x10:                      # HasWorkingDir
            read_string()
        if flags & 0x20:                      # HasArguments
            read_string()
        if flags & 0x40:                      # HasIconLocation
            out["icon"] = read_string()

        # Extra data blocks: IconEnvironmentDataBlock carries the icon path
        # when the shortcut stored it as '%var%\...'.
        if not out["icon"]:
            while off + 8 <= len(data):
                bsize = u32(data, off)
                if bsize < 8 or off + bsize > len(data):
                    break
                sig = u32(data, off + 4)
                if sig == _SIG_ICON_ENV:
                    env = data[off + 8:off + 8 + 520]
                    out["icon"] = env.decode("utf-16-le", "replace")\
                        .split("\x00")[0]
                    break
                off += bsize
    except Exception:
        return out
    return out


# Lazy per-process index of the user's shortcuts.
_sc_index: list[tuple[frozenset, str]] | None = None
_sc_index_bad = False


def _shortcut_index() -> list[tuple[frozenset, str]]:
    """(distinctive stem tokens, .lnk path) for every shortcut on disk.

    Built once per process, bounded (5000 files), never raises.
    """
    global _sc_index, _sc_index_bad
    if _sc_index is not None or _sc_index_bad:
        return _sc_index or []
    _sc_index_bad = True
    index: list[tuple[frozenset, str]] = []
    try:
        seen = 0
        for root in _shortcut_roots():
            base_depth = os.path.normpath(root).rstrip("\\/")\
                .count(os.sep)
            for dirpath, dirnames, filenames in os.walk(root):
                depth = os.path.normpath(dirpath).rstrip("\\/")\
                    .count(os.sep) - base_depth
                if depth >= 5:
                    dirnames[:] = []
                for fn in filenames:
                    seen += 1
                    if seen > 5000:
                        _sc_index_bad = False
                        _sc_index = index
                        return index
                    if not fn.lower().endswith(".lnk"):
                        continue
                    stem = fn[:-4]
                    toks = frozenset(_tokens(stem))
                    if toks:
                        index.append((toks, os.path.join(dirpath, fn)))
    except OSError:
        pass
    _sc_index_bad = False
    _sc_index = index
    return index


def _lnk_candidates(app_name: str) -> list[str]:
    """Icon source paths from shortcuts whose name matches the app."""
    toks = _tokens(app_name)
    if not toks:
        return []
    want = set(toks[:4])
    exact = (app_name or "").strip().lower()
    matches: list[tuple[int, int, str]] = []
    for stoks, path in _shortcut_index():
        hit = want & set(stoks)
        if hit != want:
            continue
        stem = os.path.splitext(os.path.basename(path))[0].lower()
        exact_first = 1 if stem == exact else 0
        matches.append((exact_first, len(hit), path))
    matches.sort(reverse=True)

    from ..core.installed_apps import parse_display_icon

    out: list[str] = []
    for _e, _h, path in matches[:3]:
        try:
            with open(path, "rb") as f:
                data = f.read(65536)
        except OSError:
            continue
        parsed = _lnk_strings(data)
        for raw in (parsed.get("icon", ""), parsed.get("target", "")):
            p, _idx = parse_display_icon(raw)
            if p and os.path.splitext(p)[1].lower() in (".exe", ".dll",
                                                        ".ico", ".png"):
                if p not in out and os.path.isfile(p):
                    out.append(p)
    return out


def icon_candidates(app) -> list[str]:
    """Every plausible LOCAL icon source for one app, best first.

    Pure discovery (path logic + reads); callers extract/cache per path.
    Never raises; may return [].
    """
    from ..core.installed_apps import parse_display_icon

    out: list[str] = []

    def add(p: str) -> None:
        if p and p not in out and os.path.isfile(p):
            out.append(p)

    name = getattr(app, "name", "") or ""
    toks = _tokens(name)

    # 1) the registry's own pointer
    disp, _idx = parse_display_icon(getattr(app, "icon_source", "") or "")
    if disp and os.path.splitext(disp)[1].lower() in (".exe", ".dll",
                                                      ".ico", ".png"):
        add(disp)

    # 2) Start-Menu / Desktop shortcuts (what the user actually clicks)
    for p in _lnk_candidates(name):
        add(p)

    # 3) the registered install folder
    roots: list[str] = []
    iloc = (getattr(app, "install_location", "") or "").strip()
    if iloc and os.path.isdir(iloc):
        roots.append(iloc)
    # a DisplayIcon pointing at a DIRECTORY is an install folder too
    if disp and os.path.isdir(disp):
        roots.append(disp)
    for root in roots[:2]:
        for p in _best_in_dir(root, toks):
            add(p)

    # 4) well-known roots: a folder named after the app
    if toks and len(out) < 1:
        for base in _common_roots():
            try:
                entries = os.listdir(base)
            except OSError:
                continue
            scored: list[tuple[int, int, str]] = []
            for d in entries:
                dlow = d.lower()
                if not os.path.isdir(os.path.join(base, d)):
                    continue
                overlap = sum(1 for t in toks[:4]
                              if dlow == t or dlow.startswith(t)
                              or (len(t) >= 4 and t in dlow))
                if overlap:
                    scored.append((overlap, -len(d), d))
            scored.sort(reverse=True)
            for _o, _l, d in scored[:2]:
                for p in _best_in_dir(os.path.join(base, d), toks,
                                      max_depth=3, max_files=800):
                    add(p)
            if len(out) >= 2:
                break
    return out[:10]


def _png_for_path(path: str) -> bytes:
    """Cache-first shell extraction for ONE icon source path."""
    cache = cached_icon_file(path)
    try:
        with open(cache, "rb") as f:
            data = f.read()
        if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) > 100:
            return data
    except OSError:
        pass
    png = extract_icon_png(path)
    if png:
        try:
            os.makedirs(icons_dir(), exist_ok=True)
            tmp = cache + f".tmp{os.getpid()}"
            with open(tmp, "wb") as f:
                f.write(png)
            os.replace(tmp, cache)
            prune_cache()
        except OSError:
            pass
        return png
    return b""


# ---------------------------------------------------------------------------
# Tier 2: UniGetUI community icon database (last resort, opt-in)
# ---------------------------------------------------------------------------

_ICON_DB_URLS = (
    "https://raw.githubusercontent.com/marticliment/UniGetUI/main/"
    "WebBasedData/screenshot-database-v2.json",
    "https://cdn.jsdelivr.net/gh/marticliment/UniGetUI@main/"
    "WebBasedData/screenshot-database-v2.json",
)
_DB_TTL = 7 * 24 * 3600.0
_MAX_ICON_BYTES = 768 * 1024
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
       "Safari/537.36 SoftDownloader/2.0")

_online: dict = {"db": None, "tried": False}


def reset_online_state() -> None:
    """Give a new IconWorker run one fresh shot at the icon database."""
    _online["db"] = None
    _online["tried"] = False


def _offline_env() -> bool:
    return bool(os.environ.get("SOFTUPDATER_OFFLINE_ICONS"))


def _db_cache_path() -> str:
    return os.path.join(icons_dir(), "unigetui-icon-db.json")


def _parse_icon_db(raw: bytes) -> dict:
    """'{...}' bytes -> {slug_lower: {'icon': url}} (pure, testable)."""
    import json

    try:
        d = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return {}
    db = d.get("icons_and_screenshots") if isinstance(d, dict) else None
    if not isinstance(db, dict) or not db:
        return {}
    return {str(k).lower(): v for k, v in db.items()
            if isinstance(v, dict)}


def _http_get_bytes(url: str, timeout) -> bytes:
    """One GET returning the body bytes; raises on any failure (seam for
    tests; also keeps the network code in exactly one place)."""
    import requests

    r = requests.get(url, timeout=timeout, headers={"User-Agent": _UA},
                     allow_redirects=True)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}")
    return r.content


def _load_icon_db() -> dict:
    """The slug -> icon-URL database: memory -> 7-day disk cache -> download.

    One download attempt per worker run (never per app!) and two official
    mirrors of UniGetUI's database (raw.githubusercontent + jsdelivr).
    """
    if _online["tried"]:
        return _online["db"] or {}
    _online["tried"] = True
    path = _db_cache_path()
    try:
        if time.time() - os.path.getmtime(path) < _DB_TTL:
            with open(path, "rb") as f:
                raw = f.read()
            if len(raw) > 100000:
                _online["db"] = _parse_icon_db(raw)
                return _online["db"] or {}
    except (OSError, ValueError):
        pass
    for url in _ICON_DB_URLS:
        try:
            raw = _http_get_bytes(url, timeout=(5, 20))
            if not raw.startswith(b"{") or len(raw) < 100000:
                continue
            db = _parse_icon_db(raw)
            if db:
                _online["db"] = db
                try:
                    os.makedirs(icons_dir(), exist_ok=True)
                    tmp = path + f".tmp{os.getpid()}"
                    with open(tmp, "wb") as f:
                        f.write(raw)
                    os.replace(tmp, path)
                except OSError:
                    pass
                break
        except Exception:
            continue
    return _online["db"] or {}


def slug_candidates(name: str) -> list[str]:
    """Possible database slugs for an app name, best first (pure function).

    'Google Chrome' -> ['googlechrome', 'google', 'chrome'],
    'LAV Filters 0.78' -> ['lavfilters', 'lav', 'filters'], ...
    """
    raw = [t for t in re.split(r"[^a-z0-9]+", (name or "").lower()) if t]
    distinct = [t for t in raw
                if t not in _GENERIC_TOKENS and not t.isdigit()]
    out: list[str] = []

    def add(s: str) -> None:
        if len(s) >= 2 and s not in out:
            out.append(s)

    add("".join(raw))            # 'googlechrome' style
    add("".join(distinct))       # 'lavfilters' style
    for t in distinct[:4]:
        add(t)                   # single distinctive token ('vlc')
    return out[:6]


def _is_image(head: bytes) -> bool:
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    if head[:4] == b"\x00\x00\x01\x00":          # ICO
        return True
    if head[:3] == b"\xff\xd8\xff":              # JPEG
        return True
    if head[:6] in (b"GIF87a", b"GIF89a"):       # GIF
        return True
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return True
    return False


def _web_image_png(url: str) -> bytes:
    """Download (once, disk-cached, magic-validated) one remote icon image."""
    os.makedirs(_web_icons_dir(), exist_ok=True)
    cache = os.path.join(_web_icons_dir(),
                         hashlib.sha1(url.encode()).hexdigest()[:16] + ".img")
    try:
        with open(cache, "rb") as f:
            data = f.read(4096)
        if len(data) > 100 and _is_image(data[:16]):
            with open(cache, "rb") as f:
                return f.read(_MAX_ICON_BYTES)
    except OSError:
        pass
    try:
        raw = _http_get_bytes(url, timeout=(5, 15))
    except Exception:
        return b""
    if not raw or len(raw) > _MAX_ICON_BYTES or not _is_image(raw[:16]):
        return b""
    try:
        tmp = cache + f".tmp{os.getpid()}"
        with open(tmp, "wb") as f:
            f.write(raw)
        os.replace(tmp, cache)
        _prune_web_cache()
    except OSError:
        pass
    return raw


def _prune_web_cache(max_files: int = 500) -> None:
    try:
        d = _web_icons_dir()
        entries = []
        for name in os.listdir(d):
            if name.endswith(".img"):
                full = os.path.join(d, name)
                try:
                    entries.append((os.stat(full).st_mtime, full))
                except OSError:
                    continue
        if len(entries) <= max_files:
            return
        entries.sort()
        for _m, full in entries[:len(entries) - max_files]:
            try:
                os.remove(full)
            except OSError:
                pass
    except OSError:
        pass


def _online_icon_png(name: str) -> bytes:
    """Tier 2: look the app up in UniGetUI's icon database and fetch it."""
    db = _load_icon_db()
    if not db:
        return b""
    url = ""
    for slug in slug_candidates(name):
        entry = db.get(slug)
        u = (entry or {}).get("icon") or ""
        u = str(u).strip()
        if u.startswith("http://") or u.startswith("https://"):
            url = u
            break
    if not url:
        return b""
    return _web_image_png(url)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def icon_png_for_app(app, allow_online: bool = False) -> bytes:
    """The PNG bytes shown for one installed app.

    Offline-first: local candidates (cache -> shell extraction), then - only
    when the caller explicitly opted in - the UniGetUI icon database, then
    the themed letter tile. Never raises; never returns empty when Qt is
    available.
    """
    tile = letter_tile_png(getattr(app, "name", "") or "?")
    try:
        for path in icon_candidates(app):
            png = _png_for_path(path)
            if png:
                return png
        if allow_online and not _offline_env():
            png = _online_icon_png(getattr(app, "name", "") or "")
            if png:
                return png
    except Exception:
        pass
    return tile


def prune_cache(max_files: int = 1000) -> None:
    """Keep the icon cache bounded - delete the oldest PNGs beyond the cap."""
    try:
        d = icons_dir()
        entries = []
        for name in os.listdir(d):
            if name.endswith(".png"):
                full = os.path.join(d, name)
                try:
                    entries.append((os.stat(full).st_mtime, full))
                except OSError:
                    continue
        if len(entries) <= max_files:
            return
        entries.sort()
        for _mtime, full in entries[:len(entries) - max_files]:
            try:
                os.remove(full)
            except OSError:
                pass
    except OSError:
        pass
