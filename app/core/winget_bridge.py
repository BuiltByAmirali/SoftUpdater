"""winget bridge - resolve installed-app names to winget package IDs.

This is the piece that pushes "Managed by vendor" rows down to the minimum:
UniGetUI finds updates for apps like Steam, Git, Notepad++ ... by asking the
winget CLI itself which catalog package corresponds to an installed program
(winget correlates registry ARP entries with microsoft/winget-pkgs). We adopt
the SAME technique:

  1. run  `winget list --accept-source-agreements --disable-interactivity`
     (read-only listing - winget is NEVER asked to install anything here);
  2. parse its output table the way UniGetUI's WinGetTableLayout does:
     locate the dashed separator line, compute the column START OFFSETS from
     the header line, and slice every data row at those offsets. Header
     captions are locale-dependent ("Name"/"名前"/"نام"...) but the column
     ORDER is not, so offset slicing works on every Windows language;
  3. keep rows whose Id column matches the winget ID grammar
     (dotted alphanumeric, e.g. "Git.Git", "Valve.Steam") plus the
     'Available' column - the version winget's OWN catalog source offers
     for that package (an instant, offline-ish update hint);
  4. cache the name->ID list in memory for the run and on disk for 24 h,
     so the CLI (which can take 5-30 s) runs at most once a day.

Two extra read-only helpers (both cached, both optional - every caller
degrades gracefully when winget is missing):
  * package_versions(id)   - `winget show --id X --versions`, the package's
    full version list without touching api.github.com;
  * search_by_name(name)   - `winget search --name X`, a conservative
    catalog lookup for apps the `winget list` correlation could not place.

The resulting package ID is then checked against the official winget-pkgs
manifest repository over HTTPS by update_checker._check_winget - the same
honest data path used for VC++/WebView2/.NET. If winget is missing, times
out, or returns nothing usable, every caller falls back to the previous
behaviour ("Managed by vendor" / "No source found") - nothing breaks.
"""

from __future__ import annotations
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time

from .version_utils import normalize_name
from .win_info import is_windows

_CACHE_TTL = 24 * 3600.0
_CLI_TIMEOUT = 150
_SHOW_TIMEOUT = 60          # `winget show` per call (versions / search)
_MAX_NAME_SEARCHES = 40     # per-process cap for the search fallback

# winget package Id grammar: dotted identifier, alnum/+._- segments, at
# least one letter (a bare "24.08" version never matches).
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+._\-]*$")

_version_re = re.compile(r"^v?\d+(\.\d+)+$")

_lock = threading.Lock()
_index: list[dict] | None = None      # parsed rows, kept for the process run
_index_ts: float = 0.0

_extras_lock = threading.Lock()
_versions_mem: dict[str, tuple[list[str], float]] = {}
_search_mem: dict[str, tuple[tuple[str, str], float]] = {}
_searches_done = 0


# --------------------------------------------------------------------- CLI
def cache_path() -> str:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = "/tmp"
    return os.path.join(base, "SoftUpdater", "winget_ids.json")


