# Changelog

All notable changes to SoftUpdater are documented here.
Versions follow the project `VERSION` file; each release also ships as a
GitHub Release with the two official installers and their SHA-256 hashes.

## [1.1.7] - Open-source release prep

- New **Settings → About** page: app version, developer signature
  (**BuiltByAmirali**), a one-click button to the official repository and
  the MIT-license note - so an official build can always be told apart
  from any modified copy (and a future donation link has its proper,
  verifiable home).
- Signature everywhere: MIT `LICENSE` (BuiltByAmirali), EXE version
  resource and both Inno Setup installers now name
  *BuiltByAmirali / https://github.com/BuiltByAmirali/SoftUpdater* as the
  publisher (they previously carried placeholder values).
- GitHub-ready docs: this `CHANGELOG.md`, `CONTRIBUTING.md`,
  `SECURITY.md`, `.gitignore` and a Persian README (`README.fa.md`).
- `build/make_checksums.bat`: generates `SHA256SUMS.txt` for the built
  64-bit and 32-bit installers so users can verify their download.

## [1.1.6] - Icon optical alignment

- Every icon is nudged down by the exact cap-band offset of the live
  font metrics, so icons sit level with their label text in every
  language, at every size (14-20 pt) and on both build lines.

## [1.1.5] - Fluent-style vector icon set

- 27 hand-painted QPainter glyphs (no icon font, no image files) across
  the whole UI: buttons, search, context menu, tray, details dialog,
  Settings sidebar (active = accent), quick tour, header brand mark.
- Colored status dot in the footer (gray/green/amber/red).
- Direction-aware icons mirror in fa/ar RTL.

## [1.1.4] - Font-size rework

- The app-wide font only changes on **Done**; a fixed-height preview box
  on the Appearance page shows the chosen size while dragging (no page
  movement at all).
- Spinbox arrows are real antialiased white triangles (the old QSS
  border trick rendered as solid squares).
- Allowed range is **14-20 pt** (default 14).

## [1.1.3] - Three reported bugs

- Font-size slider truly mirrors for RTL (fa/ar).
- Windows 11 detected by build number (>= 22000), never shown as
  "Windows 10".
- Live font preview debounced; spinbox arrows visible again.

## [1.1.2] - Live re-translation + auto sorting

- Language switching re-translates everything in place, including
  checker notes (stored as canonical keys).
- After a 100% check the table groups itself: updates first, then
  up-to-date / vendor-managed, then "no source found", errors last.

## [1.1.1] - Frozen-build i18n hotfix

- Language modules are statically imported so PyInstaller one-file
  builds bundle all six dictionaries (raw keys no longer possible).

## [1.1.0] - Six languages + first-run tour

- Full UI in English, Persian, Arabic, Portuguese, French and German
  with live switching and true RTL; a dismissible first-run tour.

## [1.0.0] - Initial release

- Registry-based installed-app detection, official-source update
  checks (GitHub Releases / vendor feeds), per-architecture installer
  download (save-only), dark glassmorphism UI, background workers.
