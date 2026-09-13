"""Rotating application log + global crash capture.

Everything the app does that is worth diagnosing later (checks, downloads,
errors, crashes) is appended to a small rotating log file so a problem can
be investigated afterwards instead of being lost with the process.

Log location:
  Windows : %LOCALAPPDATA%\\SoftUpdater\\logs\\softupdater.log
  other   : /tmp/SoftUpdater/logs/softupdater.log
Rotation: 512 KB per file, 3 backups kept (softupdater.log.1 ... .3).
"""
from __future__ import annotations

import logging
import os
import traceback
from logging.handlers import RotatingFileHandler

_MAX_BYTES = 512 * 1024
_BACKUPS = 3

_logger: logging.Logger | None = None


def log_dir() -> str:
    """Directory that holds the rotating log file."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = "/tmp"
    return os.path.join(base, "SoftUpdater", "logs")


def log_file() -> str:
    return os.path.join(log_dir(), "softupdater.log")


def legacy_error_file() -> str:
    """The error.log location older versions wrote crashes to (kept in sync)."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = "/tmp"
    return os.path.join(base, "SoftUpdater", "error.log")


def _append_legacy(text: str) -> None:
    """Best-effort mirror of crash traces into the legacy error.log file."""
    try:
        os.makedirs(os.path.dirname(legacy_error_file()), exist_ok=True)
        with open(legacy_error_file(), "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass


def get_logger() -> logging.Logger:
    """Create (once) and return the app logger."""
    global _logger
    if _logger is not None:
        return _logger
    logger = logging.getLogger("SoftUpdater")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        try:
            os.makedirs(log_dir(), exist_ok=True)
            handler = RotatingFileHandler(
                log_file(), maxBytes=_MAX_BYTES, backupCount=_BACKUPS,
                encoding="utf-8")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s"))
            logger.addHandler(handler)
        except Exception:
            pass  # logging must never break the app - console only then
    _logger = logger
    return logger


def event(msg: str) -> None:
    """Log an informational line (never raises)."""
    try:
        get_logger().info(msg)
    except Exception:
        pass


def error(msg: str) -> None:
    """Log an error line (never raises)."""
    try:
        get_logger().error(msg)
    except Exception:
        pass


def format_exception(exc_type, exc_value, exc_tb) -> str:
    return "".join(traceback.format_exception(exc_type, exc_value, exc_tb))


def install_crash_hook(show_dialog: bool = False) -> None:
    """Route uncaught Python exceptions into the rotating log.

    show_dialog: additionally show one non-modal QMessageBox (GUI mode) so
    the user knows a problem happened and where the details are stored.
    """
    import sys

    def hook(exc_type, exc_value, exc_tb):
        text = format_exception(exc_type, exc_value, exc_tb)
        try:
            error("UNCAUGHT EXCEPTION:\n" + text.rstrip())
        except Exception:
            pass
        _append_legacy(text)
        try:
            sys.__stderr__.write(text + "\n")
        except Exception:
            pass
        if show_dialog:
            try:
                from PySide6.QtWidgets import QApplication, QMessageBox
                if QApplication.instance() is not None:
                    QMessageBox.critical(
                        None, "Unexpected error",
                        "An unexpected error occurred. Details were written "
                        "to the SoftUpdater log:\n" + log_file() +
                        "\n\n" + text[-800:])
            except Exception:
                pass

    sys.excepthook = hook