def extras_cache_path() -> str:
    """24h cache for the `winget show --versions` / `winget search` results
    (keeps repeat runs CLI-free)."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = "/tmp"
    return os.path.join(base, "SoftUpdater", "winget_extras.json")


def available() -> bool:
    """True when the winget CLI exists on PATH (read-only probe)."""
    if not is_windows():
        return False
    try:
        import shutil

        return shutil.which("winget") is not None
    except Exception:
        return False


def _creationflags() -> int:
    """CREATE_NO_WINDOW: no console flashes above the GUI on Windows."""
    if os.name == "nt":
        return 0x08000000  # subprocess.CREATE_NO_WINDOW
    return 0


def _run_winget(args: list[str], timeout: int = _CLI_TIMEOUT) -> str | None:
    """Run one read-only winget command, capture stdout or None on failure."""
    try:
        proc = subprocess.run(  # noqa: S603 - fixed argv, no shell
            args,
            capture_output=True, timeout=timeout,
            creationflags=_creationflags(),
        )
    except Exception:
        return None
    try:
        text = proc.stdout.decode("utf-8", errors="replace")
    except Exception:
        return None
    if not text:
        return None
    # A non-zero exit code with data still happens (e.g. msstore source
    # warnings); the table parser only accepts well-formed rows, so parse.
    return text


def _run_winget_list(timeout: int = _CLI_TIMEOUT) -> str | None:
    """Capture `winget list` output, or None on any failure."""
    return _run_winget(
        ["winget", "list",
         "--accept-source-agreements",
         "--disable-interactivity"],
        timeout=timeout,
    )


# ------------------------------------------------------------------ parser
def _is_separator(line: str) -> bool:
    """UniGetUI rule: a line of spaces and dashes (>=3 dashes) underlines
    the header row."""
    if not line or line.strip(" -") != "":
        return False
    return line.count("-") >= 3


def _column_starts(header: str) -> list[int]:
    """Offsets where a new column begins: a non-space character that follows
    a space run (exactly how UniGetUI derives the layout from the header)."""
    starts: list[int] = []
    prev_space = True
    for i, ch in enumerate(header.rstrip("\n")):
        if ch != " " and prev_space:
            starts.append(i)
        prev_space = ch == " "
    return starts


def parse_winget_table(text: str) -> list[dict]:
    """Parse `winget list` output into [{'name','id','version'}, ...].

    Pure function (no subprocess) so it is fully unit-testable. Rows whose
    Id cell does not match the winget ID grammar are dropped, which also
    skips footer/warning lines around the table.
    """
    rows_out: list[dict] = []
    if not text:
        return rows_out
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if _is_separator(lines[i]) and i > 0:
            header = lines[i - 1]
            starts = _column_starts(header)
            if len(starts) >= 3:  # Name | Id | Version [ | Available | Source]
                j = i + 1
                while j < len(lines) and lines[j].strip():
                    cells = _slice_row(lines[j], starts)
                    row = _row_from_cells(cells)
                    if row:
                        rows_out.append(row)
                    j += 1
                i = j
                continue
        i += 1
    return rows_out


def _slice_row(line: str, starts: list[int]) -> list[str]:
    """Slice one data row at the header-derived offsets. Long cell values
    (app names) bleed into the next column, so each cell also absorbs the
    gap up to where the next cell's content begins - handled by trimming:
    the Id/Version cells are single tokens, the Name takes everything left
    of the Id token start."""
    if not starts:
        return [line.strip()]
    cells: list[str] = []
    for k, start in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(line)
        cells.append(line[start:end].strip())
    return cells


def _row_from_cells(cells: list[str]) -> dict | None:
    """Validate one sliced row. The Id cell must be a winget ID; when long
    names overflowed their column the Name cell is re-stitched so the name
    keeps ALL its text (everything before the Id token). The 4th column
    ('Available') is kept when it holds a clean version - it is winget's own
    catalog hint that a different version exists."""
    if len(cells) < 3:
        return None
    name, pkg_id, version = cells[0], cells[1], cells[2]
    if not _ID_RE.match(pkg_id) or not any(c.isalpha() for c in pkg_id):
        return None
    if _version_re.match(pkg_id):
        return None  # that is a version, not an ID (locale-damaged row)
    available = ""
    if len(cells) > 3 and _version_re.match(cells[3].strip() or "-"):
        available = cells[3].strip()
    return {"name": name, "id": pkg_id, "version": version,
            "available": available}


# ------------------------------------------------------------------- cache
def _load_disk_cache() -> tuple[list[dict], float] | None:
    try:
        with open(cache_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        rows = data.get("rows")
        ts = float(data.get("ts", 0))
        if isinstance(rows, list) and ts > 0:
            cleaned = []
            for r in rows:
                if (isinstance(r, dict) and r.get("id") and r.get("name")
                        and _ID_RE.match(str(r["id"]))):
                    cleaned.append({"name": str(r["name"]),
                                    "id": str(r["id"]),
                                    "version": str(r.get("version", "")),
                                    "available": str(r.get("available", ""))})
            return cleaned, ts
    except Exception:
        pass
    return None


def _save_disk_cache(rows: list[dict]) -> None:
    try:
        path = cache_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "rows": rows}, f)
        os.replace(tmp, path)
    except Exception:
        pass


def _get_index(max_age: float = _CACHE_TTL, force_refresh: bool = False,
               timeout: int = _CLI_TIMEOUT) -> list[dict]:
    """The parsed winget rows: memory -> disk cache (24 h) -> CLI run."""
    global _index, _index_ts
    with _lock:
        if not force_refresh and _index is not None:
            return _index
        if not force_refresh:
            cached = _load_disk_cache()
            if cached and (time.time() - cached[1]) < max_age:
                _index, _index_ts = cached[0], cached[1]
                return _index
        rows: list[dict] = []
        if available():
            from . import applog

            applog.event("winget bridge: running 'winget list' to build the "
                         "name -> package ID map (cached for 24h)")
            text = _run_winget_list(timeout=timeout)
            if text:
                rows = parse_winget_table(text)
                if rows:
                    _save_disk_cache(rows)
            applog.event(f"winget bridge: {len(rows)} catalog rows resolved")
        _index, _index_ts = rows, time.time()
        return _index


def refresh() -> bool:
    """Force a fresh `winget list` run (used by tests / future UI hooks)."""
    if not available():
        return False
    return bool(_get_index(force_refresh=True))


def reset_for_tests() -> None:
    """Clear in-memory state (tests only)."""
    global _index, _index_ts, _versions_mem, _search_mem, _searches_done
    with _lock:
        _index, _index_ts = None, 0.0
    with _extras_lock:
        _versions_mem = {}
        _search_mem = {}
        _searches_done = 0


# ----------------------------------------------------------------- lookup
def _arch_token(name: str) -> str:
    low = (name or "").lower()
    if re.search(r"(?<!\d)x64|64-bit|64bit|amd64", low):
        return "x64"
    if re.search(r"(?i)\bx86\b|32-bit|32bit|win32", low):
        return "x86"
    return ""


def _id_arch(package_id: str) -> str:
    low = (package_id or "").lower()
    if low.endswith(".x64") or ".x64." in low:
        return "x64"
    if low.endswith(".x86") or ".x86." in low:
        return "x86"
    return ""


def _match(app_name: str, rows: list[dict]) -> tuple[str, str]:
    """Conservative (name -> package ID) matching shared by `winget list`
    correlation and catalog search. Returns (id, available-hint) or ("", "").

    Matching is deliberately conservative (a WRONG match is worse than no
    match - same rule as the fresh-version matcher):
      1. exact case-insensitive raw-name match wins;
      2. normalized-name match when it is UNIQUE, or ambiguous candidates
         are disambiguated by the x64/x86 token in the app name vs the ID;
      3. winget truncates very long names with '...' - a truncated row is
         accepted only when its visible part is a prefix of the app name,
         the app name is at least 10 chars long and the match is unique.
    """
    if not (app_name or "").strip() or not rows:
        return ("", "")
    raw = app_name.strip()
    raw_low = raw.casefold()

    # 1) exact raw name
    for row in rows:
        if row["name"].strip().casefold() == raw_low:
            return (row["id"], str(row.get("available", "")))

    norm = normalize_name(raw)
    if not norm:
        return ("", "")
    want_arch = _arch_token(raw)

    # 2) normalized match
    cands = [r for r in rows if normalize_name(r["name"]) == norm]
    if len(cands) > 1 and want_arch:
        arch_cands = [r for r in cands if _id_arch(r["id"]) == want_arch]
        if len(arch_cands) == 1:
            cands = arch_cands
    if len(cands) == 1:
        return (cands[0]["id"], str(cands[0].get("available", "")))

    # 3) truncated ('...') winget names - unique prefix only
    for row in rows:
        nm = row["name"].strip()
        if nm.endswith("...") or nm.endswith("\u2026"):
            visible = nm.rstrip(".").rstrip("\u2026").strip()
            visible = re.sub(r"[\s.\u2026]+$", "", visible)
            if (len(visible) >= 10 and raw_low.startswith(visible.casefold())):
                # count how many rows could match this prefix
                peers = [r2 for r2 in rows
                         if re.sub(r"[\s.\u2026]+$", "",
                                   r2["name"].strip()).casefold()
                         == visible.casefold()]
                if len(peers) == 1:
                    return (row["id"], str(row.get("available", "")))
    return ("", "")


def lookup(app_name: str, rows: list[dict] | None = None) -> str:
    """The winget package ID for an installed app, or ""."""
    if rows is None:
        rows = _get_index()
    return _match(app_name, rows or [])[0]


def lookup_with_hint(app_name: str,
                     rows: list[dict] | None = None) -> tuple[str, str]:
    """(package ID, winget's 'Available' version hint) for an installed app.
    The hint is non-empty only when the winget source publishes a clean
    version for the package - i.e. winget itself believes a different
    version exists in the catalog."""
    if rows is None:
        rows = _get_index()
    return _match(app_name, rows or [])


# ------------------------------------------------ winget show / search
def _load_extras() -> dict:
    try:
        with open(extras_cache_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_extras(data: dict) -> None:
    try:
        path = extras_cache_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, path)
    except Exception:
        pass


def _parse_versions_output(text: str | None) -> list[str]:
    """Version lines of `winget show --versions` output. Pure function.
    The header caption is locale-dependent but the version lines themselves
    are plain dotted numbers on every Windows language."""
    out: list[str] = []
    for line in (text or "").splitlines():
        s = line.strip().lower()
        if _version_re.match(s):
            out.append(s)
    return out


def package_versions(pkg_id: str, max_age: float = _CACHE_TTL) -> list[str]:
    """All published versions of a winget package (as printed). Sources, in
    order: memory -> 24h disk cache -> `winget show --id X --exact
    --versions` (read-only). [] when winget is missing or silent - callers
    fall back to the GitHub manifest listing."""
    pkg_id = (pkg_id or "").strip()
    if not pkg_id:
        return []
    now = time.time()
    with _extras_lock:
        hit = _versions_mem.get(pkg_id)
        if hit and (now - hit[1]) < max_age:
            return list(hit[0])
    extras = _load_extras()
    entry = (extras.get("versions") or {}).get(pkg_id)
    if isinstance(entry, dict):
        ts = float(entry.get("ts", 0) or 0)
        if (now - ts) < max_age:
            versions = [str(v) for v in entry.get("versions", [])
                        if _version_re.match(str(v))]
            with _extras_lock:
                _versions_mem[pkg_id] = (versions, ts)
            return list(versions)
    versions: list[str] = []
    if available():
        from . import applog

        applog.event(f"winget bridge: 'winget show --versions' for {pkg_id}")
        text = _run_winget(
            ["winget", "show", "--id", pkg_id, "--exact",
             "--accept-source-agreements", "--disable-interactivity",
             "--versions"],
            timeout=_SHOW_TIMEOUT,
        )
        versions = _parse_versions_output(text)
        if versions:
            extras.setdefault("versions", {})[pkg_id] = {
                "ts": time.time(), "versions": versions}
            _save_extras(extras)
    with _extras_lock:
        _versions_mem[pkg_id] = (versions, now)
    return list(versions)


def search_by_name(app_name: str, max_age: float = _CACHE_TTL) -> tuple[str, str]:
    """Conservative winget-catalog lookup by display name - the rescue path
    for apps whose `winget list` row carries no usable ID (a common shape
    for vendor-managed installs). Returns (package_id, catalog_version) or
    ("", ""); accepts ONLY exact / normalized-unique / unique-truncated
    matches (same matcher as lookup), so a wrong package can never be
    offered. Cached for 24 h and capped per process."""
    global _searches_done
    raw = (app_name or "").strip()
    if len(raw) < 3:
        return ("", "")
    key = raw.casefold()
    now = time.time()
    with _extras_lock:
        hit = _search_mem.get(key)
        if hit and (now - hit[1]) < max_age:
            return hit[0]
    extras = _load_extras()
    entry = (extras.get("searches") or {}).get(key)
    if isinstance(entry, dict):
        ts = float(entry.get("ts", 0) or 0)
        if (now - ts) < max_age:
            out = (str(entry.get("id", "")), str(entry.get("version", "")))
            with _extras_lock:
                _search_mem[key] = (out, ts)
            return out
    if not available():
        return ("", "")
    with _extras_lock:
        if _searches_done >= _MAX_NAME_SEARCHES:
            return ("", "")
        _searches_done += 1
    from . import applog

    applog.event(f"winget bridge: 'winget search --name' for {raw!r}")
    text = _run_winget(
        ["winget", "search", "--name", raw, "--source", "winget",
         "--accept-source-agreements", "--disable-interactivity"],
        timeout=_SHOW_TIMEOUT,
    )
    pkg_id, _hint = ("", "")
    rows = parse_winget_table(text or "")
    if rows:
        pkg_id, _hint = _match(raw, rows)
    version = ""
    if pkg_id:
        # search tables have Name|Id|Version|Match|Source - the catalog's
        # latest version is the Version column (the 4th column is the match
        # reason, not an Available version like in `winget list`).
        for r in rows:
            if r["id"] == pkg_id:
                version = str(r.get("version", "") or "")
                break
    if pkg_id:
        extras.setdefault("searches", {})[key] = {
            "ts": time.time(), "id": pkg_id, "version": version}
        _save_extras(extras)
    with _extras_lock:
        _search_mem[key] = ((pkg_id, version), time.time())
    return (pkg_id, version)
