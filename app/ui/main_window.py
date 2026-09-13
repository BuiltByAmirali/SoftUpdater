"""Main window - multilingual UI (i18n + RTL), explicit crash-safety
(native frame + queued signals).

Extras (UniGetUI-inspired, without cloning its UI):
  * system tray icon + scheduled re-checks + toast notifications
  * per-app details dialog (versions, source, direct installer URL, hash)
  * skip-one-version ignore map (in addition to hiding whole apps)
  * export/import app list (JSON backup)
  * POST-INSTALL AUTO RE-CHECK: after a successful download the app quietly
    watches the registry; the moment the user finishes installing (version
    changes), that one app is re-checked automatically so its row flips to
    the honest 'Up to date' - no manual click needed.
"""

from __future__ import annotations
from __future__ import annotations

import json
import os
import re
import textwrap
import time
from datetime import datetime

from PySide6.QtCore import QPointF, QEvent, QRectF, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QFontMetrics,
    QIcon,
    QPainter,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStyle,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QSystemTrayIcon,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core import applog
from ..core.downloader import (
    download_dir,
    format_size,
    format_speed,
    set_custom_download_dir,
)
from ..core.installed_apps import InstalledApp, build_fresh_index, list_installed_apps
from ..core.update_checker import CheckResult
from ..core.version_utils import compare_versions, normalize_name
from ..core.win_info import os_bitness, windows_summary, windows_summary_l10n
from .. import i18n
from ..i18n import tr
from . import settings as app_settings
from . import theme
from . import ui_icons
from .workers import (
    CheckWorker,
    DownloadWorker,
    IconWorker,
    VersionWatchWorker,
)

COL_NAME, COL_PUB, COL_INSTALLED, COL_LATEST, COL_STATUS, COL_SOURCE = range(6)
# Role that stores (version, size_text) for the Latest column delegate so the
# update size can be drawn in the accent green next to the version number.
LATEST_SIZE_ROLE = Qt.UserRole + 1

_STATUS_CODES = frozenset((
    "update", "latest", "no_installer", "vendor", "no_source",
    "failed", "pending", "skipped",
))

# Automatic row order after a finished 100% check (user request):
# apps WITH updates first, then up-to-date / vendor-managed, then
# "no source found", and the red errors LAST; alphabetical within each
# group. Unknown codes sort with the pending tail.
_STATUS_ORDER = {
    "update": 0,        # update available - actionable, top of the list
    "latest": 1,        # already the newest version
    "vendor": 2,        # managed/updated by its vendor (nothing to do)
    "no_installer": 3,  # source found but no installer for this machine
    "no_source": 4,     # no official source discovered
    "skipped": 5,       # update dismissed by the user
    "pending": 6,       # not checked yet
    "failed": 7,        # red check errors at the very bottom
}
_NAT_SPLIT = re.compile(r"(\d+)")


def _natural_name_key(text: str) -> tuple:
    """Case-insensitive NATURAL sort key ('app 2' < 'app 9' < 'app 10') -
    pure Python so both Qt engines sort identically."""
    chunks = []
    for part in _NAT_SPLIT.split((text or "").strip().casefold()):
        if part == "":
            continue
        if part.isdigit():
            chunks.append((1, int(part), ""))
        else:
            chunks.append((0, 0, part))
    return tuple(chunks)


def _status_label(code: str) -> str:
    """Translated status text; unknown codes pass through untouched."""
    return tr("status." + code) if code in _STATUS_CODES else code


def _l10n_source(label: str) -> str:
    """Translate the canonical (English) source labels at DISPLAY time -
    the values stored on results (and in logs/exports) stay canonical, so
    switching languages can never corrupt data."""
    if not label:
        return label
    if label == "Vendor-managed":
        return tr("src.vendor")
    if label == "Winget official manifest":
        return tr("src.winget")
    if label.startswith("GitHub (auto-matched) - "):
        return tr("src.github_auto",
                  repo=label[len("GitHub (auto-matched) - "):])
    if label.startswith("GitHub - "):
        return tr("src.github", repo=label[len("GitHub - "):])
    fixed = {
        "Official version feed": "src.feed",
        "Official website": "src.website",
        "Mozilla official download": "src.mozilla",
        "VideoLAN official mirror": "src.vlc",
        "Microsoft Edge official updates": "src.edge",
        "Discord official download": "src.discord",
        "Official download server": "src.dl_server",
    }
    return tr(fixed[label]) if label in fixed else label


STATUS_COLOR = {
    "update": "#ffb224",
    "latest": "#2dd4a7",
    "no_installer": "#ff8d5c",
    "vendor": "#69b7a2",
    "no_source": "#98a2b3",
    "failed": "#e5484d",
    "pending": "#6b7686",
    "skipped": "#c792ea",
}

# Column widths are distributed PROPORTIONALLY across the table, so no single
# column hogs the window and none gets starved (user feedback).
_COL_WEIGHTS = {
    COL_NAME: 25,      # Application
    COL_PUB: 14,       # Publisher
    COL_INSTALLED: 9,  # Installed
    COL_LATEST: 9,     # Latest
    COL_STATUS: 17,    # Status
    COL_SOURCE: 15,    # Source
}
_COL_MIN_PX = {
    COL_NAME: 200,
    COL_PUB: 110,
    COL_INSTALLED: 86,
    COL_LATEST: 86,
    COL_STATUS: 150,
    COL_SOURCE: 110,
}

# Post-install auto re-check: after a successful download the app polls the
# LOCAL registry (worker thread, no network requests) and the moment the
# installed version changes it re-checks that ONE app, so the row turns
# 'Up to date' by itself right after the user installs the update.
WATCH_POLL_SEC = 12          # registry poll cadence (cheap, off the UI thread)
WATCH_WINDOW_SEC = 60 * 60   # stop watching quietly after one hour

# Retired-but-still-alive worker wrappers are parked here so the garbage
# collector can NEVER destroy a QThread while its thread is running - Qt
# aborts the whole process with qFatal ("QThread: Destroyed while thread is
# still running") in that case, which closed the app without any dialog.
_PARKED_WORKERS: list = []


def _retire_worker(worker) -> None:
    """Wait for FULL thread termination, then queue object destruction.

    The worker has just emitted finished_all from the last statement of
    run(), so wait() returns almost instantly. Dropping the last Python
    reference any earlier destroys the C++ QThread while Qt still considers
    the thread running -> qFatal -> the app closes with no error dialog
    (the crash reported when a check finished).
    """
    if worker is None:
        return
    try:
        if worker.isRunning() and not worker.wait(2000):
            # Stuck in a long network call: park the wrapper so it is never
            # garbage-collected while running. closeEvent waits for it too,
            # and process exit joins it in the worst case.
            _PARKED_WORKERS.append(worker)
            return
    except RuntimeError:
        return  # wrapper already destroyed - nothing to do
    try:
        worker.deleteLater()
    except RuntimeError:
        pass


class _LatestDelegate(QStyledItemDelegate):
    """Latest column painter: version in the normal text color and the exact
    update size in the accent green, side by side (user request: the white
    size text was hard to tell apart from the version number). Rows without
    a known size fall back to the default painter."""

    def paint(self, painter, option, index) -> None:
        data = index.data(LATEST_SIZE_ROLE)
        if not (isinstance(data, tuple) and len(data) == 2):
            super().paint(painter, option, index)
            return
        version, size_text = str(data[0]), str(data[1])
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""  # background/selection only; text is drawn by hand
        widget = opt.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)
        try:
            rect = style.subElementRect(QStyle.SE_ItemViewItemText, opt, widget)
            if rect.isNull():
                rect = opt.rect
            rect = rect.adjusted(4, 0, -4, 0)
            fm = QFontMetrics(opt.font)
            sep = "  \u00b7  "
            size_w = fm.horizontalAdvance(size_text)
            sep_w = fm.horizontalAdvance(sep)
            avail = max(10, rect.width() - size_w - sep_w)
            version_text = fm.elidedText(version, Qt.ElideRight, avail)
            if version_text != version:  # keep the version, drop the sep
                sep, sep_w = "", 0
            # Colors come from the theme constants (the QSS selection-color
            # is the same TEXT color, so this matches every row state).
            painter.save()
            painter.setFont(opt.font)
            y = rect.top() + ((rect.height() - fm.height()) // 2) + fm.ascent()
            if opt.direction == Qt.RightToLeft:
                # mirrored: the version starts at the row's RIGHT edge and
                # the size flows to its left
                total = fm.horizontalAdvance(version_text) + sep_w + size_w
                x = rect.right() + 1 - total
            else:
                x = rect.left()
            painter.setPen(QColor(theme.TEXT))
            painter.drawText(x, y, version_text)
            x += fm.horizontalAdvance(version_text)
            if sep:
                painter.setPen(QColor(theme.TEXT_DIM))
                painter.drawText(x, y, sep)
                x += sep_w
            painter.setPen(QColor(theme.ACCENT))
            painter.drawText(x, y, size_text)
            painter.restore()
        except Exception:
            try:
                painter.restore()
            except Exception:
                pass
            super().paint(painter, option, index)  # last-resort fallback


class _RowAccentDelegate(QStyledItemDelegate):
    """Selected-row 'glass edge': after the normal cell paint, draw a soft
    white vertical bar on the left edge of the selected row (column 0 is the
    row's start, so the bar sits exactly at the row's left edge).
    Pure extra painting on top of the standard pipeline - no geometry or
    interaction changes, and every failure falls back to the default look."""

    def paint(self, painter, option, index) -> None:
        super().paint(painter, option, index)
        try:
            if not (option.state & QStyle.State_Selected):
                return
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing, True)
            rect = option.rect
            pt = option.font.pointSizeF()
            if not pt or pt <= 0:
                pt = float(option.font.pointSize() or 11)
            inset = max(3.0, 4.0 * pt / 10.0)
            width = max(2.0, 3.0 * pt / 10.0)
            if opt.direction == Qt.RightToLeft:
                bar = QRectF(rect.right() - width - 1.0, rect.top() + inset,
                             width, max(4.0, rect.height() - 2 * inset))
            else:
                bar = QRectF(rect.left() + 1.0, rect.top() + inset, width,
                             max(4.0, rect.height() - 2 * inset))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, 221))
            painter.drawRoundedRect(bar, width / 2.0, width / 2.0)
            painter.restore()
        except Exception:
            try:
                painter.restore()
            except Exception:
                pass


