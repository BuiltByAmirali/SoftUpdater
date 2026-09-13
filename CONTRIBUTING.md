# Contributing to SoftUpdater

Thank you for considering a contribution! Issues and pull requests in
**English or Persian** are both welcome.

## Development setup

1. Windows 10/11 (the app reads the Windows registry).
2. Python 3.10+ on PATH - or just double-click `run.bat`, which creates
   its own virtual environment and installs the dependencies.
3. Launch from source: `python run.py` (or `run.bat`).

## Before you open a PR

- **Run the offline test suite** (no GUI/network needed):

  ```
  python run.py --selftest
  python build/audit_tr_keys.py
  python build/audit_dynamic_keys.py
  ```

- **Both build lines must keep working.** The x64 line uses PySide6/Qt 6;
  the Windows 7 / 32-bit line runs the *same code* on PyQt5/Qt 5 through
  `app/qt_compat.py` (forced by `SOFTUPDATER_QT5=1`). Avoid Qt6-only APIs;
  use the scoped enums and `.exec()` spellings already used in the code.
- **New user-visible strings must be translated in all six languages**
  (`app/i18n/en.py` is the master; fa/ar are RTL). The audit scripts above
  fail the check if any `tr()` key or placeholder is missing anywhere.
- Keep the styling inside `app/ui/theme.py` (dark glassmorphism) - don't
  introduce per-widget hard-coded colors or external asset files; draw
  icons with `app/ui/ui_icons.py` instead.
- Stay dependency-light: everything user-facing should work offline.

## Reporting bugs

Open a GitHub issue and include: Windows version + bitness, Python
version (or installer version), steps to reproduce, and the log from
`%LOCALAPPDATA%\SoftUpdater\logs\softupdater.log` (remove anything you
consider private first). See `SECURITY.md` for security reports.

## Code style

Plain, explicit Python - type hints where they help, no clever tricks.
Follow the existing module layout (`app/core` = logic, `app/ui` = Qt,
`app/i18n` = translations). PyInstaller-safe: no dynamic imports for
app code, no data files loaded from relative paths without fallbacks.
