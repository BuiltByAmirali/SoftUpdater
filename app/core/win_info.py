"""Windows version and bitness detection (English output, LTR-safe)."""
from __future__ import annotations

import os
import platform
import sys


def is_windows() -> bool:
    return sys.platform.startswith("win")


def os_bitness() -> int:
    """Return 64 or 32 - bitness of the OS (not of Python)."""
    if not is_windows():
        # Non-Windows dev environment fallback
        return 64 if platform.machine().endswith("64") else 32
    arch = os.environ.get("PROCESSOR_ARCHITEW6432") or os.environ.get("PROCESSOR_ARCHITECTURE", "")
    if arch.upper() in ("AMD64", "ARM64", "IA64"):
        return 64
    if platform.machine().endswith("64"):
        return 64
    return 32


def python_bitness() -> int:
    return 64 if sys.maxsize > 2**32 else 32


def _build_number() -> int:
    try:
        return int(platform.version().split(".")[-1])
    except Exception:
        return 0


_PRODUCT_PREFIXES = ("Windows 11", "Windows 10", "Windows Server",
                     "Windows NT", "Windows")


def _windows_base_name(major: int, minor: int, build: int,
                       product_type: int = 1) -> str:
    """Map OS version numbers to the friendly BASE name.

    Pure function (verifiable on any OS). The name comes from the BUILD
    NUMBER ONLY - never from the registry ProductName, which on Windows 11
    still reports "Windows 10 ..." (v1.1.2 bug). VER_NT_WORKSTATION == 1;
    product_type 2/3 are server / domain-controller products.
    """
    if product_type != 1:
        return "Windows Server"
    if major == 10:
        # Windows 11 kept major.minor at 10.0 - only the build number moved
        # (22000+ = 11), so the build number is the only reliable signal.
        return "Windows 11" if build >= 22000 else "Windows 10"
    if major == 6 and minor == 3:
        return "Windows 8.1"
    if major == 6 and minor == 2:
        return "Windows 8"
    if major == 6 and minor == 1:
        return "Windows 7"
    if major == 6 and minor == 0:
        return "Windows Vista"
    if major == 5 and minor == 2:
        return "Windows XP x64"
    if major == 5 and minor == 1:
        return "Windows XP"
    return f"Windows {major}.{minor}"


def _edition_suffix(product_name: str, base_name: str = "") -> str:
    """Extract the EDITION suffix from a registry ProductName.

    'Windows 10 Pro' -> 'Pro'; 'Windows 7 Ultimate' -> 'Ultimate';
    'Windows Server 2019 Standard' -> '2019 Standard'; '' when nothing
    usable remains. The detected BASE name is tried as the first prefix
    (so 'Windows 8.1 Pro' yields 'Pro', not a duplicated '8.1'); the
    known product prefixes follow, which is what makes the stale
    'Windows 10 ...' ProductName of Windows 11 harmless. Pure function,
    testable on any OS."""
    text = (product_name or "").strip()
    if not text:
        return ""
    for prefix in (base_name, *_PRODUCT_PREFIXES):
        if prefix and text.startswith(prefix):
            rest = text[len(prefix):].strip()
            # Sanity guard: a real edition suffix is short and plain text.
            if 0 < len(rest) <= 40 and "\n" not in rest and "\r" not in rest:
                return rest
            return ""
    return ""


def _registry_product_name() -> str:
    """HKLM ...\\CurrentVersion\\ProductName, or '' when unavailable.

    Prefers the 64-bit registry view so the 32-bit (Win7) build running on
    64-bit Windows reads the real value."""
    try:
        import winreg  # noqa: WPS433 (windows only)

        path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        try:
            flags = winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, flags)
        except OSError:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        with key:
            value, _ = winreg.QueryValueEx(key, "ProductName")
        return value if isinstance(value, str) else ""
    except Exception:
        return ""


def windows_edition_name() -> str:
    """Return friendly Windows name: 'Windows 11 Pro', 'Windows 10 Home',
    'Windows 7 Ultimate', 'Windows Server 2019 Standard', ...

    v1.1.3 bug fix: the base name ("Windows 11" / "Windows 10" / ...) is
    derived from the BUILD NUMBER ONLY. The old code overwrote it with the
    registry ProductName - and on Windows 11 that registry value still
    reads "Windows 10 Pro", so a Windows 11 machine displayed as
    "Windows 10 Pro". The registry is now used ONLY for the edition
    suffix ("Pro", "Home", ...), never for the base name."""
    if not is_windows():
        return "Non-Windows OS"
    try:
        ver = sys.getwindowsversion()  # type: ignore[attr-defined]
    except Exception:
        return "Windows (unknown)"
    build = int(getattr(ver, "build", 0) or _build_number())
    product_type = int(getattr(ver, "product_type", 1) or 1)
    name = _windows_base_name(ver.major, ver.minor, build, product_type)
    suffix = _edition_suffix(_registry_product_name(), name)
    if suffix and suffix.lower() not in name.lower():
        name = f"{name} {suffix}"
    return name


def windows_summary() -> str:
    """One-line summary shown in the UI, e.g. 'Windows 11 Pro - 64-bit - Build 22631'."""
    name = windows_edition_name()
    bits = "64-bit" if os_bitness() == 64 else "32-bit"
    if is_windows():
        build = _build_number()
        return f"{name} - {bits} - Build {build}" if build else f"{name} - {bits}"
    return f"{name} - {bits} - (dev preview)"


def windows_summary_l10n() -> str:
    """Same summary as windows_summary(), but through app.i18n.tr() in the
    CURRENT UI language (used by the main-window subtitle; logs keep the
    stable English version)."""
    from ..i18n import tr

    name = windows_edition_name()
    if name == "Non-Windows OS":
        name = tr("win.nonwin")
    elif name == "Windows (unknown)":
        name = tr("win.unknown")
    bits = tr("bits.64") if os_bitness() == 64 else tr("bits.32")
    if not is_windows():
        return tr("win.summary_dev", name=name, bits=bits)
    build = _build_number()
    if build:
        return tr("win.summary_build", name=name, bits=bits, build=build)
    return tr("win.summary_plain", name=name, bits=bits)


def arch_tag() -> str:
    return "x64" if os_bitness() == 64 else "x86"
