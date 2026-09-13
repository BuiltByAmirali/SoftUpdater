"""App-name normalization and version comparison helpers."""
from __future__ import annotations

import re
from functools import lru_cache

try:
    from packaging.version import InvalidVersion, Version

    _HAS_PACKAGING = True
except Exception:  # pragma: no cover - fallback when packaging missing
    _HAS_PACKAGING = False
    InvalidVersion = ValueError  # type: ignore[assignment,misc]

_NOISE_PATTERNS = [
    (re.compile(r"\(.*?\)"), " "),            # remove parenthesised chunks
    (re.compile(r"\b(x64|x86|win64|win32|64-bit|32-bit|64bit|32bit|amd64|i386|i686|arm64|arm)\b", re.I), " "),
    (re.compile(r"\bv?\d+(\.\d+)+\b"), " "),  # version numbers
    (re.compile(r"\b\d+\b"), " "),            # bare numbers
    (re.compile(r"\b(remove only|redistributable|runtime|package|setup|installer)\b", re.I), " "),
    (re.compile(r"[^\w+# ]"), " "),           # keep word chars, spaces, + and #
    (re.compile(r"\s+"), " "),
]


@lru_cache(maxsize=4096)
def normalize_name(name: str) -> str:
    """Normalize an installed-app display name for fuzzy matching."""
    s = (name or "").strip().lower()
    for pattern, repl in _NOISE_PATTERNS:
        s = pattern.sub(repl, s)
    return s.strip()


@lru_cache(maxsize=4096)
def _version_key(version: str):
    """Return a sortable key for a version string, or None if unparseable."""
    if not version:
        return None
    v = version.strip()
    if _HAS_PACKAGING:
        try:
            return Version(v)
        except InvalidVersion:
            pass
    m = re.findall(r"\d+", v)
    if not m:
        return None
    return tuple(int(x) for x in m)


def compare_versions(installed: str, latest: str) -> int:
    """Return -1 if installed < latest, 0 if equal, 1 if installed > latest.

    Returns 0 when both are empty/unknown. Falls back to plain string compare
    when numeric parsing fails on either side.
    """
    if not installed and not latest:
        return 0
    ki, kl = _version_key(installed or ""), _version_key(latest or "")
    if ki is not None and kl is not None:
        return -1 if ki < kl else (1 if ki > kl else 0)
    si, sl = (installed or "").strip(), (latest or "").strip()
    if si == sl:
        return 0
    return -1 if si < sl else 1


def is_newer(installed: str, latest: str) -> bool:
    return compare_versions(installed, latest) < 0


def prefix_equal(a: str, b: str) -> bool:
    """True when two version strings describe the SAME build, allowing
    trailing zero-padding / shorter component counts to differ.

    Rationale: VC++ Redistributable MSI entries write DisplayVersion values
    like "12.0.40664" while the official manifest publishes "12.0.40664.0" -
    the very same installer. Without this, those rows would forever show a
    phantom "update available" that never resolves (a classic winget bug).
    """
    ta = _numeric_tuple(a)
    tb = _numeric_tuple(b)
    if ta is None or tb is None:
        # no numbers on one side: fall back to a plain string comparison
        return (a or "").strip() == (b or "").strip()
    n = max(len(ta), len(tb))
    ta += (0,) * (n - len(ta))
    tb += (0,) * (n - len(tb))
    return ta == tb


def _numeric_tuple(version: str) -> tuple[int, ...] | None:
    nums = re.findall(r"\d+", version or "")
    if not nums:
        return None
    return tuple(int(x) for x in nums)
