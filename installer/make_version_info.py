"""Generate a PyInstaller --version-file resource for SoftUpdater.

Usage:
    python make_version_info.py 1.2.3 [output_path]

Writes the standard Windows VSVersionInfo script (ASCII, CRLF) so the
built SoftUpdater.exe shows formal metadata in Explorer's Properties
dialog (product name, version, description, copyright).
"""
from __future__ import annotations

import datetime
import sys

TEMPLATE = """\
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={t},
    prodvers={t},
    mask=0x3F,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'BuiltByAmirali'),
        StringStruct('FileDescription',
                     'SoftUpdater - check installed apps against official sources'),
        StringStruct('FileVersion', '{v}'),
        StringStruct('InternalName', 'SoftUpdater'),
        StringStruct('LegalCopyright', 'Copyright (C) {y} BuiltByAmirali'),
        StringStruct('OriginalFilename', 'SoftUpdater.exe'),
        StringStruct('ProductName', 'SoftUpdater'),
        StringStruct('ProductVersion', '{v}')])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def main(argv: list[str]) -> int:
    if len(argv) < 2 or not argv[1].strip():
        print("usage: make_version_info.py VERSION [output_path]")
        return 2
    raw = argv[1].strip()
    parts = (raw.split(".") + ["0", "0", "0", "0"])[:4]
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        print(f"[ERROR] VERSION must be numeric dots like 1.2.3, got: {raw!r}")
        return 2
    ver = ".".join(str(n) for n in nums)
    out = argv[2] if len(argv) > 2 else "version_info.txt"
    text = TEMPLATE.format(t=tuple(nums), v=ver,
                           y=datetime.date.today().year)
    # Windows-native line endings so every tool (and Notepad) is happy.
    with open(out, "w", encoding="ascii", newline="\r\n") as fh:
        fh.write(text)
    print(f"version resource written: {out} (version {ver})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
