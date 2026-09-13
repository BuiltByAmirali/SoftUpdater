"""Enumerate installed applications from the Windows registry.

Games and game-only components are filtered out so the app lists real
applications only.

Non-Windows environments get an empty list plus one demo entry so the UI
can still be previewed during development.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from .win_info import is_windows

_UNINSTALL_KEYS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",  # HKCU handled below
]

_SKIP_PREFIXES = ("KB", "KB0", "Update for Microsoft", "Security Update",
                  "Update for (KB", "Update for (")
_SKIP_PREFIXES_LOWER = tuple(p.lower() for p in _SKIP_PREFIXES)


def _is_update_entry(name: str) -> bool:
    """True for hotfix/update entries (KB958488, 'Update for  (KB2504637)').

    The registry sometimes stores double spaces ('Update for  (KB...)'), so
    the comparison runs on whitespace-normalized, lowercased text.
    """
    compact = " ".join((name or "").split()).lower()
    return compact.startswith(_SKIP_PREFIXES_LOWER)

# ---------------------------------------------------------------------------
# Game filtering: the user asked for games NOT to be listed as applications.
# ---------------------------------------------------------------------------
_GAME_NAME_KEYWORDS = (
    # repack / release-scene markers
    "repack", "elamigos", "fitgirl", "online-fix", "online fix", "xatab",
    "skidrow", "gamefarsi", "par30game", "steamrip",
    # popular titles (word-boundary or substring matched)
    "red dead redemption", "grand theft auto", "gta", "gtav", "battlefield",
    "manor lords", "call of duty", "assassin's creed", "assassins creed",
    "cyberpunk 2077", "witcher", "elden ring", "hogwarts legacy",
    "baldur's gate", "baldurs gate", "starfield", "fallout",
    "elder scrolls", "skyrim", "need for speed", "forza", "efootball",
    "fifa", "pes", "ea sports fc", "world of warcraft", "mortal kombat",
    "street fighter", "resident evil", "silent hill", "tekken",
    "farming simulator", "truck simulator", "wwe 2", "ufc 2", "nba 2k",
    "horizon zero dawn", "days gone", "death stranding", "spider-man",
    "spider man", "marvel", "uncharted", "the last of us",
    "ghost of tsushima", "god of war", "it takes two", "a way out",
    "stray", "minecraft",
    # game-only runtime components
    "denuvo", "epic online services", "playstation pc sdk",
    "easy anti-cheat", "easyanticheat", "battleye", "punkbuster",
    "anti-cheat", "anticheat",
)

_GAME_PUBLISHER_KEYWORDS = (
    "gog.com", "dodi-repacks", "dodi repacks", "fitgirl", "elamigos",
    "par30game", "straygamefarsi", "gamefarsi", "online-fix",
    "rockstar games", "playstation publishing", "playstation mobile",
    "battlefield studios", "electronic arts", "ea sports", "ea games",
    "ea digital illusion", "ubisoft", "activision", "blizzard",
    "bethesda", "bandai namco", "namco", "square enix", "capcom", "sega",
    "konami", "2k games", "2k sports", "visual concepts", "warner bros",
    "cd projekt", "fromsoftware", "deep silver", "505 games",
    "focus entertainment", "focus home", "devolver", "private division",
    "team17", "thq nordic", "neowiz", "riot games", "paradox interactive",
    "codemasters", "nintendo", "gameforge", "wargaming", "gaijin",
    "atlus", "koei tecmo", "arc system", "team cherry", "concernedape",
)

# Store-front launchers are real apps, not games - never hide them.
_LAUNCHER_KEEP = (
    "steam", "gog galaxy", "epic games launcher", "ea app", "ea desktop",
    "origin", "ubisoft connect", "ubisoft game launcher", "battle.net",
    "riot client", "curseforge", "playnite", "heroic", "vortex",
)


def _keyword_hit(low: str, kw: str) -> bool:
    """Substring for long/compound keywords, word-boundary for short ones."""
    if " " in kw or "-" in kw or "'" in kw or len(kw) >= 6:
        return kw in low
    return re.search(rf"\b{re.escape(kw)}\b", low) is not None


def _is_game(name: str, publisher: str = "", key: str = "",
             install_location: str = "") -> bool:
    low = " ".join(re.sub(r"\([^)]*\)", " ", (name or "").lower()).split())
    # Unambiguous game signals come FIRST - they must win over the
    # launcher whitelist (e.g. "Steam App 1234567" contains "steam").
    if key and key.startswith("Steam App "):
        return True
    if low.startswith("steam app"):
        return True
    loc = (install_location or "").lower()
    if "steamapps" in loc or "gog games" in loc or "gog galaxy" in loc:
        return True
    # Store-front launchers are real apps, not games - never hide them.
    if any(k in low for k in _LAUNCHER_KEEP):
        return False
    if any(_keyword_hit(low, k) for k in _GAME_NAME_KEYWORDS):
        return True
    pub = (publisher or "").lower()
    return any(k in pub for k in _GAME_PUBLISHER_KEYWORDS)


@dataclass
class InstalledApp:
    name: str
    version: str = ""
    publisher: str = ""
    install_location: str = ""
    url_about: str = ""
    system_component: bool = False
    hive: str = ""  # HKLM64 / HKLM32 / HKCU
    key: str = field(default="", repr=False)
    icon_source: str = ""  # registry DisplayIcon value (exe/ico/dll + ",index")

    @property
    def display_version(self) -> str:
        return self.version.strip() if self.version else "-"


def _iter_registry_apps() -> list[InstalledApp]:
    import winreg  # noqa: WPS433

    found: dict[tuple, InstalledApp] = {}
    hives = [
        ("HKLM64", winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
        ("HKLM32", winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
        ("HKCU", winreg.HKEY_CURRENT_USER, 0),
    ]
    for hive_name, hive, wow in hives:
        base = _UNINSTALL_KEYS[0] if hive_name != "HKLM32" else _UNINSTALL_KEYS[1]
        try:
            root = winreg.OpenKey(hive, base, 0, winreg.KEY_READ | wow)
        except OSError:
            continue
        with root:
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(root, index)
                except OSError:
                    break
                index += 1
                try:
                    with winreg.OpenKey(root, subkey_name) as sub:
                        get = _value_getter(sub)
                        name = get("DisplayName")
                        if not name:
                            continue
                        name = str(name).strip()
                        if not name:
                            continue
                        if _is_update_entry(name):
                            continue
                        syscomp = bool(get("SystemComponent", 0))
                        if syscomp:
                            continue
                        version = str(get("DisplayVersion", "") or "")
                        publisher = str(get("Publisher", "") or "")
                        install_location = str(get("InstallLocation", "") or "")
                        icon_source = str(get("DisplayIcon", "") or "")
                        if _is_game(name, publisher=publisher, key=subkey_name,
                                    install_location=install_location):
                            continue
                        app = InstalledApp(
                            name=name,
                            version=version,
                            publisher=publisher,
                            install_location=install_location,
                            url_about=str(get("URLInfoAbout", "") or ""),
                            system_component=False,
                            hive=hive_name,
                            key=subkey_name,
                            icon_source=icon_source,
                        )
                        found[(app.name.lower(), app.version)] = app
                except OSError:
                    continue
    return list(found.values())


def _value_getter(key):
    import winreg  # noqa: WPS433

    def get(name: str, default=None):
        try:
            value, _ = winreg.QueryValueEx(key, name)
            return value
        except OSError:
            return default

    return get


def parse_display_icon(value: str) -> tuple[str, int]:
    """Split a registry DisplayIcon value into (icon_path, index).

    The value can look like:
      * "C:\\Program Files\\App\\app.exe"              -> (path, 0)
      * "C:\\...\\app.exe,0" / "...,12"                -> (path, 12)
      * "\"C:\\Program Files\\App\\app.exe,0""  (quoted) -> (path, 0)
      * "%ProgramFiles%\\App\\app.exe,-3" (env vars)   -> expanded
      * "C:\\...\\icon.ico" / "...\\resources.dll,1"   -> kept as-is
    Anything without a file extension (bare dirs, URLs, empty) -> ("", 0).
    Pure string parsing - no disk access, safe to unit-test anywhere.
    """
    s = (value or "").strip()
    if not s:
        return "", 0
    # Windows-style %VAR% expansion first (os.path.expandvars below only
    # understands $VAR / ${VAR}); undefined vars stay literal.
    s = re.sub(r"%([A-Za-z_][A-Za-z0-9_]*)%",
               lambda m: os.environ.get(m.group(1), m.group(0)), s)
    s = os.path.expandvars(s)
    # Strip surrounding quotes (keep the ,index inside the quotes intact).
    if len(s) >= 2 and s[0] == s[-1] == '"':
        s = s[1:-1].strip()
    index = 0
    # The index is a comma SUFFIX only when the comma is not part of the
    # path (Windows paths may contain commas, so split on the LAST one and
    # only when what follows is a small integer).
    head, sep, tail = s.rpartition(",")
    if sep and tail.strip().lstrip("-").isdigit():
        try:
            index = max(0, int(tail.strip()))
            s = head.strip()
        except ValueError:
            pass
    s = s.strip('"').strip()
    if not s or "://" in s or not os.path.splitext(s)[1]:
        return "", 0
    return s, index


def list_installed_apps() -> list[InstalledApp]:
    """Return sorted list of installed applications."""
    if is_windows():
        apps = _iter_registry_apps()
    else:
        # Development preview (non-Windows): provide a few sample entries
        demo = [
            ("7-Zip 24.08 (x64)", "24.08", "Igor Pavlov"),
            ("VLC media player", "3.0.20", "VideoLAN"),
            ("Notepad++ (64-bit x64)", "8.6.9", "Notepad++ team"),
            ("Google Chrome", "126.0.6478.127", "Google LLC"),
            ("Mozilla Firefox (x64 en-US)", "127.0.2", "Mozilla"),
            ("OBS Studio", "30.1.2", "OBS Project"),
            ("qBittorrent 4.6.5", "4.6.5", "The qBittorrent project"),
            ("WinRAR 7.01 (64-bit)", "7.01.0", "win.rar GmbH"),
            ("Spotify", "1.2.41.434", "Spotify AB"),
            ("Krita 5.2.2", "5.2.2", "KDE"),
        ]
        apps = [InstalledApp(name=n, version=v, publisher=p, hive="DEMO") for n, v, p in demo]
    apps.sort(key=lambda a: a.name.lower())
    return apps


# ---------------------------------------------------------------------------
# Fresh-version matching.
#
# After the user installs a downloaded update, the row's stored version is
# stale. These helpers re-match an app against a NEW registry scan so a
# single-app re-check compares the ACTUAL installed version - the row then
# honestly shows "Up to date" without re-checking the whole list.
#
# BUG FIX (screenshot regression): normalize_name() strips years, versions,
# architectures and words like "redistributable"/"runtime" BY DESIGN (it
# exists for catalog fuzzy matching). That made ALL "Microsoft Visual C++"
# entries from every year collide into a handful of normalized buckets
# ("microsoft visual c++", "microsoft visual c++ minimum", ...). The old
# matcher then picked the HIGHEST version in the bucket, so VC++ 2005/2008/
# 2010/2012 rows were "refreshed" to the VC++ 2015-2022 version
# (14.44.35211.0). The checker then honestly concluded "installed is newer
# than the manifest latest" and the UI showed a LATEST version lower than
# the installed one. The fix mirrors how winget/UniGetUI correlate installed
# packages: registry-key IDENTITY first, strict display-name disambiguation
# second, and a refusal to guess when the result would be ambiguous.
# ---------------------------------------------------------------------------

_YEAR_RE = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")
_VER_IN_NAME_RE = re.compile(r"\bv?\d+(?:\.\d+)+")
_ARCH64_TOKENS = ("x64", "win64", "amd64", "64-bit", "64bit", "x86_64")
_ARCH86_TOKENS = ("x86", "win32", "ia32", "i386", "i686", "32-bit", "32bit")


def _name_signature(name: str) -> tuple[frozenset, frozenset, str]:
    """Discriminating features of a RAW display name: (years, versions, arch).

    Extracted from the raw name (NOT the normalized one) because these tokens
    are exactly what normalize_name() throws away - and they are what keeps
    'Visual C++ 2005 x86' from being confused with 'Visual C++ 2015-2022 x64'.
    """
    low = " ".join((name or "").lower().split())
    years = frozenset(_YEAR_RE.findall(low))
    vers = frozenset(v.lstrip("v") for v in _VER_IN_NAME_RE.findall(low))
    if any(t in low for t in _ARCH64_TOKENS):
        arch = "x64"
    elif any(t in low for t in _ARCH86_TOKENS):
        arch = "x86"
    else:
        arch = ""
    return years, vers, arch


class FreshIndex:
    """Result of one fresh registry scan, indexed two ways.

    by_key  : (hive, registry subkey) -> InstalledApp. The STABLE identity
              anchor - the same trick winget uses (ARP ProductCode). After a
              normal update the SAME registry key remains with a new
              DisplayVersion, so identity is preserved across versions.
    by_name : normalized display name -> [InstalledApp]. Fallback for the
              rare case the old registry key vanished (major upgrade with a
              new ProductCode). Never trusted on its own - see
              match_fresh_version for the strict disambiguation rules.
    """

    __slots__ = ("by_key", "by_name")

    def __init__(self) -> None:
        self.by_key: dict[tuple[str, str], "InstalledApp"] = {}
        self.by_name: dict[str, list["InstalledApp"]] = {}


def build_fresh_index() -> FreshIndex:
    """One registry scan, indexed by registry-key identity + normalized name.

    Runs in the check worker thread (never the UI thread). Returns an EMPTY
    FreshIndex if the scan fails for any reason - callers then keep the
    stored versions.
    """
    from .version_utils import normalize_name

    index = FreshIndex()
    try:
        for app in list_installed_apps():
            norm = normalize_name(app.name)
            if norm:
                index.by_name.setdefault(norm, []).append(app)
            if app.key:
                index.by_key[(app.hive, app.key)] = app
    except Exception:
        return FreshIndex()
    return index


def match_fresh_version(app: "InstalledApp", index) -> str:
    """The app's CURRENT installed version from a fresh scan, or "".

    Matching is deliberately conservative - updating the WRONG row is worse
    than not updating one:

      Stage 1 - registry-key identity: the same (hive, subkey) still exists
        -> its DisplayVersion is authoritative. This is the winget/UniGetUI
        correlation anchor and resolves virtually every real refresh.

      Stage 2 - the old key vanished (major upgrade): look at the
        normalized-name bucket, then
          a) refuse candidates whose 4-digit YEAR tokens differ
             (VC++ 2005 is never VC++ 2015-2022),
          b) refuse candidates whose architecture token differs
             (x86 and x64 runtimes coexist on one machine),
          c) among survivors prefer candidates whose display-name version
             equals the app's (legit updates usually keep it or the row is
             about to be renamed anyway),
          d) refresh ONLY when the survivors agree on ONE version; if two
             different versions survive, the bucket is ambiguous -> keep
             the stored version rather than guess.

      Legacy dict indexes ({normalized_name: [InstalledApp]}) from older
      callers/tests are still accepted (Stage 2 only).
    """
    from .version_utils import compare_versions, normalize_name

    stored = (app.version or "").strip()

    # ---- Stage 1: registry-key identity ---------------------------------
    if getattr(index, "by_key", None) is not None and app.key:
        twin = index.by_key.get((app.hive, app.key))
        if twin is not None:
            fresh = (twin.version or "").strip()
            if not fresh or fresh == stored:
                return ""
            return fresh

    # ---- Stage 2: normalized-name bucket, strictly disambiguated --------
    norm = normalize_name(app.name)
    if not norm:
        return ""
    if isinstance(index, FreshIndex):
        bucket = index.by_name.get(norm) or []
    elif isinstance(index, dict):                 # legacy shape (old tests)
        bucket = index.get(norm) or []
    else:
        return ""
    if not bucket:
        return ""

    a_years, a_vers, a_arch = _name_signature(app.name)
    survivors = []
    for cand in bucket:
        c_years, _c_vers, c_arch = _name_signature(cand.name)
        if a_years != c_years or a_arch != c_arch:
            continue
        survivors.append(cand)
    if not survivors:
        return ""

    if a_vers:                                    # prefer same name-version
        preferred = [c for c in survivors
                     if _name_signature(c.name)[1] == a_vers]
        if preferred:
            survivors = preferred

    versions = [(c.version or "").strip() for c in survivors]
    versions = [v for v in versions if v]
    if not versions:
        return ""
    first = versions[0]
    if any(compare_versions(v, first) != 0 for v in versions[1:]):
        return ""                                 # ambiguous -> refuse
    return "" if first == stored else first
