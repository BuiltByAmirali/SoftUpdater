"""Qt binding compatibility layer for SoftUpdater.

The normal (Windows 10/11, 64-bit) build uses PySide6. The Windows 7 /
32-bit build uses PyQt5 5.15 instead, because PySide6, Qt 6 itself and
the official PySide wheels simply do not support Windows 7 or 32-bit
Windows, while PyQt5 5.15 ships official 32-bit wheels and Qt 5.15
still runs on Windows 7 SP1.

run.main() calls install() BEFORE its first "from PySide6 ..." import.
install() keeps the real PySide6 whenever it is importable and only
otherwise registers a minimal PySide6-compatible facade over PyQt5 in
sys.modules, so the whole codebase keeps importing "PySide6" unchanged.
Only the two names that PySide and PyQt spell differently are aliased
(Signal and Slot) - the codebase uses no other divergent API (it was
audited: no QAction, no QMouseEvent.position(), only Qt5-valid scoped
enums and .exec()).

Set SOFTUPDATER_QT5=1 to force the PyQt5 facade even when PySide6 is
installed - the offline compatibility smoke test uses this to exercise
exactly the code path of the Windows 7 / 32-bit build.
"""
from __future__ import annotations

import os
import sys
import types

QT_IMPL = "unresolved"


def install() -> str:
    """Make "from PySide6 ... import" work under either binding. Idempotent."""
    global QT_IMPL
    force_qt5 = os.environ.get("SOFTUPDATER_QT5", "").strip() == "1"
    if not force_qt5:
        try:
            import PySide6  # noqa: F401  (real binding present - nothing to do)

            QT_IMPL = "PySide6"
            return QT_IMPL
        except ImportError:
            pass

    from PyQt5 import QtCore, QtGui, QtWidgets

    # The only PySide/PyQt spelling differences the codebase touches.
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

    facade = types.ModuleType("PySide6")
    facade.__path__ = []  # package-style; the submodules are aliased below
    facade.__version__ = "5.15-qt5-compat"
    facade.QtCore = QtCore
    facade.QtGui = QtGui
    facade.QtWidgets = QtWidgets
    sys.modules["PySide6"] = facade
    sys.modules["PySide6.QtCore"] = QtCore
    sys.modules["PySide6.QtGui"] = QtGui
    sys.modules["PySide6.QtWidgets"] = QtWidgets
    QT_IMPL = "PyQt5 5.15 (Windows 7 / 32-bit compatibility mode)"
    return QT_IMPL