class _DetailsDialog(QDialog):
    """Everything known about ONE app in a small dark dialog: its own icon,
    versions, status, source, direct installer link + copy button, and the
    checker's explanation (UniGetUI's package-details idea, our own layout)."""

    def __init__(self, app: InstalledApp, res: CheckResult | None, parent=None,
                 icon: QIcon | None = None):
        super().__init__(parent)
        self.setWindowTitle(tr("det.title", name=app.name))
        self.setMinimumWidth(620)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 14)
        lay.setSpacing(12)
        head = QHBoxLayout()
        head.setSpacing(12)
        try:
            if icon is not None and not icon.isNull():
                ic_lbl = QLabel()
                ic_lbl.setPixmap(icon.pixmap(44, 44))
                head.addWidget(ic_lbl, 0, Qt.AlignVCenter)
        except Exception:
            pass
        head.addWidget(QLabel(app.name, objectName="detailTitle"), 1)
        lay.addLayout(head)

        card = QFrame(objectName="card")
        grid = QGridLayout(card)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(9)

        status = res.status if res else "pending"
        note = (res.note_text() if res else "") or ""
        self._source_url = (res.source_url if res else "") or ""
        rows = [
            (tr("det.publisher"), app.publisher or "-", ""),
            (tr("det.installed_version"),
             (res.installed_version if res else app.version) or "-", ""),
            (tr("det.latest_version"),
             (res.latest_version if res else "") or "-", ""),
            (tr("det.status"), _status_label(status),
             STATUS_COLOR.get(status, theme.TEXT)),
            (tr("det.source"), _l10n_source((res.source_label if res else "") or ""), ""),
            (tr("det.size"),
             format_size(res.size_bytes) if (res and res.size_bytes) else "-", ""),
            (tr("det.arch"), (res.arch if res else "") or "-", ""),
            (tr("det.sha"),
             (tr("det.sha_ok") if res and res.sha256 else tr("det.sha_none")), ""),
        ]
        for i, (key, value, color) in enumerate(rows):
            k = QLabel(key, objectName="detailKey")
            v = QLabel(value, objectName="detailValue")
            v.setTextInteractionFlags(Qt.TextSelectableByMouse)
            v.setWordWrap(True)
            if color:
                v.setStyleSheet(f"color: {color};")
            grid.addWidget(k, i, 0, Qt.AlignTop)
            grid.addWidget(v, i, 1)
        grid.setColumnStretch(1, 1)
        lay.addWidget(card)

        if note:
            note_lbl = QLabel(textwrap.fill(note, 78), objectName="settingsHint")
            note_lbl.setWordWrap(True)
            lay.addWidget(note_lbl)

        # installer URL row (copyable)
        url = (res.installer_url if res else "") or ""
        url_row = QHBoxLayout()
        url_row.setSpacing(8)
        self._url_edit = QLineEdit(url)
        self._url_edit.setReadOnly(True)
        self._url_edit.setPlaceholderText(tr("det.placeholder"))
        url_row.addWidget(self._url_edit, 1)
        btn_copy = QPushButton(tr("btn.copy"), objectName="compact")
        btn_copy.setEnabled(bool(url))
        btn_copy.clicked.connect(self._copy_url)
        try:
            px = theme.scale_px(13, self.font().pointSize()
                                or theme.DEFAULT_FONT_PT)
            btn_copy.setIcon(ui_icons.icon("copy", px))
            btn_copy.setIconSize(QSize(px, px))
        except Exception:
            pass
        url_row.addWidget(btn_copy)
        lay.addLayout(url_row)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        btn_page = QPushButton(tr("btn.open_page"), objectName="compact")
        btn_page.setEnabled(bool(res and res.source_url))
        btn_page.clicked.connect(self._open_page)
        try:
            px = theme.scale_px(13, self.font().pointSize()
                                or theme.DEFAULT_FONT_PT)
            btn_page.setIcon(ui_icons.icon("globe", px))
            btn_page.setIconSize(QSize(px, px))
        except Exception:
            pass
        btns.addWidget(btn_page)
        btns.addStretch(1)
        btn_close = QPushButton(tr("btn.close"), objectName="primary")
        btn_close.setDefault(True)
        btn_close.clicked.connect(self.accept)
        try:
            px = theme.scale_px(14, self.font().pointSize()
                                or theme.DEFAULT_FONT_PT)
            btn_close.setIcon(ui_icons.icon("check", px, "on_primary"))
            btn_close.setIconSize(QSize(px, px))
        except Exception:
            pass
        btns.addWidget(btn_close)
        lay.addLayout(btns)

    def _copy_url(self) -> None:
        try:
            QApplication.clipboard().setText(self._url_edit.text())
        except Exception:
            pass

    def _open_page(self) -> None:
        try:
            if self._source_url:
                QDesktopServices.openUrl(QUrl(self._source_url))
        except Exception:
            pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("win.title"))
        # 1240 default: the icon-bearing action row fits comfortably at the
        # default 14 pt font (the row needs ~1200px incl. icons); the user
        # can still shrink to the 760px minimum - columns re-balance.
        self.resize(1240, 680)
        self.setMinimumSize(760, 480)
        # Layout direction follows the chosen UI language (the QApplication
        # default is set at startup and live-flipped on language change).

        self.apps: list[InstalledApp] = []
        self.results: dict[str, CheckResult] = {}   # key = f"{name}|{version}"
        self._check_worker: CheckWorker | None = None
        self._download_worker: DownloadWorker | None = None
        self._icon_worker: IconWorker | None = None
        self._icons_by_name: dict[str, QIcon] = {}   # rendered app icons
        self._dl_paused = False
        self._font_pt = app_settings.load_font_pt()
        self._skipped: dict[str, str] = app_settings.load_skipped_versions()
        self._auto_run = False          # check was started automatically
        self._dl_total = 0              # bulk download queue counters
        self._dl_done = 0
        self._tray: QSystemTrayIcon | None = None
        self._interval_timer: QTimer | None = None
        self._checking_keys: set[str] = set()  # rows currently "Checking..."
        self._tray_updates = 0          # last updates count (tooltip re-text)
        self._check_scope = 0           # apps in the RUNNING check (auto-sort)

        # Post-install auto re-check state (see WATCH_* constants).
        self._watch_keys: set[str] = set()          # row keys being watched
        self._watch_deadline: dict[str, float] = {}  # key -> unix deadline
        self._watch_scan_worker: VersionWatchWorker | None = None
        self._post_install_names: set[str] = set()   # normalized names awaiting the confirming re-check
        self._post_install_confirmed: list[tuple[str, str]] = []
        self._watch_timer = QTimer(self)
        self._watch_timer.timeout.connect(self._on_watch_tick)
        # Fluent-style UI icons (ui_icons.py): btn -> [name, base_px, role];
        # re-created at the user's font size, live-rescaled by _apply_font_pt.
        self._icon_specs: dict = {}
        self._search_action = None      # QLineEdit trailing search glass
        self._status_kind = "dim"       # status dot color kind

        # Honor the user-chosen download folder (Settings) from the start.
        set_custom_download_dir(app_settings.load_download_dir())

        self._build_ui()
        self._load_apps()

        # Optional convenience: run the full check by itself at startup.
        if app_settings.load_auto_check():
            QTimer.singleShot(600, self._auto_check_on_start)

        self._build_tray()
        self._arm_interval_timer()
        # First-launch quick tour (a few tips; permanently opt-out-able).
        QTimer.singleShot(500, self._maybe_show_tour)
        applog.event(
            f"App started - {len(self.apps)} app(s) listed - {windows_summary()}")

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        root = QWidget(objectName="root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(18, 16, 18, 12)
        lay.setSpacing(12)

        # --- header card
        header = QFrame(objectName="card")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(16, 12, 16, 12)
        hlay.setSpacing(12)
        # Brand mark (ui_icons 'logo' tile) left of the title - scales with
        # the font size and mirrors into RTL automatically via the layout.
        self._logo_label = QLabel()
        self._logo_label.setPixmap(
            ui_icons.pixmap("logo", theme.scale_px(40, self._font_pt),
                            vshift=0.0))  # full-bleed tile: never nudged
        self._logo_label.setAlignment(Qt.AlignVCenter)
        hlay.addWidget(self._logo_label, 0, Qt.AlignVCenter)
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self.title_label = QLabel("SoftUpdater", objectName="appTitle")
        self.subtitle_label = QLabel(windows_summary_l10n(),
                                     objectName="appSubtitle")
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)
        hlay.addLayout(title_box)
        hlay.addStretch(1)
        self.arch_chip = QLabel(
            tr("bits.64") if os_bitness() == 64 else tr("bits.32"),
            objectName="chip")
        self.arch_chip.setAlignment(Qt.AlignCenter)
        hlay.addWidget(self.arch_chip, 0, Qt.AlignVCenter)
        lay.addWidget(header)

        # --- toolbar row
        bar = QHBoxLayout()
        bar.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("search.placeholder"))
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._apply_filter)
        self._add_search_icon()
        bar.addWidget(self.search, 1)

        self.btn_refresh = QPushButton(tr("btn.refresh"))
        self.btn_refresh.setToolTip(tr("tip.refresh"))
        self.btn_refresh.clicked.connect(self._on_refresh_clicked)
        self._iconize(self.btn_refresh, "refresh")
        bar.addWidget(self.btn_refresh)

        self.btn_open_dir = QPushButton(tr("btn.open_dir"))
        self.btn_open_dir.clicked.connect(self._open_download_dir)
        self._iconize(self.btn_open_dir, "folder")
        bar.addWidget(self.btn_open_dir)

        self.btn_settings = QPushButton(tr("btn.settings"))
        self.btn_settings.setToolTip(tr("tip.settings"))
        self.btn_settings.clicked.connect(self._on_settings)
        self._iconize(self.btn_settings, "gear")
        bar.addWidget(self.btn_settings)
        lay.addLayout(bar)

        # --- action row
        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.btn_check = QPushButton(tr("btn.check_all"), objectName="primary")
        self.btn_check.setToolTip(tr("tip.check_all"))
        self.btn_check.clicked.connect(self._on_check_all)
        self._iconize(self.btn_check, "shield_check", 17, "on_primary")
        actions.addWidget(self.btn_check)

        self.btn_check_sel = QPushButton(tr("btn.check_sel"))
        self.btn_check_sel.setToolTip(tr("tip.check_sel"))
        self.btn_check_sel.clicked.connect(self._on_check_selected)
        self._iconize(self.btn_check_sel, "check_square")
        actions.addWidget(self.btn_check_sel)

        self.btn_download = QPushButton(tr("btn.download"))
        self.btn_download.setToolTip(tr("tip.download"))
        self.btn_download.clicked.connect(self._on_download_selected)
        self._iconize(self.btn_download, "download", 16, "accent")
        actions.addWidget(self.btn_download)

        self.chk_open = QCheckBox(tr("chk.open"))
        self.chk_open.setToolTip(tr("tip.open"))
        self.chk_open.setChecked(app_settings.load_open_installer())
        self.chk_open.toggled.connect(self._on_open_toggled)
        actions.addWidget(self.chk_open)
        actions.addStretch(1)
        lay.addLayout(actions)

        # --- progress (update CHECKS only)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        lay.addWidget(self.progress)

        # --- download panel (only visible while downloading; keeps the UI
        # clean - nothing overlaps the table or other labels)
        self.dl_panel = QFrame(objectName="card")
        dl = QVBoxLayout(self.dl_panel)
        dl.setContentsMargins(14, 10, 14, 10)
        dl.setSpacing(6)
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.dl_title = QLabel("", objectName="dlTitle")
        row1.addWidget(self.dl_title, 1)
        self.btn_pause = QPushButton(tr("btn.pause"), objectName="compact")
        self.btn_pause.setToolTip(tr("tip.pause"))
        self.btn_pause.clicked.connect(self._on_pause_clicked)
        self._iconize(self.btn_pause, "pause", 13)
        row1.addWidget(self.btn_pause)
        self.btn_cancel_dl = QPushButton(tr("btn.cancel"), objectName="compact")
        self.btn_cancel_dl.setToolTip(tr("tip.cancel"))
        self.btn_cancel_dl.clicked.connect(self._on_cancel_download)
        self._iconize(self.btn_cancel_dl, "close", 13, "danger")
        row1.addWidget(self.btn_cancel_dl)
        dl.addLayout(row1)
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.dl_bar = QProgressBar()
        self.dl_bar.setRange(0, 100)
        self.dl_bar.setValue(0)
        row2.addWidget(self.dl_bar, 1)
        self.dl_meta = QLabel("", objectName="dlMeta")
        row2.addWidget(self.dl_meta)
        dl.addLayout(row2)
        self.dl_panel.setVisible(False)
        lay.addWidget(self.dl_panel)

        # --- table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            tr("col.app"), tr("col.pub"), tr("col.installed"),
            tr("col.latest"), tr("col.status"), tr("col.source"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(False)
        self.table.setWordWrap(False)
        self.table.itemDoubleClicked.connect(self._on_row_double_clicked)
        # Selection feedback: frosted white band (QSS) + glass edge bar drawn
        # by the column-0 delegate. Hover needs mouse tracking to work.
        self.table.setMouseTracking(True)
        self.table.setItemDelegateForColumn(COL_NAME, _RowAccentDelegate(self.table))
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)
        header_view = self.table.horizontalHeader()
        header_view.setStretchLastSection(False)
        header_view.setMinimumSectionSize(48)
        # All columns user-resizable; the app re-balances them proportionally
        # whenever the table is resized (see _distribute_columns).
        header_view.setSectionResizeMode(QHeaderView.Interactive)
        self.table.setItemDelegateForColumn(COL_LATEST, _LatestDelegate(self.table))
        self.table.viewport().installEventFilter(self)
        # App icons in the Application column (UniGetUI-style): reserve the
        # icon slot and give rows enough height to show it cleanly.
        icon_px = theme.scale_px(20, self._font_pt)
        self.table.setIconSize(QSize(icon_px, icon_px))
        self.table.verticalHeader().setDefaultSectionSize(
            theme.scale_px(30, self._font_pt))
        lay.addWidget(self.table, 1)

        # --- footer status line (inside layout; window has native frame)
        footer = QHBoxLayout()
        footer.setSpacing(8)
        self._status_dot = QLabel()
        self._status_dot.setFixedWidth(theme.scale_px(12, self._font_pt))
        self._status_dot.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        footer.addWidget(self._status_dot)
        self.status_label = QLabel(tr("msg.ready"), objectName="statusLabel")
        footer.addWidget(self.status_label)
        footer.addStretch(1)
        self.counts_label = QLabel("", objectName="countsLabel")
        footer.addWidget(self.counts_label)
        lay.addLayout(footer)
        self._set_status(tr("msg.ready"))

    # ------------------------------------------------------- UI icon kit
    def _iconize(self, btn, name: str, base: int = 16,
                 role: str = "text") -> None:
        """Give a button a Fluent-style vector icon (scaled to the current
        font size) and remember it so _apply_font_pt can re-scale it live."""
        try:
            px = theme.scale_px(base, self._font_pt)
            btn.setIcon(ui_icons.icon(name, px, role))
            btn.setIconSize(QSize(px, px))
            self._icon_specs[btn] = [name, int(base), role]
        except Exception:
            pass

    def _add_search_icon(self) -> None:
        """Magnifier glass inside the search field (leading side; Qt puts it
        on the correct side in RTL automatically)."""
        try:
            if self._search_action is not None:
                self.search.removeAction(self._search_action)
            px = theme.scale_px(14, self._font_pt)
            self._search_action = self.search.addAction(
                ui_icons.icon("search", px, "dim"), QLineEdit.LeadingPosition)
        except Exception:
            self._search_action = None

    def _apply_icon_sizes(self) -> None:
        """Re-render every registered UI icon at the new font size."""
        try:
            pt = int(self._font_pt)
            for btn, (name, base, role) in list(self._icon_specs.items()):
                try:
                    px = theme.scale_px(base, pt)
                    btn.setIcon(ui_icons.icon(name, px, role))
                    btn.setIconSize(QSize(px, px))
                except Exception:
                    pass
            self._logo_label.setPixmap(
                ui_icons.pixmap("logo", theme.scale_px(40, pt),
                                vshift=0.0))  # full-bleed tile: never nudged
            self._status_dot.setFixedWidth(theme.scale_px(12, pt))
            self._set_status(self.status_label.text(), self._status_kind)
            self._add_search_icon()
        except Exception:
            pass

    def _set_status(self, text: str, kind: str = "dim") -> None:
        """Status line text + the small colored state dot in front of it
        (dim=neutral, accent=success/action, amber=busy/warn, danger=error)."""
        self._status_kind = kind if kind in ui_icons.DOT_COLORS else "dim"
        try:
            self.status_label.setText(text)
            px = theme.scale_px(11, self._font_pt)
            self._status_dot.setPixmap(
                ui_icons.pixmap("dot", px, self._status_kind))
        except Exception:
            pass

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _app_key(name: str, version: str) -> str:
        return f"{name}|{version}"

    # ------------------------------------------------- proportional columns
    def eventFilter(self, obj, event):  # noqa: N802 - Qt override
        # Re-balance column widths whenever the table viewport is resized
        # (window resized/maximized, scrollbar appears, font size changed).
        try:
            if (obj is self.table.viewport() and
                    event.type() == QEvent.Resize):
                self._distribute_columns()
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def _distribute_columns(self) -> None:
        """Share the table width across columns by weight, honoring minimums,
        so the whole row always fits the window with no oversized column."""
        vw = self.table.viewport().width()
        if vw < 100:
            return
        total_w = float(sum(_COL_WEIGHTS.values()))
        sizes = {
            col: max(_COL_MIN_PX[col], int(vw * w / total_w))
            for col, w in _COL_WEIGHTS.items()
        }
        # If the minimums overshot a narrow window, shrink the columns that
        # are still above their minimum until everything fits.
        excess = sum(sizes.values()) - vw
        while excess > 0:
            flexible = [c for c in sizes if sizes[c] > _COL_MIN_PX[c]]
            if not flexible:
                break
            pool = sum(sizes[c] - _COL_MIN_PX[c] for c in flexible)
            cut = min(excess, pool)
            removed = 0
            for c in flexible:
                dec = min(round(cut * (sizes[c] - _COL_MIN_PX[c]) / pool),
                          sizes[c] - _COL_MIN_PX[c], excess)
                if dec > 0:
                    sizes[c] -= dec
                    excess -= dec
                    removed += dec
            if removed == 0:
                break
        header = self.table.horizontalHeader()
        for col, size in sizes.items():
            header.resizeSection(col, size)

    def _load_apps(self) -> None:
        hidden = set(app_settings.load_hidden_apps())
        self.apps = [a for a in list_installed_apps() if a.name not in hidden]
        self.results.clear()
        self._checking_keys.clear()
        self.table.setSortingEnabled(False)
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(0)
        for app in self.apps:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, COL_NAME, self._item(app.name))
            self.table.setItem(row, COL_PUB, self._item(app.publisher or "-"))
            self.table.setItem(row, COL_INSTALLED, self._item(app.display_version))
            self.table.setItem(row, COL_LATEST, self._item("-"))
            self.table.setItem(row, COL_STATUS,
                               self._item(_status_label("pending")))
            self.table.setItem(row, COL_SOURCE, self._item("-"))
            key = self._app_key(app.name, app.version)
            self.table.item(row, COL_NAME).setData(Qt.UserRole, key)
        self.table.setUpdatesEnabled(True)
        self._apply_filter(self.search.text())
        self._set_counts()
        self._set_status(tr("msg.found_apps", n=len(self.apps)))
        self._start_icon_worker()

    # ------------------------------------------------------------ app icons
    def _start_icon_worker(self) -> None:
        """(Re)start background icon extraction for the current rows.
        Runs off the UI thread (UniGetUI's IconStore approach); every icon
        arrives individually via a queued signal so the list shows up
        immediately and icons pop in progressively."""
        try:
            old = self._icon_worker
            if old is not None:
                try:
                    old.cancel()
                except Exception:
                    pass
                _retire_worker(old)
            worker = IconWorker(list(self.apps), online_icons=True)
            self._icon_worker = worker
            worker.icon_ready.connect(self._on_icon_ready)
            worker.finished_all.connect(
                lambda _n, w=worker: _retire_worker(w))
            worker.start()
        except Exception:
            pass

    def _on_icon_ready(self, name: str, key: str, png) -> None:
        """Apply one extracted icon to its row(s); thread-safe queued slot."""
        try:
            if not png:
                return
            pm = QPixmap()
            if not pm.loadFromData(bytes(png)):
                return
            icon = QIcon(pm)
            self._icons_by_name[name] = icon
            for row in self._rows_with_key(key):
                it = self.table.item(row, COL_NAME)
                if it is not None:
                    it.setIcon(icon)
                    self.table.resizeRowToContents(row)
        except Exception:
            pass

    @staticmethod
    def _item(text: str) -> QTableWidgetItem:
        it = QTableWidgetItem(text or "-")
        it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return it

    def _find_row(self, key: str) -> int:
        rows = self._rows_with_key(key)
        return rows[0] if rows else -1

    def _rows_with_key(self, key: str) -> list[int]:
        return [row for row in range(self.table.rowCount())
                if (it := self.table.item(row, COL_NAME)) is not None
                and it.data(Qt.UserRole) == key]

    def _set_row_result(self, res: CheckResult) -> None:
        key = self._app_key(res.app_name, res.installed_version)
        row = self._find_row(key)
        if row < 0:
            return
        latest = res.latest_version or "-"
        latest_item = self._item(latest)
        if res.status == "update" and res.latest_version and res.size_bytes > 0:
            size_text = format_size(res.size_bytes)
            latest = f"{res.latest_version}  \u00b7  {size_text}"
            latest_item = self._item(latest)
            # The delegate draws the size part in accent green (user request).
            latest_item.setData(LATEST_SIZE_ROLE,
                                (str(res.latest_version), size_text))
        self.table.setItem(row, COL_LATEST, latest_item)
        status_item = self._item(_status_label(res.status))
        status_item.setForeground(QColor(STATUS_COLOR.get(res.status, theme.TEXT)))
        if (note_text := res.note_text()):
            # Wrap long explanations (e.g. "Managed by vendor") so the
            # tooltip stays a readable box instead of one huge line.
            status_item.setToolTip(textwrap.fill(note_text, 64))
        self.table.setItem(row, COL_STATUS, status_item)
        self.table.setItem(row, COL_SOURCE,
                           self._item(_l10n_source(res.source_label or "-")))
        self._checking_keys.discard(
            self._app_key(res.app_name, res.installed_version))

    def _apply_filter(self, text: str) -> None:
        q = (text or "").strip().lower()
        for row in range(self.table.rowCount()):
            name_it = self.table.item(row, COL_NAME)
            pub_it = self.table.item(row, COL_PUB)
            hay = f"{name_it.text() if name_it else ''} {pub_it.text() if pub_it else ''}".lower()
            self.table.setRowHidden(row, bool(q) and q not in hay)

    def _set_counts(self) -> None:
        total = len(self.apps)
        checked = len(self.results)
        updates = sum(1 for r in self.results.values() if r.status == "update")
        self.counts_label.setText(tr(
            "msg.counts", total=total, checked=checked, updates=updates))

    def _set_busy(self, busy: bool) -> None:
        for b in (self.btn_check, self.btn_check_sel, self.btn_download,
                  self.btn_refresh):
            b.setEnabled(not busy)

    # ------------------------------------------------------------- actions
    def _on_refresh_clicked(self) -> None:
        if self._check_worker or self._download_worker:
            return
        self._load_apps()

    def _selected_apps(self) -> list[InstalledApp]:
        apps = []
        for rng in self.table.selectedRanges():
            for row in range(rng.topRow(), rng.bottomRow() + 1):
                it = self.table.item(row, COL_NAME)
                if it is None:
                    continue
                key = it.data(Qt.UserRole)
                for app in self.apps:
                    if self._app_key(app.name, app.version) == key:
                        apps.append(app)
                        break
        return apps

    def _start_check(self, apps: list[InstalledApp]) -> None:
        if self._check_worker or self._download_worker or not apps:
            return
        self._set_busy(True)
        self.progress.setVisible(True)
        self.progress.setRange(0, max(1, len(apps)))
        self.progress.setValue(0)
        self._set_status(tr("msg.checking_n", n=len(apps)), "amber")
        self.table.setSortingEnabled(False)
        # Immediate per-row feedback while the worker re-scans and checks.
        for app in apps:
            key = self._app_key(app.name, app.version)
            self._checking_keys.add(key)
            for row in self._rows_with_key(key):
                st = self.table.item(row, COL_STATUS)
                if st is not None:
                    st.setText(tr("status.checking"))
                    st.setForeground(QColor(STATUS_COLOR["pending"]))
        worker = CheckWorker(apps)
        self._check_scope = len(apps)
        worker.app_checked.connect(self._on_app_checked)
        worker.app_version_refreshed.connect(self._on_version_refreshed)
        worker.progress.connect(self._on_progress)
        worker.finished_all.connect(self._on_check_finished)
        # NOTE: no finished->deleteLater here. The worker is retired explicitly
        # in _on_check_finished (waiting for full thread termination first) -
        # destroying it earlier can abort the whole process (qFatal).
        self._check_worker = worker
        worker.start()

    def _on_check_all(self) -> None:
        try:
            self._start_check(list(self.apps))
        except Exception as exc:
            self._show_error(exc)

    def _on_check_selected(self) -> None:
        try:
            apps = self._selected_apps()
            if not apps:
                self._set_status(tr("msg.select_first"), "amber")
                return
            self._start_check(apps)
        except Exception as exc:
            self._show_error(exc)

    # worker slots (main thread, guarded)
    def _on_app_checked(self, res) -> None:
        try:
            # The user skipped THIS latest version of the app: keep the row
            # honest ("Version skipped") instead of nagging with the update.
            if res.status == "update" and res.latest_version:
                skipped_ver = self._skipped.get(normalize_name(res.app_name))
                if skipped_ver and skipped_ver == res.latest_version:
                    res.status = "skipped"
                    res.set_note("note.skipped", version=skipped_ver)
            elif res.status == "failed":
                # UniGetUI behaviour: a failed RE-check never wipes what a
                # previous run already found. Keep the last known latest
                # version/source on the row (the status stays a red "Check
                # failed" with the reason) so a flaky network cannot erase
                # good information the user was already shown.
                prev = self.results.get(
                    self._app_key(res.app_name, res.installed_version))
                if prev is not None and prev.latest_version:
                    res.latest_version = prev.latest_version
                    res.size_bytes = prev.size_bytes or 0
                    # the previous run also had a downloadable installer -
                    # keep it so Download stays available on flaky days
                    res.installer_url = prev.installer_url or ""
                    res.sha256 = prev.sha256 or ""
                    res.alt_urls = tuple(getattr(prev, "alt_urls", ()) or ())
                    if prev.source_label:
                        res.source_label = prev.source_label
                    res.note_parts = list(prev.note_parts)
                    res.note = prev.note
                    if (res.note_text()):
                        res.add_note("msg.last_known_tail")
                    else:
                        res.set_note("msg.last_known_tail")
            self.results[self._app_key(res.app_name, res.installed_version)] = res
            self._set_row_result(res)
            self._set_counts()
            # Post-install auto re-check: a confirming result arrived for a
            # name the watcher triggered. 'Up to date' means the user's
            # install really landed - remember it for the finish message.
            name_l = (res.app_name or "").strip().lower()
            if name_l and name_l in self._post_install_names:
                self._post_install_names.discard(name_l)
                if res.status == "latest":
                    self._post_install_confirmed.append(
                        (res.app_name, res.installed_version or ""))
                    applog.event(
                        f"Post-install confirmed: {res.app_name} "
                        f"{res.installed_version or '?'} is up to date")
            if res.status == "update":
                applog.event(
                    f"Update found: {res.app_name} "
                    f"{res.installed_version or '?'} -> {res.latest_version} "
                    f"({res.source_label})")
            elif res.status == "failed":
                applog.error(f"Check failed: {res.app_name} - {res.note_text()}")
        except Exception as exc:
            self._show_error(exc)

    def _on_progress(self, done: int, total: int) -> None:
        try:
            self.progress.setMaximum(max(1, total))
            self.progress.setValue(done)
        except Exception:
            pass

    def _on_check_finished(self, updates: int, failed: int, total: int) -> None:
        try:
            worker, self._check_worker = self._check_worker, None
            _retire_worker(worker)
            self._set_busy(False)
            self.progress.setVisible(False)
            self.progress.setValue(self.progress.maximum())
            # skipped versions are deliberately not counted as updates
            real_updates = sum(1 for r in self.results.values()
                               if r.status == "update")
            msg = tr("msg.done", n=real_updates)
            if failed:
                msg += tr("msg.done_failed_tail", n=failed)
            # Post-install auto re-check finished: the confirmation is the
            # headline the user is waiting for - say it clearly + toast.
            if self._post_install_confirmed:
                bits = [tr("msg.postinstall_updated", name=n, version=v) if v
                        else tr("msg.postinstall_uptodate", name=n)
                        for n, v in self._post_install_confirmed]
                msg = "; ".join(bits)
                for n, v in self._post_install_confirmed:
                    self._notify_installed(n, v)
            self._post_install_confirmed.clear()
            self._post_install_names.clear()
            self._set_status(msg + ".", "accent")
            self._set_counts()
            # Automatic result order (user request): after a 100% check the
            # table groups itself - updates on top, then up-to-date, then
            # no-source, errors last - alphabetical inside every group.
            # NOTE: header-click sorting stays OFF after this on purpose -
            # setSortingEnabled(True) re-sorts the whole table by the
            # default sort indicator (name, DESCENDING) and would wipe the
            # automatic order the user asked for.
            self.table.setSortingEnabled(False)
            if self.apps and self._check_scope >= len(self.apps):
                self._sort_rows_by_outcome()
            self._check_scope = 0
            self._update_tray_tooltip(real_updates)
            if self._auto_run:
                applog.event(
                    f"Automatic check finished: {real_updates} update(s), "
                    f"{failed} failed, {total} app(s)")
                if real_updates:
                    self._notify_updates(real_updates)
            self._auto_run = False
        except Exception as exc:
            self._show_error(exc)

    # ------------------------------------------------ automatic result order
    def _sort_rows_by_outcome(self) -> None:
        """Re-order the rows after a finished check: updates on top, then
        up-to-date, then no-source, errors last - alphabetical (natural,
        case-insensitive) inside every group. Selection is preserved."""
        try:
            n = self.table.rowCount()
            if n < 2:
                return

            def sort_key(row: int):
                name_it = self.table.item(row, COL_NAME)
                key = name_it.data(Qt.UserRole) if name_it else ""
                res = self.results.get(key)
                rank = _STATUS_ORDER.get(res.status if res else "pending", 6)
                name = name_it.text() if name_it else ""
                version = ""
                ver_it = self.table.item(row, COL_INSTALLED)
                if ver_it is not None:
                    version = ver_it.text()
                return (rank, _natural_name_key(name),
                        _natural_name_key(version), row)

            order = sorted(range(n), key=sort_key)
            if order != list(range(n)):
                self._reorder_rows(order)
        except Exception as exc:
            self._show_error(exc)

    def _reorder_rows(self, order: list) -> None:
        """Physically move whole rows into `order` (list of old row indexes).
        Cell ITEMS are moved (icons, colors, tooltips, roles travel with
        them), selection and the search filter are re-applied afterwards."""
        table = self.table
        selected_keys = set()
        try:
            for it in table.selectedItems():
                key = it.data(Qt.UserRole)
                if key:
                    selected_keys.add(key)
        except Exception:
            pass
        table.setSortingEnabled(False)
        table.setUpdatesEnabled(False)
        try:
            rows_items = []
            for r in range(table.rowCount()):
                rows_items.append([table.takeItem(r, c) for c in range(6)])
            table.setRowCount(0)
            for new_r, old_r in enumerate(order):
                table.insertRow(new_r)
                for c, it in enumerate(rows_items[old_r]):
                    if it is not None:
                        table.setItem(new_r, c, it)
        finally:
            table.setUpdatesEnabled(True)
        if selected_keys:
            for r in range(table.rowCount()):
                it = table.item(r, COL_NAME)
                if it is not None and it.data(Qt.UserRole) in selected_keys:
                    it.setSelected(True)
        self._apply_filter(self.search.text())
        table.resizeRowsToContents()

    def _on_version_refreshed(self, old_key: str, fresh_version: str) -> None:
        """The worker's fresh registry scan found a different installed
        version (the user installed a downloaded update). Update the row's
        version + key BEFORE the result arrives so 'Up to date' lands on the
        right row. Runs on the UI thread via a queued signal."""
        try:
            fresh_version = (fresh_version or "").strip()
            if not fresh_version:
                return
            new_key = None
            for row in self._rows_with_key(old_key):
                it = self.table.item(row, COL_NAME)
                if it is None:
                    continue
                if new_key is None:
                    new_key = self._app_key(it.text(), fresh_version)
                it.setData(Qt.UserRole, new_key)
                inst = self.table.item(row, COL_INSTALLED)
                if inst is not None:
                    inst.setText(fresh_version)
                st = self.table.item(row, COL_STATUS)
                if st is not None:
                    st.setText(tr("status.checking"))
                    st.setForeground(QColor(STATUS_COLOR["pending"]))
            # Keep self.apps in sync so selection/downloads use fresh data.
            for app in self.apps:
                if self._app_key(app.name, app.version) == old_key:
                    app.version = fresh_version
            if new_key:
                self.results.pop(old_key, None)
                self._checking_keys.discard(old_key)
                self._checking_keys.add(new_key)
        except Exception as exc:
            self._show_error(exc)

    # ------------------------------------------------------------- download
    def _on_download_selected(self) -> None:
        try:
            if self._check_worker or self._download_worker:
                return
            jobs = []
            for app in self._selected_apps():
                res = self.results.get(self._app_key(app.name, app.version))
                if res and res.installer_url:
                    jobs.append((app.name, res.installer_url,
                                 res.sha256 or "", res.size_bytes or 0,
                                 tuple(getattr(res, "alt_urls", ()) or ())))
            if not jobs:
                self._set_status(tr("msg.no_jobs"), "amber")
                return
            self._start_download(jobs)
        except Exception as exc:
            self._show_error(exc)

    def _start_download(self, jobs: list) -> None:
        """Start a DownloadWorker for (name, url[, sha256]) jobs."""
        if self._check_worker or self._download_worker or not jobs:
            return
        self._set_busy(True)
        self.progress.setVisible(False)
        self._dl_paused = False
        self.btn_pause.setText(tr("btn.pause"))
        self.btn_pause.setEnabled(True)
        self.btn_cancel_dl.setEnabled(True)
        self.dl_bar.setRange(0, 0)
        self.dl_bar.setValue(0)
        self.dl_meta.setText("")
        self._dl_total = len(jobs)
        self._dl_done = 0
        self.dl_title.setText(
            tr("msg.preparing_n", n=len(jobs)) if len(jobs) > 1
            else tr("msg.preparing_one"))
        self.dl_panel.setVisible(True)
        self._set_status(tr("msg.downloading_n", n=len(jobs)), "accent")
        applog.event(
            f"Download started: {len(jobs)} installer(s) "
            f"({sum(1 for j in jobs if len(j) > 2 and j[2])} with SHA-256 check)")
        worker = DownloadWorker(jobs)
        worker.item_progress.connect(self._on_dl_progress)
        worker.item_state.connect(self._on_dl_state)
        worker.item_done.connect(self._on_download_done)
        worker.finished_all.connect(self._on_download_finished)
        # NOTE: no finished->deleteLater (see _start_check) - the worker
        # is retired explicitly in _on_download_finished.
        self._download_worker = worker
        worker.start()

    # ------------------------------------------------- download panel slots
    def _on_dl_progress(self, name: str, pct: int, done: int,
                        total: int, speed: float) -> None:
        try:
            if pct < 0:
                self.dl_bar.setRange(0, 0)  # busy indicator (size unknown)
            else:
                self.dl_bar.setRange(0, 100)
                self.dl_bar.setValue(pct)
            parts = [format_size(done)]
            if total > 0:
                parts.append(tr("msg.of_total", total=format_size(total)))
            sp = format_speed(speed)
            if sp:
                parts.append(sp)
            self.dl_meta.setText(" \u00b7 ".join(parts))
        except Exception:
            pass

    def _on_dl_state(self, name: str, state: str) -> None:
        try:
            if state == "paused":
                self._dl_paused = True
                self.btn_pause.setText(tr("btn.resume"))
                self._iconize(self.btn_pause, "play", 13)
                self.btn_pause.setEnabled(True)
                self.dl_title.setText(
                    tr("msg.dl_title_paused", name=self._dl_title_text(name)))
                self._set_status(tr("msg.paused_row", name=name), "amber")
            elif state == "downloading":
                self._dl_paused = False
                self.btn_pause.setText(tr("btn.pause"))
                self._iconize(self.btn_pause, "pause", 13)
                self.btn_pause.setEnabled(True)
                self.dl_title.setText(self._dl_title_text(name))
        except Exception:
            pass

    def _dl_title_text(self, name: str) -> str:
        """Queue-aware download panel title: 'App  (2/5)'."""
        if self._dl_total > 1:
            return f"{name}  ({min(self._dl_done + 1, self._dl_total)}/{self._dl_total})"
        return name

    def _on_pause_clicked(self) -> None:
        try:
            worker = self._download_worker
            if worker is None:
                return
            if self._dl_paused:
                self.btn_pause.setEnabled(False)  # until the state arrives
                worker.resume()
            else:
                self.btn_pause.setEnabled(False)
                worker.pause()
        except Exception as exc:
            self._show_error(exc)

    def _on_cancel_download(self) -> None:
        try:
            worker = self._download_worker
            if worker is None:
                return
            self.btn_cancel_dl.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self._set_status(tr("msg.cancelling"), "amber")
            worker.cancel()
        except Exception as exc:
            self._show_error(exc)

    def _on_download_done(self, name: str, ok: bool, info: str,
                          sha_state: str = "unchecked") -> None:
        try:
            self._dl_done += 1
            if ok:
                # Start the post-install watcher RIGHT AWAY: from now on the
                # registry is polled locally and the moment the user finishes
                # installing (version changes) this app is re-checked
                # automatically - no manual 'Re-check this app' needed.
                self._start_post_install_watch(name)
                if sha_state == "verified":
                    base = tr("msg.saved_verified", path=info)
                else:
                    base = tr("msg.saved", path=info)
                if self.chk_open.isChecked():
                    self._set_status(
                        f"{base}. {tr('msg.after_install_open')}", "accent")
                    self._open_installer(info)
                else:
                    self._set_status(
                        f"{base}. {tr('msg.after_install')}", "accent")
            else:
                self._set_status(
                    tr("msg.dl_failed", name=name, info=info), "danger")
                applog.error(f"Download failed: {name} - {info}")
        except Exception:
            pass

    def _open_installer(self, path: str) -> None:
        """Open a downloaded installer so the user can run the update now
        (explicitly requested convenience; the file itself is never touched
        by this app - Windows' own shell launches it, with its UAC prompt).
        If the shell cannot open it, say so clearly and reveal the folder
        instead - the file is verified on disk, so this path is rare."""
        try:
            if os.name == "nt":
                os.startfile(path)  # noqa: S606 - ShellExecute on the saved file
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as exc:
            applog.error(f"Could not open installer {path}: "
                         f"{exc.__class__.__name__}: {exc}")
            try:
                folder = os.path.dirname(path) or "."
                if os.name == "nt":
                    os.startfile(folder)  # noqa: S606 - opens Explorer only
                else:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
                QMessageBox.information(
                    self, tr("app.name"),
                    tr("msgbox.open_fail_text", err=exc, path=path))
            except Exception:
                self._set_status(
                    tr("msg.could_not_open", err=exc, path=path), "danger")

    def _on_open_toggled(self, checked: bool) -> None:
        try:
            app_settings.save_open_installer(bool(checked))
        except Exception:
            pass

    def _on_download_finished(self, ok: int, fail: int) -> None:
        try:
            worker, self._download_worker = self._download_worker, None
            _retire_worker(worker)
            self._dl_paused = False
            self._set_busy(False)
            self.dl_panel.setVisible(False)
            self.progress.setRange(0, 1)
            self.progress.setValue(0)
            msg = tr("msg.dl_finished", ok=ok)
            if fail:
                msg += tr("msg.dl_finished_failed_tail", n=fail)
            if ok:
                msg += tr("msg.dl_finished_files_tail", path=download_dir())
            else:
                msg += tr("msg.dl_finished_none_tail")
            self._set_status(msg, "danger" if fail else "accent")
            applog.event(f"Download run finished: {ok} ok, {fail} failed")
        except Exception as exc:
            self._show_error(exc)

    # ------------------------------------------- post-install auto re-check
    def _start_post_install_watch(self, name: str) -> None:
        """Watch ONE downloaded app so its row flips to 'Up to date' by
        itself as soon as the user installs the update. Local registry polls
        only - nothing here touches the network until the install is actually
        detected (then the normal single-app re-check runs once)."""
        try:
            name_l = (name or "").strip().lower()
            if not name_l:
                return
            for app in self.apps:
                if (app.name or "").strip().lower() != name_l:
                    continue
                key = self._app_key(app.name, app.version)
                self._watch_keys.add(key)
                self._watch_deadline[key] = time.time() + WATCH_WINDOW_SEC
                self._watch_timer.start(int(WATCH_POLL_SEC * 1000))
                applog.event(
                    f"Watching for install completion: {app.name} "
                    f"(auto re-check within {WATCH_WINDOW_SEC // 60} min)")
                return
        except Exception:
            pass

    def _stop_watch_timer_if_empty(self) -> None:
        try:
            if not self._watch_keys:
                self._watch_timer.stop()
        except Exception:
            pass

    def _on_watch_tick(self) -> None:
        """Timer tick: purge expired watches, then (if nothing else is
        running) scan the registry OFF the UI thread for version changes."""
        try:
            if not self._watch_keys:
                self._watch_timer.stop()
                return
            now = time.time()
            for key in [k for k, dl in self._watch_deadline.items()
                        if dl <= now]:
                self._watch_keys.discard(key)
                self._watch_deadline.pop(key, None)
                applog.event(f"Post-install watch window ended: {key}")
            if not self._watch_keys:
                self._watch_timer.stop()
                return
            if self._watch_scan_worker is not None:
                return  # previous scan still running - wait for it
            if self._check_worker is not None or self._download_worker is not None:
                return  # a check/download is running - next tick catches up
            apps = []
            for key in list(self._watch_keys):
                app = self._app_by_key(key)
                if app is None:
                    # row disappeared (hidden/removed) - stop watching it
                    self._watch_keys.discard(key)
                    self._watch_deadline.pop(key, None)
                    continue
                apps.append(app)
            if not apps:
                self._stop_watch_timer_if_empty()
                return
            worker = VersionWatchWorker(apps)
            self._watch_scan_worker = worker
            worker.fresh_versions.connect(self._on_watch_fresh)
            worker.start()
        except Exception as exc:
            self._show_error(exc)

    def _on_watch_fresh(self, changed) -> None:
        """Version change(s) detected by the local scan: fire the normal
        single-app re-check (queued signal, main thread)."""
        try:
            worker, self._watch_scan_worker = self._watch_scan_worker, None
            _retire_worker(worker)
            if not changed:
                self._stop_watch_timer_if_empty()
                return
            for name, old_ver, fresh in changed:
                key = self._app_key(name, old_ver)
                if key not in self._watch_keys:
                    continue
                # Re-checked EVERY iteration (live state, not a snapshot):
                # the first triggered re-check occupies the worker - the next
                # app then stays watched and is retried on a later tick
                # (never dropped silently).
                if self._check_worker is not None \
                        or self._download_worker is not None:
                    continue  # keep watching; retry on the next tick
                self._watch_keys.discard(key)
                self._watch_deadline.pop(key, None)
                self._post_install_names.add((name or "").strip().lower())
                applog.event(
                    f"Installed version changed: {name} "
                    f"{old_ver or '?'} -> {fresh} - auto re-check starts")
                self._set_status(
                    tr("msg.updated_rechecking", name=name, version=fresh),
                    "accent")
                self._recheck_single(key)
            self._stop_watch_timer_if_empty()
        except Exception as exc:
            self._show_error(exc)

    # ------------------------------------------------------------- settings
    def _on_settings(self) -> None:
        try:
            hidden_count = len(app_settings.load_hidden_apps())
            skipped_count = len(app_settings.load_skipped_versions())
            dlg = app_settings.SettingsDialog(
                self._font_pt, hidden_count, skipped_count, self)
            dlg.hidden_restored.connect(self._on_hidden_restored)
            dlg.skipped_restored.connect(self._on_skipped_restored)
            dlg.backup_export.connect(self._export_apps)
            dlg.backup_import.connect(self._import_apps)
            dlg.open_log_folder.connect(self._open_log_folder)
            dlg.language_changed.connect(self._on_language_changed)
            dlg.tour_requested.connect(self._show_tour_again)
            dlg.exec()
            if dlg.result() == QDialog.Accepted:
                self._font_pt = dlg.final_pt()
                app_settings.save_font_pt(self._font_pt)
                # v1.1.4: Done is the ONLY moment the whole-app font changes
                # (the dialog never previews live - no trembling possible).
                self._apply_font_pt(self._font_pt)
                app_settings.save_auto_check(dlg.final_auto_check())
                app_settings.save_check_interval(dlg.final_interval_hours())
                app_settings.save_notifications(dlg.final_notifications())
                dl_dir = dlg.final_download_dir()
                app_settings.save_download_dir(dl_dir)
                set_custom_download_dir(dl_dir)
                self._arm_interval_timer()
                hours = dlg.final_interval_hours()
                if hours:
                    self._set_status(
                        tr("msg.auto_interval_on", hours=hours), "accent")
            else:
                # Cancel: nothing was applied live (v1.1.4), so there is
                # nothing to revert - re-assert the current size anyway.
                self._apply_font_pt(self._font_pt)
        except Exception as exc:
            self._show_error(exc)

    def _on_hidden_restored(self) -> None:
        try:
            self._load_apps()
            self._set_status(tr("msg.hidden_restored"), "accent")
        except Exception as exc:
            self._show_error(exc)

    def _on_skipped_restored(self) -> None:
        """All skipped versions were cleared in Settings: every 'Version
        skipped' row becomes an honest 'Update available' again."""
        try:
            self._skipped = {}
            changed = 0
            for res in self.results.values():
                if res.status == "skipped":
                    res.status = "update"
                    res.clear_note()
                    self._set_row_result(res)
                    changed += 1
            self._set_counts()
            if changed:
                self._set_status(
                    tr("msg.skipped_restored", n=changed), "accent")
        except Exception as exc:
            self._show_error(exc)

    def _open_log_folder(self) -> None:
        try:
            from ..core import applog as _applog

            path = _applog.log_dir()
            os.makedirs(path, exist_ok=True)
            if os.name == "nt":
                os.startfile(path)  # noqa: S606 - opens Explorer only
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as exc:
            self._show_error(exc)

    # --------------------------------------------------------- tray / timer
    @staticmethod
    def _make_tray_icon() -> QIcon:
        """Draw the tray glyph: a rounded dark tile with the accent-green
        up-arrow (no external asset needed)."""
        pm = QPixmap(64, 64)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        try:
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(theme.BG_1))
            p.drawRoundedRect(2, 2, 60, 60, 14, 14)
            p.setBrush(QColor(theme.ACCENT))
            p.drawPolygon(QPolygonF([
                QPointF(32, 11), QPointF(53, 38), QPointF(39, 38),
                QPointF(39, 53), QPointF(25, 53), QPointF(25, 38),
                QPointF(11, 38)]))
        finally:
            p.end()
        return QIcon(pm)

    def _build_tray(self) -> None:
        try:
            tray = QSystemTrayIcon(self._make_tray_icon(), self)
            menu = QMenu(self)
            mpx = theme.scale_px(16, self._font_pt)
            act_open = menu.addAction(ui_icons.icon("logo", mpx),
                                      tr("tray.open"))
            act_open.triggered.connect(self._show_from_tray)
            act_check = menu.addAction(ui_icons.icon("refresh", mpx),
                                       tr("tray.check"))
            act_check.triggered.connect(self._on_check_all)
            menu.addSeparator()
            act_quit = menu.addAction(ui_icons.icon("close", mpx, "danger"),
                                      tr("tray.quit"))
            act_quit.triggered.connect(self.close)
            tray.setContextMenu(menu)
            tray.setToolTip(tr("app.name"))
            tray.activated.connect(self._on_tray_activated)
            tray.show()
            self.tray = tray
        except Exception:
            self.tray = None  # tray is a convenience - never a dependency

    def _on_tray_activated(self, reason) -> None:
        try:
            if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
                self._show_from_tray()
        except Exception:
            pass

    def _show_from_tray(self) -> None:
        try:
            self.showNormal()
            self.raise_()
            self.activateWindow()
        except Exception:
            pass

    def _update_tray_tooltip(self, updates: int) -> None:
        self._tray_updates = int(updates)
        try:
            if self.tray is not None:
                self.tray.setToolTip(
                    tr("tray.tip_updates", n=updates) if updates
                    else tr("tray.tip_ok"))
        except Exception:
            pass

    def _notify_updates(self, count: int) -> None:
        """Windows toast (via the tray icon) after an automatic check.
        Manual checks never interrupt with notifications."""
        try:
            if not app_settings.load_notifications():
                return
            if self.tray is None or not count:
                return
            self.tray.showMessage(
                tr("app.name"),
                tr("toast.updates_body", n=count),
                self.tray.icon(), 9000)
        except Exception:
            pass

    def _notify_installed(self, name: str, version: str) -> None:
        """Windows toast: the watched app was really updated and its row is
        now 'Up to date' (post-install auto re-check confirmation)."""
        try:
            if not app_settings.load_notifications():
                return
            if self.tray is None:
                return
            tail = tr("toast.installed_tail", version=version) if version else ""
            self.tray.showMessage(
                tr("toast.installed_title"),
                tr("toast.installed_body", name=name, tail=tail),
                self.tray.icon(), 6000)
        except Exception:
            pass

    def _arm_interval_timer(self) -> None:
        try:
            if self._interval_timer is None:
                self._interval_timer = QTimer(self)
                self._interval_timer.timeout.connect(self._on_interval_tick)
            hours = app_settings.load_check_interval()
            if hours > 0:
                self._interval_timer.start(hours * 3600 * 1000)
            else:
                self._interval_timer.stop()
        except Exception:
            pass

    def _on_interval_tick(self) -> None:
        try:
            if self.apps and not self._check_worker and not self._download_worker:
                self._auto_run = True
                self._start_check(list(self.apps))
        except Exception:
            pass

    def _apply_font_pt(self, pt: int) -> None:
        """Apply a new base font size to the whole app, live."""
        try:
            app = QApplication.instance()
            if app is None:
                return
            font = app.font()
            font.setPointSize(max(theme.MIN_FONT_PT, min(theme.MAX_FONT_PT, int(pt))))
            app.setFont(font)
            app.setStyleSheet(theme.build_qss(int(pt), rtl=i18n.is_rtl()))
            icon_px = theme.scale_px(20, int(pt))
            self.table.setIconSize(QSize(icon_px, icon_px))
            self.table.verticalHeader().setDefaultSectionSize(
                theme.scale_px(30, int(pt)))
            self.table.resizeRowsToContents()
            self._apply_icon_sizes()   # UI icons follow the font size too
        except Exception:
            pass

    # ------------------------------------------------- language / tour
    def _maybe_show_tour(self) -> None:
        """First launch only (permanently opt-out-able) quick tour."""
        try:
            from .onboarding import maybe_show_tour

            maybe_show_tour(self)
        except Exception:
            pass

    def _show_tour_again(self) -> None:
        """Settings > Appearance > 'Show the quick tour again'."""
        try:
            from .onboarding import TourDialog

            TourDialog(self).exec()
        except Exception as exc:
            self._show_error(exc)

    def _on_language_changed(self, lang: str) -> None:
        """The Settings dialog already applied + saved the language and
        re-texted itself; flip the REST of the app live (direction, QSS,
        every static string, in-flight row states). No restart, no loss."""
        try:
            app = QApplication.instance()
            if app is not None:
                app.setLayoutDirection(
                    Qt.RightToLeft if i18n.is_rtl() else Qt.LeftToRight)
            self._apply_font_pt(self._font_pt)  # rebuilds the QSS (RTL rules)
            self.retranslate_ui()
        except Exception as exc:
            self._show_error(exc)

    def retranslate_ui(self) -> None:
        """Re-text every static string IN PLACE (live language switch)."""
        self.setWindowTitle(tr("win.title"))
        self.title_label.setText("SoftUpdater")
        self.subtitle_label.setText(windows_summary_l10n())
        self.arch_chip.setText(
            tr("bits.64") if os_bitness() == 64 else tr("bits.32"))
        self.search.setPlaceholderText(tr("search.placeholder"))
        self.btn_refresh.setText(tr("btn.refresh"))
        self.btn_refresh.setToolTip(tr("tip.refresh"))
        self.btn_open_dir.setText(tr("btn.open_dir"))
        self.btn_settings.setText(tr("btn.settings"))
        self.btn_settings.setToolTip(tr("tip.settings"))
        self.btn_check.setText(tr("btn.check_all"))
        self.btn_check.setToolTip(tr("tip.check_all"))
        self.btn_check_sel.setText(tr("btn.check_sel"))
        self.btn_check_sel.setToolTip(tr("tip.check_sel"))
        self.btn_download.setText(tr("btn.download"))
        self.btn_download.setToolTip(tr("tip.download"))
        self.chk_open.setText(tr("chk.open"))
        self.chk_open.setToolTip(tr("tip.open"))
        self.btn_pause.setText(
            tr("btn.resume") if self._dl_paused else tr("btn.pause"))
        self._iconize(self.btn_pause,
                      "play" if self._dl_paused else "pause", 13)
        self.btn_pause.setToolTip(tr("tip.pause"))
        self.btn_cancel_dl.setText(tr("btn.cancel"))
        self.btn_cancel_dl.setToolTip(tr("tip.cancel"))
        self.table.setHorizontalHeaderLabels([
            tr("col.app"), tr("col.pub"), tr("col.installed"),
            tr("col.latest"), tr("col.status"), tr("col.source"),
        ])
        if self.tray is not None:
            try:
                menu = self.tray.contextMenu()
                if menu is not None:
                    acts = menu.actions()
                    if len(acts) >= 3:
                        acts[0].setText(tr("tray.open"))
                        acts[1].setText(tr("tray.check"))
                        acts[-1].setText(tr("tray.quit"))
            except Exception:
                pass
        self._update_tray_tooltip(self._tray_updates)
        # rows: re-apply results / in-flight states in the new language
        for row in range(self.table.rowCount()):
            name_it = self.table.item(row, COL_NAME)
            if name_it is None:
                continue
            key = name_it.data(Qt.UserRole)
            res = self.results.get(key)
            if res is not None:
                self._set_row_result(res)
                continue
            st = self.table.item(row, COL_STATUS)
            if st is None:
                continue
            st.setForeground(QColor(STATUS_COLOR["pending"]))
            if key in self._checking_keys:
                st.setText(tr("status.checking"))
            else:
                st.setText(_status_label("pending"))
        self._set_counts()
        if not (self._check_worker or self._download_worker):
            self._set_status(tr("msg.ready"))

    # ------------------------------------------------------------- misc
    def _auto_check_on_start(self) -> None:
        """Optional: run the full check by itself right after startup."""
        try:
            if self.apps and not self._check_worker and not self._download_worker:
                self._start_check(list(self.apps))
        except Exception:
            pass

    def _open_download_dir(self) -> None:
        try:
            path = download_dir()
            if os.name == "nt":
                os.startfile(path)  # noqa: S606 - opens Explorer only
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as exc:
            self._show_error(exc)

    def _on_row_double_clicked(self, item) -> None:
        try:
            row = item.row()
            key_it = self.table.item(row, COL_NAME)
            if key_it is None:
                return
            res = self.results.get(key_it.data(Qt.UserRole))
            if res and res.source_url:
                QDesktopServices.openUrl(QUrl(res.source_url))
        except Exception:
            pass

    # ------------------------------------------------- row context menu
    def _on_context_menu(self, pos) -> None:
        try:
            row = self.table.rowAt(pos.y())
            if row < 0:
                return
            key_it = self.table.item(row, COL_NAME)
            if key_it is None:
                return
            menu = self._build_context_menu(key_it.text(), key_it.data(Qt.UserRole))
            if menu is not None:
                menu.exec(self.table.viewport().mapToGlobal(pos))
        except Exception:
            pass

    def _build_context_menu(self, name: str, key: str) -> QMenu | None:
        """The right-click actions for one app row:
        details / re-check / download / open the official page / skip / hide."""
        if not key:
            return None
        menu = QMenu(self)
        res = self.results.get(key)
        busy = bool(self._check_worker or self._download_worker)
        app = self._app_by_key(key)

        act_details = menu.addAction(
            ui_icons.icon("info", theme.scale_px(16, self._font_pt)),
            tr("menu.details"))
        act_details.setToolTip(tr("tip.menu.details"))
        act_recheck = menu.addAction(
            ui_icons.icon("refresh", theme.scale_px(16, self._font_pt)),
            tr("menu.recheck"))
        act_recheck.setEnabled(not busy)
        act_recheck.setToolTip(tr("tip.menu.recheck"))
        act_dl = menu.addAction(
            ui_icons.icon("download", theme.scale_px(16, self._font_pt),
                          "accent"),
            tr("menu.download"))
        act_dl.setEnabled(bool(res and res.installer_url) and not busy)
        act_src = menu.addAction(
            ui_icons.icon("globe", theme.scale_px(16, self._font_pt)),
            tr("menu.src"))
        act_src.setEnabled(bool(res and res.source_url))
        act_skip = None
        if res and res.status == "update" and res.latest_version:
            act_skip = menu.addAction(
                ui_icons.icon("ban", theme.scale_px(16, self._font_pt),
                              "amber"),
                tr("menu.skip", version=res.latest_version))
            act_skip.setToolTip(tr("tip.menu.skip"))
        elif res and res.status == "skipped" and res.latest_version:
            act_skip = menu.addAction(
                ui_icons.icon("check_circle", theme.scale_px(16, self._font_pt),
                              "accent"),
                tr("menu.unskip", version=res.latest_version))
            act_skip.setToolTip(tr("tip.menu.unskip"))
        menu.addSeparator()
        act_hide = menu.addAction(
            ui_icons.icon("eye_off", theme.scale_px(16, self._font_pt),
                          "danger"),
            tr("menu.hide"))
        act_hide.setToolTip(tr("tip.menu.hide"))

        act_details.triggered.connect(
            lambda: self._show_details(app, key))
        act_recheck.triggered.connect(
            lambda: self._recheck_single(key))
        act_dl.triggered.connect(
            lambda: self._download_single(key))
        act_src.triggered.connect(
            lambda: self._open_source_page(key))
        if act_skip is not None:
            if res.status == "update":
                act_skip.triggered.connect(lambda: self._skip_version(key))
            else:
                act_skip.triggered.connect(lambda: self._unskip_version(key))
        act_hide.triggered.connect(
            lambda: self._hide_app(name))
        return menu

    def _app_by_key(self, key: str) -> InstalledApp | None:
        for app in self.apps:
            if self._app_key(app.name, app.version) == key:
                return app
        return None

    def _recheck_single(self, key: str) -> None:
        """Re-check ONE app: the worker re-scans the registry first, so a
        freshly installed update is detected and the row shows the honest
        'Up to date' - no full-list re-check needed."""
        try:
            app = self._app_by_key(key)
            if app is None:
                return
            self._start_check([app])
        except Exception as exc:
            self._show_error(exc)

    def _download_single(self, key: str) -> None:
        try:
            res = self.results.get(key)
            if res and res.installer_url:
                self._start_download(
                    [(res.app_name, res.installer_url, res.sha256 or "",
                      res.size_bytes or 0,
                      tuple(getattr(res, "alt_urls", ()) or ()))])
        except Exception as exc:
            self._show_error(exc)

    # ------------------------------------------------- details / skip
    def _show_details(self, app: InstalledApp | None, key: str) -> None:
        try:
            if app is None:
                return
            dlg = _DetailsDialog(app, self.results.get(key), self,
                                 icon=self._icons_by_name.get(app.name))
            dlg.exec()
        except Exception as exc:
            self._show_error(exc)

    def _skip_version(self, key: str) -> None:
        try:
            res = self.results.get(key)
            if not (res and res.latest_version):
                return
            skipped = app_settings.load_skipped_versions()
            skipped[normalize_name(res.app_name)] = res.latest_version
            app_settings.save_skipped_versions(skipped)
            self._skipped = skipped
            res.status = "skipped"
            res.set_note("note.skipped", version=res.latest_version)
            self._set_row_result(res)
            self._set_counts()
            self._set_status(
                tr("msg.skip_done", version=res.latest_version,
                   name=res.app_name), "amber")
            applog.event(
                f"Skipped version {res.latest_version} for {res.app_name}")
        except Exception as exc:
            self._show_error(exc)

    def _unskip_version(self, key: str) -> None:
        try:
            res = self.results.get(key)
            if not (res and res.latest_version):
                return
            skipped = app_settings.load_skipped_versions()
            skipped.pop(normalize_name(res.app_name), None)
            app_settings.save_skipped_versions(skipped)
            self._skipped = skipped
            res.status = "update"
            res.clear_note()
            self._set_row_result(res)
            self._set_counts()
            self._set_status(
                tr("msg.unskip_done", version=res.latest_version,
                   name=res.app_name), "accent")
            applog.event(
                f"Un-skipped version {res.latest_version} for {res.app_name}")
        except Exception as exc:
            self._show_error(exc)

    # ----------------------------------------------------- export / import
    def _export_apps(self) -> None:
        try:
            path, _ = QFileDialog.getSaveFileName(
                self, tr("fd.export_title"), "softupdater_apps.json",
                "JSON (*.json)")
            if not path:
                return
            rows = []
            for app in sorted(self.apps, key=lambda a: a.name.lower()):
                res = self.results.get(self._app_key(app.name, app.version))
                rows.append({
                    "name": app.name,
                    "publisher": app.publisher or "",
                    "installed_version": app.version or "",
                    "latest_version": (res.latest_version if res else "") or "",
                    "status": (res.status if res else "pending"),
                    "source_label": (res.source_label if res else "") or "",
                })
            data = {
                "schema": 1,
                "exported_at": datetime.now().isoformat(timespec="seconds"),
                "source": "SoftUpdater",
                "apps": rows,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._set_status(
                tr("msg.exported", n=len(rows), file=os.path.basename(path)),
                "accent")
            applog.event(f"Exported {len(rows)} app(s) -> {path}")
        except Exception as exc:
            self._show_error(exc)

    @staticmethod
    def _parse_export_json(data) -> list[dict]:
        """Accept our own export files (schema key) or a bare {apps:[...]} -
        returns a clean list of dicts, or [] when the file is unrelated."""
        try:
            if not isinstance(data, dict):
                return []
            apps = data.get("apps")
            if data.get("source") not in (None, "SoftUpdater"):
                return []
            if not isinstance(apps, list):
                return []
            out = []
            for item in apps:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()
                if not name:
                    continue
                out.append({
                    "name": name,
                    "publisher": str(item.get("publisher") or ""),
                    "installed_version": str(item.get("installed_version") or ""),
                    "latest_version": str(item.get("latest_version") or ""),
                    "status": str(item.get("status") or ""),
                })
            return out
        except Exception:
            return []

    @staticmethod
    def _import_report(imported: list[dict], index: dict) -> str:
        """Pure helper: compare an exported list with a fresh registry index
        and build a plain-text report (testable without Qt dialogs)."""
        missing: list[str] = []
        need_update: list[str] = []
        ok: list[str] = []
        plain: list[str] = []
        for item in imported:
            norm = normalize_name(item["name"])
            cands = index.get(norm) or []
            if not cands:
                missing.append(item["name"])
                continue
            best = cands[0]
            for cand in cands[1:]:
                if compare_versions(cand.version or "0", best.version or "0") > 0:
                    best = cand
            latest = item.get("latest_version") or ""
            here = best.version or ""
            if item.get("status") == "update" and latest:
                if here and compare_versions(here, latest) >= 0:
                    ok.append(item["name"])
                else:
                    need_update.append(
                        tr("rep.row_update", name=item["name"],
                           here=here or "?", export=latest))
            else:
                plain.append(item["name"])

        def block(title: str, items: list[str]) -> list[str]:
            if not items:
                return []
            lines = [tr("rep.block", title=title, n=len(items))]
            for name in items[:12]:
                lines.append(f"  - {name}")
            if len(items) > 12:
                lines.append("  " + tr("rep.more", n=len(items) - 12))
            return lines

        lines = [tr("rep.header", n=len(imported)), ""]
        lines += block(tr("rep.missing"), missing)
        lines += block(tr("rep.need_update"), need_update)
        lines += block(tr("rep.up_to_date"), ok)
        lines += block(tr("rep.plain"), plain)
        if len(lines) == 2:
            lines.append(tr("rep.nothing"))
        return "\n".join(lines)

    def _import_apps(self) -> None:
        try:
            path, _ = QFileDialog.getOpenFileName(
                self, tr("fd.import_title"), "", "JSON (*.json)")
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            imported = self._parse_export_json(data)
            if not imported:
                QMessageBox.information(
                    self, tr("msgbox.import_none_title"),
                    tr("msgbox.import_none_text"))
                return
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                index = build_fresh_index()
            finally:
                QApplication.restoreOverrideCursor()
            report = self._import_report(imported, index)
            QMessageBox.information(
                self, tr("msgbox.import_none_title"), report)
            applog.event(f"Imported app list from {path} ({len(imported)} apps)")
        except Exception as exc:
            self._show_error(exc)

    def _open_source_page(self, key: str) -> None:
        try:
            res = self.results.get(key)
            if res and res.source_url:
                QDesktopServices.openUrl(QUrl(res.source_url))
        except Exception as exc:
            self._show_error(exc)

    def _hide_app(self, name: str) -> None:
        try:
            name = (name or "").strip()
            if not name:
                return
            names = app_settings.load_hidden_apps()
            if name not in names:
                names.append(name)
                app_settings.save_hidden_apps(names)
            self._remove_rows_by_name(name)
            self._set_status(tr("msg.hidden_one", name=name), "amber")
        except Exception as exc:
            self._show_error(exc)

    def _remove_rows_by_name(self, name: str) -> None:
        """Drop every row of this app (and its results) WITHOUT touching the
        other rows' check results."""
        name_l = name.strip().lower()
        for row in range(self.table.rowCount() - 1, -1, -1):
            it = self.table.item(row, COL_NAME)
            if it is None or (it.text() or "").strip().lower() != name_l:
                continue
            self.results.pop(it.data(Qt.UserRole), None)
            self.table.removeRow(row)
        self.apps = [a for a in self.apps
                     if (a.name or "").strip().lower() != name_l]
        self._apply_filter(self.search.text())
        self._set_counts()

    def _show_error(self, exc: Exception) -> None:
        self._set_status(tr("msg.error", err=exc), "danger")
        try:
            QMessageBox.warning(self, tr("app.name"),
                                tr("msgbox.error_text", err=exc))
        except Exception:
            pass

    def closeEvent(self, event) -> None:  # noqa: N802
        # Stop workers cleanly so the app never crashes while checking or
        # downloading - and NEVER destroy a thread that is still running
        # (Qt aborts the whole process with qFatal if that happens).
        try:
            self._watch_timer.stop()
        except Exception:
            pass
        for worker in (self._check_worker, self._download_worker,
                       self._icon_worker, self._watch_scan_worker):
            if worker is not None:
                try:
                    worker.cancel()
                except Exception:
                    pass
        for worker in (self._check_worker, self._download_worker,
                       self._icon_worker, self._watch_scan_worker):
            if worker is not None:
                try:
                    waited = 0
                    limit = 3000 if worker is self._icon_worker else 10000
                    while worker.isRunning() and waited < limit:
                        worker.wait(250)
                        waited += 250
                except RuntimeError:
                    pass
        super().closeEvent(event)
        # Last resort: if a thread is STILL running (e.g. a hung socket),
        # quitting normally would destroy a live QThread -> crash dialog on
        # exit. Nothing is lost by exiting hard - downloads stream into
        # .part files and are only renamed once complete.
        for worker in (self._check_worker, self._download_worker,
                       self._icon_worker, self._watch_scan_worker):
            try:
                if worker is not None and worker.isRunning():
                    os._exit(0)
            except RuntimeError:
                pass
