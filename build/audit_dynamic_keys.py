"""Runtime verification of every DYNAMIC tr() key family in the project.

Static call-site audit can't see these; here we enumerate the real
runtime values from the actual modules and check them against ALL six
language dictionaries (not just en.py).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Qt facade first (sandbox has no libEGL for real PySide6 QtGui) - the
# exact code path of the Windows 7 / 32-bit build line.
from app import qt_compat  # noqa: E402

qt_compat.install()

from app.i18n import messages_for  # noqa: E402

codes = ("en", "fa", "ar", "pt", "fr", "de")
dicts = {c: messages_for(c) for c in codes}

missing = []


def check(key: str, origin: str) -> None:
    for c in codes:
        if key not in dicts[c]:
            missing.append(f"{origin}: {key!r} missing in {c}")


# 1) onboarding pages: prefix + ".title" / ".body"
from app.ui.onboarding import _PAGES  # noqa: E402
for prefix, _glyph in _PAGES:
    check(prefix + ".title", "onboarding")
    check(prefix + ".body", "onboarding")

# 2) settings sidebar/header keys
from app.ui import settings as ui_settings  # noqa: E402
inst = ui_settings.SettingsDialog.__new__(ui_settings.SettingsDialog)
for nav_key, header_key, _b in ui_settings.SettingsDialog._pages(inst):
    check(nav_key, "settings nav")
    check(header_key, "settings header")

# 3) main_window source-label translation (fixed dict + branches)
from app.ui.main_window import _STATUS_CODES  # noqa: E402
for code in _STATUS_CODES:
    check("status." + code, "status label")
for k in ("src.vendor", "src.winget", "src.github", "src.github_auto",
          "src.feed", "src.website", "src.mozilla", "src.vlc", "src.edge",
          "src.discord", "src.dl_server"):
    check(k, "source label")

# 4) catalog blocked reasons (blk.*)
from app.core import catalog  # noqa: E402
reasons = set()
for name in dir(catalog):
    obj = getattr(catalog, name)
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, str) and v.startswith("blk."):
                reasons.add(v)
            elif isinstance(v, dict):
                for vv in v.values():
                    if isinstance(vv, str) and vv.startswith("blk."):
                        reasons.add(vv)
blocked_sample = None
try:
    blocked_sample = catalog.blocked_reason
except AttributeError:
    pass
print(f"catalog blk.* reasons discovered: {len(reasons)}")
for r in sorted(reasons):
    check(r, "catalog blocked")

# 4b) every value of BLOCKED_GENERIC-style structures via blocked_reason()
#     is covered above only if the dicts are module-level; also probe the
#     public function with known inputs if cheap
# 5) update_checker variant notes (vn.*)
from app.core import update_checker  # noqa: E402
vn = set()
for name in dir(update_checker):
    obj = getattr(update_checker, name)
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, dict):
                note = v.get("note")
                if isinstance(note, str) and note.startswith("vn."):
                    vn.add(note)
            elif isinstance(v, str) and v.startswith("vn."):
                vn.add(v)
print(f"update_checker vn.* notes discovered: {len(vn)}")
for n in sorted(vn):
    check(n, "variant note")

if missing:
    print("MISSING KEYS:")
    print("\n".join(missing))
    sys.exit(1)
print("OK - every dynamic key family resolves in all 6 languages")
