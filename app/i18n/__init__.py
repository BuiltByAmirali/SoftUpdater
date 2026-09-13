"""SoftUpdater i18n engine - tiny, dependency-free, Qt-free.

Every user-facing string in the app goes through tr("some.key"). The
translations live in one module per language (app/i18n/en.py is the
master key set; fa/ar/pt/fr/de mirror it 1:1 - run.py --selftest
verifies the parity of keys AND placeholders for every language).

Design notes:
  * Plain Python (no Qt import here) so worker threads and the core
    checker/downloader can call tr() from any thread at any time.
  * Missing key -> English -> the key itself (never raises, never
    returns None) - a partial translation can never break the UI.
  * Placeholders use str.format style: tr("msg.found", n=3).
  * set_language() is instant and global: the Settings dialog calls it
    and every window re-translates itself live (MainWindow.retranslate_ui,
    SettingsDialog.retranslate) - no restart, no state loss.
"""
from __future__ import annotations

# STATIC imports for every language module - DO NOT replace these with
# importlib.import_module(). The frozen build (PyInstaller --onefile)
# only bundles modules that are visible to its static analysis; v1.1.0
# loaded the languages dynamically, which worked from source but produced
# an exe whose tr() could not find ANY language module, so the whole UI
# displayed raw keys ("ob.welcome.title", "btn.refresh", ...). With this
# static import graph, "pyinstaller run.py" bundles all six language
# modules on both build lines (PySide6 x64 and PyQt5 win32) with zero
# --hidden-import flags. When adding a language: create app/i18n/xx.py
# AND add it to the import below AND to _MODULES.
from . import ar, de, en, fa, fr, pt  # noqa: F401

# code -> native name (ALWAYS shown in its own language, never translated)
LANGUAGES = (
    ("en", "English"),
    ("fa", "فارسی"),
    ("ar", "العربية"),
    ("pt", "Português"),
    ("fr", "Français"),
    ("de", "Deutsch"),
)

RTL_LANGUAGES = frozenset(("fa", "ar"))
DEFAULT_LANGUAGE = "en"

# static code -> module map (PyInstaller-safe, see the import note above)
_MODULES = {
    "en": en,
    "fa": fa,
    "ar": ar,
    "pt": pt,
    "fr": fr,
    "de": de,
}

_current = DEFAULT_LANGUAGE
_en_fallback: dict = {}


def language_codes() -> list:
    return [code for code, _name in LANGUAGES]


def native_name(code: str) -> str:
    for c, name in LANGUAGES:
        if c == code:
            return name
    return code


def current_language() -> str:
    return _current


def is_rtl(code: str = "") -> bool:
    """True for right-to-left languages (Persian, Arabic)."""
    return (code or _current) in RTL_LANGUAGES


def set_language(code: str) -> str:
    """Switch the active language (instant, global, thread-safe enough:
    module-level str swap is atomic under the GIL)."""
    global _current
    _current = code if code in language_codes() else DEFAULT_LANGUAGE
    return _current


def _messages(code: str) -> dict:
    mod = _MODULES.get(code)
    if mod is None:  # unknown code -> English (never raises)
        mod = _MODULES[DEFAULT_LANGUAGE]
    return mod.MESSAGES


def _english() -> dict:
    if not _en_fallback:
        _en_fallback.update(_messages(DEFAULT_LANGUAGE))
    return _en_fallback


def tr(key: str, **kwargs) -> str:
    """Translate `key` in the current language (English fallback).

    Never raises: an unknown key returns the key itself so a forgotten
    translation can never crash the UI."""
    try:
        text = _messages(_current).get(key)
        if text is None:
            text = _english().get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass  # keep the raw template instead of crashing
        return text
    except Exception:
        return key


def messages_for(code: str) -> dict:
    """Direct access (self-test / parity checks only)."""
    return _messages(code)
