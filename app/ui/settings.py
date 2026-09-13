"""User settings (persisted in the registry via QSettings) + Settings dialog.

Exposed preferences (each one mirrors a feature that established updaters
such as Patch My PC / SUMo / UCheck / UniGetUI also offer - kept small):
  * Appearance : base font size (14-20 pt - picked on a PREVIEW box here,
                 applied to the whole app only when Done is pressed), UI
                 language (6 languages, applies live - no restart) and the
                 "show the quick tour again" button
  * Checking   : check on startup, re-check every N hours, tray notifications
  * Downloads  : custom download folder (empty = default Downloads folder)
  * Applications: hidden-apps (ignore) list + skipped-version map, both
                  managed from the row right-click menu and restorable here
  * Backup     : export/import the app list (JSON), open the log folder
  * About      : app version, developer signature (BuiltByAmirali), the
                 OFFICIAL source-code link and the MIT license note - so
                 users can always tell the official build from any fork

Every visible string goes through app.i18n.tr(); retranslate() re-texts
the whole dialog IN PLACE when the user switches language, so switching
never disturbs any other part of the app.
"""
from __future__ import annotations

import json
import os
import sys

from PySide6.QtCore import Qt, QPointF, QSettings, QSize, QTimer, Signal, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QFontMetrics,
    QPainter,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QStyle,
    QStyleOptionSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..i18n import (
    LANGUAGES,
    DEFAULT_LANGUAGE,
    is_rtl,
    language_codes,
    tr,
)
from . import theme
from . import ui_icons

_ORG = "SoftUpdater"
_APP = "SoftUpdater"
_KEY = "ui/font_pt"
_KEY_OPEN = "ui/open_installer_after_download"
# v1.1.4: the app-wide live font preview is GONE (user report: even the
# debounced v1.1.3 version still trembled the page). The slider now only
# drives a PREVIEW box on the Appearance page; the whole-app font changes
# exactly once - when the user presses Done (MainWindow._on_settings).
_KEY_AUTOCHECK = "behavior/auto_check_at_startup"
_KEY_DLDIR = "downloads/folder"
_KEY_HIDDEN = "apps/hidden_names"
_KEY_SKIP = "apps/skipped_versions"
_KEY_INTERVAL = "behavior/check_interval_hours"
_KEY_NOTIFY = "behavior/tray_notifications"
_KEY_LANG = "ui/language"
_KEY_TOUR = "behavior/quick_tour_done"

INTERVAL_CHOICES = [0, 2, 4, 6, 12, 24]   # hours; 0 = off

# One Fluent-style icon per Settings section (same order as _pages()).
_NAV_ICONS = ("shield_check", "download", "grid", "database", "palette",
              "info")

# The one and only official home of the project (developer signature).
OFFICIAL_REPO_URL = "https://github.com/BuiltByAmirali/SoftUpdater"
OFFICIAL_DEVELOPER = "BuiltByAmirali"


def app_version() -> str:
    """Best-effort read of the project VERSION file (for the About page).

    Works from the source tree (VERSION sits next to run.py) and from a
    frozen build when the file was bundled; returns "" when unavailable
    (the About page simply hides the row then)."""
    roots = []
    if getattr(sys, "frozen", False):
        roots.append(getattr(sys, "_MEIPASS", ""))
        roots.append(os.path.dirname(sys.executable))
    try:
        # app/ui/settings.py -> app -> project root (VERSION next to run.py)
        roots.append(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))))
    except Exception:
        pass
    for root in roots:
        if not root:
            continue
        try:
            path = os.path.join(root, "VERSION")
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    value = fh.read().strip()
                if value:
                    return value
        except Exception:
            pass
    return ""


def _settings() -> QSettings:
    return QSettings(_ORG, _APP)


def _to_bool(val, default: bool) -> bool:
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


def load_font_pt() -> int:
    """Read the saved base font size, clamped to the allowed range."""
    try:
        val = int(_settings().value(_KEY, theme.DEFAULT_FONT_PT))
    except Exception:
        val = theme.DEFAULT_FONT_PT
    return max(theme.MIN_FONT_PT, min(theme.MAX_FONT_PT, val))


def save_font_pt(pt: int) -> None:
    try:
        s = _settings()
        s.setValue(_KEY, int(pt))
        s.sync()
    except Exception:
        pass


def load_language() -> str:
    """Saved UI language code, or the default when unset/unknown."""
    try:
        val = str(_settings().value(_KEY_LANG, "") or "").strip()
    except Exception:
        val = ""
    return val if val in language_codes() else DEFAULT_LANGUAGE


def save_language(code: str) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_LANG, str(code))
        s.sync()
    except Exception:
        pass


def load_tour_done() -> bool:
    """True when the user finished (or opted out of) the first-run tour."""
    try:
        return _to_bool(_settings().value(_KEY_TOUR, False), False)
    except Exception:
        return False


def save_tour_done(done: bool) -> None:
    """Stored permanently: only uninstalling the app removes it (the
    uninstaller clears the whole SoftUpdater registry key on purpose)."""
    try:
        s = _settings()
        s.setValue(_KEY_TOUR, bool(done))
        s.sync()
    except Exception:
        pass


def load_open_installer() -> bool:
    """Whether downloaded installers should open automatically (default: on)."""
    try:
        return _to_bool(_settings().value(_KEY_OPEN, True), True)
    except Exception:
        return True


def save_open_installer(enabled: bool) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_OPEN, bool(enabled))
        s.sync()
    except Exception:
        pass


def load_auto_check() -> bool:
    """Check for updates automatically when the app starts (default: off)."""
    try:
        return _to_bool(_settings().value(_KEY_AUTOCHECK, False), False)
    except Exception:
        return False


def save_auto_check(enabled: bool) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_AUTOCHECK, bool(enabled))
        s.sync()
    except Exception:
        pass


def load_download_dir() -> str:
    """Custom download folder, or '' for the default Downloads location."""
    try:
        return str(_settings().value(_KEY_DLDIR, "") or "").strip()
    except Exception:
        return ""


def save_download_dir(path: str) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_DLDIR, (path or "").strip())
        s.sync()
    except Exception:
        pass


def load_hidden_apps() -> list:
    """Apps hidden from the list via the row right-click menu."""
    try:
        raw = _settings().value(_KEY_HIDDEN, "")
        if isinstance(raw, list):  # QSettings may return native lists
            return [str(x) for x in raw if str(x).strip()]
        data = json.loads(str(raw or "[]"))
        if isinstance(data, list):
            return [str(x) for x in data if str(x).strip()]
    except Exception:
        pass
    return []


def save_hidden_apps(names: list) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_HIDDEN, json.dumps([str(n) for n in names if str(n).strip()]))
        s.sync()
    except Exception:
        pass


def load_skipped_versions() -> dict:
    """Apps whose CURRENT latest version the user skipped
    (normalized app name -> skipped version)."""
    try:
        raw = _settings().value(_KEY_SKIP, "")
        data = json.loads(str(raw or "{}"))
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()
                    if str(k).strip() and str(v).strip()}
    except Exception:
        pass
    return {}


def save_skipped_versions(mapping: dict) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_SKIP, json.dumps(
            {str(k): str(v) for k, v in mapping.items()
             if str(k).strip() and str(v).strip()}))
        s.sync()
    except Exception:
        pass


def load_check_interval() -> int:
    """Automatic re-check interval in hours (0 = never)."""
    try:
        val = int(_settings().value(_KEY_INTERVAL, 0))
    except Exception:
        val = 0
    return val if val in INTERVAL_CHOICES else 0


def save_check_interval(hours: int) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_INTERVAL, int(hours) if int(hours) in INTERVAL_CHOICES else 0)
        s.sync()
    except Exception:
        pass


def load_notifications() -> bool:
    """Show a tray notification when a scheduled check finds updates."""
    try:
        return _to_bool(_settings().value(_KEY_NOTIFY, True), True)
    except Exception:
        return True


def save_notifications(enabled: bool) -> None:
    try:
        s = _settings()
        s.setValue(_KEY_NOTIFY, bool(enabled))
        s.sync()
    except Exception:
        pass


class _ArrowSpinBox(QSpinBox):
    """QSpinBox with clean, clearly visible WHITE triangle arrows.

    v1.1.4 (user screenshot): the QSS border-trick arrows rendered as two
    solid white SQUARES - Qt stylesheets cannot draw real triangles. The
    fix is widget-level, not QSS: theme.py hides the built-in arrows
    completely (image:none + 0 size) and this subclass paints crisp
    ANTIALIASED white triangles over the standard up/down sub-control
    rects. QPainter polygons are resolution-independent, follow the real
    sub-control rects (correct even when Qt mirrors the spinbox in RTL),
    and behave identically on Qt6/PySide6 (x64) and Qt5/PyQt5 (Win7/32-bit)
    - no image files, no extra resources, nothing to bundle.
    """

    def paintEvent(self, event):  # noqa: N802 - Qt override
        super().paintEvent(event)
        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)
        style = self.style()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        # White when enabled, dimmed when disabled - matching the QSS
        # disabled text color of the theme.
        painter.setBrush(QColor("#ffffff") if self.isEnabled()
                         else QColor(232, 236, 241, 90))
        up = style.subControlRect(QStyle.CC_SpinBox, opt,
                                  QStyle.SC_SpinBoxUp, self)
        self._paint_triangle(painter, up, up=True)
        down = style.subControlRect(QStyle.CC_SpinBox, opt,
                                    QStyle.SC_SpinBoxDown, self)
        self._paint_triangle(painter, down, up=False)

    @staticmethod
    def _paint_triangle(painter, rect, up=True):
        """One centered triangle inside `rect` (pointing up or down)."""
        if rect.isEmpty():
            return
        arrow_w = max(6.0, min(rect.width() * 0.5, 11.0))
        arrow_h = arrow_w * 0.62
        cx = rect.center().x()
        cy = rect.center().y()
        half_w = arrow_w / 2.0
        half_h = arrow_h / 2.0
        if up:
            tip, left, right = (QPointF(cx, cy - half_h),
                                QPointF(cx - half_w, cy + half_h),
                                QPointF(cx + half_w, cy + half_h))
        else:
            tip, left, right = (QPointF(cx, cy + half_h),
                                QPointF(cx - half_w, cy - half_h),
                                QPointF(cx + half_w, cy - half_h))
        painter.drawPolygon(QPolygonF([tip, left, right]))


class SettingsDialog(QDialog):
    """Settings dialog - horizontal layout: navigation + one section page.

    The old dialog stacked every section in ONE tall narrow column and kept
    whatever window size it had when it opened, so dragging the font slider
    compressed the rows into each other (clipped buttons, truncated path,
    unreadable options at large font sizes). Now a slim navigation panel on
    the left switches between small section pages on the right, the dialog
    re-fits itself after every font change and every hard-coded pixel size
    scales with the font.

    The font slider NO LONGER previews on the whole app (v1.1.4 - the
    user still saw page-trembling with the debounced version). It only
    drives a PREVIEW box on this page; the whole-app font changes exactly
    ONCE when the user presses Done (MainWindow applies final_pt). The
    language combo applies INSTANTLY (and is saved at once - Cancel does
    not undo it, like the other one-way actions). retranslate() re-texts
    every widget in place, so a language switch mid-dialog is seamless.
    """

    hidden_restored = Signal()
    skipped_restored = Signal()
    backup_export = Signal()
    backup_import = Signal()
    open_log_folder = Signal()
    language_changed = Signal(str)   # new language code (already applied)
    tour_requested = Signal()

    def __init__(self, current_pt: int, hidden_count: int = 0,
                 skipped_count: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("set.title"))
        self._original_pt = int(current_pt)
        self._applied_pt = int(current_pt)
        self._original_dl_dir = load_download_dir()
        self._dl_dir = self._original_dl_dir
        self._hidden_count = int(hidden_count)
        self._skipped_count = int(skipped_count)
        self._nav_pages = []   # [(nav_btn, header_label)] for retranslate
        # NOTE: no explicit setMinimumWidth here - the layout's own minimum
        # (font-derived size hints) is the correct lower bound; a hard-coded
        # pixel minimum was one of the causes of the overlap bug.

        outer = QVBoxLayout(self)
        outer.setContentsMargins(self._px(18), self._px(16),
                                 self._px(18), self._px(14))
        outer.setSpacing(self._px(12))

        body = QHBoxLayout()
        body.setSpacing(self._px(12))
        outer.addLayout(body, 1)

        # ------------------------------------------------ left: navigation
        # Frosted panel with one button per section; the right side shows
        # exactly one section at a time, so the dialog stays SHORT and WIDE
        # at any font size (no more screen-height clipping).
        self._side = QFrame(objectName="sidePanel")
        side_lay = QVBoxLayout(self._side)
        side_lay.setContentsMargins(self._px(8), self._px(10),
                                    self._px(8), self._px(10))
        side_lay.setSpacing(self._px(4))
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._stack = QStackedWidget()
        for index, (nav_key, header_key, builder) in enumerate(self._pages()):
            btn = QPushButton(tr(nav_key), objectName="sideNav")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setIcon(ui_icons.icon(_NAV_ICONS[index], self._px(16),
                                      "accent" if index == 0 else "dim",
                                      vshift=ui_icons.shift_for_pt(
                                          self._applied_pt)))
            btn.setIconSize(QSize(self._px(16), self._px(16)))
            btn.clicked.connect(
                lambda _checked=False, i=index: self._stack.setCurrentIndex(i))
            self._nav_group.addButton(btn, index)
            side_lay.addWidget(btn)
            header_lbl = self._section(tr(header_key))
            self._nav_pages.append((btn, header_lbl))
            page = builder(header_lbl)
            self._stack.addWidget(page)
        self._nav_group.button(0).setChecked(True)
        # The checked section's icon lights up in the accent color.
        self._stack.currentChanged.connect(self._sync_nav_icons)
        side_lay.addStretch(1)
        body.addWidget(self._side)
        body.addWidget(self._stack, 1)

        # --------------------------------------------------- bottom: Done
        btns = QHBoxLayout()
        btns.setSpacing(self._px(8))
        self._reset_btn = QPushButton(tr("set.btn.reset_font"))
        self._reset_btn.setToolTip(tr(
            "tip.set.reset_font", default=theme.DEFAULT_FONT_PT))
        self._reset_btn.clicked.connect(self._on_reset)
        self._icon_btn(self._reset_btn, "undo")
        btns.addWidget(self._reset_btn)
        btns.addStretch(1)
        self._done_btn = QPushButton(tr("set.btn.done"), objectName="primary")
        self._done_btn.setDefault(True)
        self._done_btn.clicked.connect(self.accept)
        self._icon_btn(self._done_btn, "check", "on_primary")
        btns.addWidget(self._done_btn)
        outer.addLayout(btns)

        self._refresh_dl_label()
        self._refresh_hidden_label()
        self._refresh_skipped_label()
        self._refit()

    # ---------------------------------------------------------- builders
    def _pages(self):
        """(sidebar key, header key, page builder) for every section."""
        return [
            ("set.nav.checking", "set.header.checking",
             self._build_checking_page),
            ("set.nav.downloads", "set.header.downloads",
             self._build_downloads_page),
            ("set.nav.apps", "set.header.apps", self._build_apps_page),
            ("set.nav.backup", "set.header.backup",
             self._build_backup_page),
            ("set.nav.appearance", "set.header.appearance",
             self._build_appearance_page),
            ("set.nav.about", "set.header.about",
             self._build_about_page),
        ]

    def _build_about_page(self, header: QLabel) -> QWidget:
        """Developer signature + the OFFICIAL project links (v1.1.7).

        This page is the app's identity card: version, developer, the one
        official repository and the license - so users can always tell an
        official build from any modified copy (and a donation link can
        safely live here later, next to the official source link)."""
        page, lay = self._new_page(header)
        card, cl = self._new_card()
        cl.setSpacing(self._px(10))

        # --- brand row: logo tile + name + tagline
        brand = QHBoxLayout()
        brand.setSpacing(self._px(12))
        logo = QLabel()
        logo.setPixmap(ui_icons.pixmap("logo", self._px(52), vshift=0.0))
        logo.setFixedSize(self._px(52), self._px(52))
        logo.setScaledContents(True)
        brand.addWidget(logo, 0, Qt.AlignVCenter)
        name_col = QVBoxLayout()
        name_col.setSpacing(self._px(2))
        self._about_name = QLabel("SoftUpdater")
        name_font = self.font()
        name_font.setPointSize(self._applied_pt + 5)
        name_font.setBold(True)
        self._about_name.setFont(name_font)
        name_col.addWidget(self._about_name)
        self._about_tagline = QLabel(tr("set.about.tagline"))
        self._about_tagline.setObjectName("settingsHint")
        self._about_tagline.setWordWrap(True)
        name_col.addWidget(self._about_tagline)
        brand.addLayout(name_col, 1)
        cl.addLayout(brand)

        # --- version / developer rows (signature)
        ver_row = QHBoxLayout()
        ver_row.setSpacing(self._px(10))
        self._about_ver_cap = QLabel(tr("set.about.version"))
        ver_row.addWidget(self._about_ver_cap)
        ver_row.addStretch(1)
        self._about_ver_val = QLabel(app_version() or "-")
        self._about_ver_val.setObjectName("settingsSection")
        ver_row.addWidget(self._about_ver_val)
        cl.addLayout(ver_row)

        dev_row = QHBoxLayout()
        dev_row.setSpacing(self._px(10))
        self._about_dev_cap = QLabel(tr("set.about.dev"))
        dev_row.addWidget(self._about_dev_cap)
        dev_row.addStretch(1)
        # Literal, NOT translated: this is the developer's signature.
        self._about_dev_val = QLabel(OFFICIAL_DEVELOPER)
        self._about_dev_val.setObjectName("settingsSection")
        dev_font = self.font()
        dev_font.setBold(True)
        self._about_dev_val.setFont(dev_font)
        dev_row.addWidget(self._about_dev_val)
        cl.addLayout(dev_row)

        # --- official source button (opens the browser)
        self._about_src_btn = QPushButton(tr("set.about.source"))
        self._about_src_btn.setToolTip(OFFICIAL_REPO_URL)
        self._about_src_btn.setCursor(Qt.PointingHandCursor)
        self._about_src_btn.clicked.connect(self._open_official_repo)
        self._icon_btn(self._about_src_btn, "globe", "accent")
        cl.addWidget(self._about_src_btn)

        self._about_license = QLabel(tr("set.about.license"))
        self._about_license.setObjectName("settingsHint")
        self._about_license.setWordWrap(True)
        cl.addWidget(self._about_license)

        # --- anti-fake note: the official home is THIS repository
        self._about_official = QLabel(tr("set.about.official"))
        self._about_official.setObjectName("settingsHint")
        self._about_official.setWordWrap(True)
        cl.addWidget(self._about_official)
        self._about_url = QLabel(OFFICIAL_REPO_URL)
        self._about_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._about_url.setObjectName("settingsSection")
        cl.addWidget(self._about_url)

        cl.addStretch(1)
        lay.addWidget(card)
        lay.addStretch(1)
        return page

    def _open_official_repo(self) -> None:
        """Open the one official repository in the system browser."""
        try:
            QDesktopServices.openUrl(QUrl(OFFICIAL_REPO_URL))
        except Exception:
            pass

    def _px(self, v: int) -> int:
        """Font-scaled pixel size (mirrors the QSS scaling of theme.py)."""
        return theme.scale_px(v, self._applied_pt)

    def _icon_btn(self, btn, name: str, role: str = "text",
                  base: int = 15) -> None:
        """One vector icon on a dialog button (dialog font is fixed while
        open, so no live re-scaling is needed here). 'undo' is mirrored for
        right-to-left languages so 'go back' points the right way."""
        try:
            px = self._px(base)
            btn.setIcon(ui_icons.icon(name, px, role,
                                      mirror=(name == "undo" and is_rtl()),
                                      vshift=ui_icons.shift_for_pt(
                                          self._applied_pt)))
            btn.setIconSize(QSize(px, px))
        except Exception:
            pass

    def _sync_nav_icons(self, _index: int = -1) -> None:
        """Checked section = accent icon, the rest stay dim."""
        try:
            for i, (btn, _hdr) in enumerate(self._nav_pages):
                role = "accent" if btn.isChecked() else "dim"
                btn.setIcon(ui_icons.icon(_NAV_ICONS[i], self._px(16), role,
                                          vshift=ui_icons.shift_for_pt(
                                              self._applied_pt)))
        except Exception:
            pass

    def _new_page(self, header: QLabel):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(self._px(6))
        lay.addWidget(header)
        return page, lay

    def _new_card(self):
        card = QFrame(objectName="card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(self._px(14), self._px(12),
                              self._px(14), self._px(12))
        cl.setSpacing(self._px(8))
        return card, cl

    def _build_checking_page(self, header: QLabel) -> QWidget:
        page, lay = self._new_page(header)
        card, cl = self._new_card()
        self.chk_auto = QCheckBox(tr("set.chk_auto"))
        self.chk_auto.setChecked(load_auto_check())
        self.chk_auto.setToolTip(tr("tip.set.chk_auto"))
        cl.addWidget(self.chk_auto)

        crow = QHBoxLayout()
        crow.setSpacing(self._px(8))
        self._interval_caption = QLabel(tr("set.lbl_interval"))
        crow.addWidget(self._interval_caption)
        self.cmb_interval = QComboBox()
        self._fill_interval_combo()
        self.cmb_interval.setToolTip(tr("tip.set.interval"))
        crow.addWidget(self.cmb_interval, 1)
        cl.addLayout(crow)

        self.chk_notify = QCheckBox(tr("set.chk_notify"))
        self.chk_notify.setChecked(load_notifications())
        self.chk_notify.setToolTip(tr("tip.set.notify"))
        cl.addWidget(self.chk_notify)
        self._hint_checking = self._hint(tr("set.hint.checking"))
        cl.addWidget(self._hint_checking)
        lay.addWidget(card)
        lay.addStretch(1)
        return page

    def _fill_interval_combo(self) -> None:
        current = self.cmb_interval.currentData() if \
            self.cmb_interval.count() else None
        self.cmb_interval.blockSignals(True)
        self.cmb_interval.clear()
        for hours in INTERVAL_CHOICES:
            label = tr("set.cmb_never") if hours == 0 \
                else tr("set.cmb_hours", n=hours)
            self.cmb_interval.addItem(label, userData=hours)
        if current is not None:
            idx = self.cmb_interval.findData(current)
            if idx >= 0:
                self.cmb_interval.setCurrentIndex(idx)
        else:
            self.cmb_interval.setCurrentIndex(
                INTERVAL_CHOICES.index(load_check_interval()))
        self.cmb_interval.blockSignals(False)

    def _build_downloads_page(self, header: QLabel) -> QWidget:
        page, lay = self._new_page(header)
        card, cl = self._new_card()
        crow = QHBoxLayout()
        crow.setSpacing(self._px(8))
        self.dl_dir_label = QLabel(objectName="settingsValue")
        # A custom path can be long: let the row squeeze THIS label (never
        # the caption) and elide its middle - the full path stays in the
        # tooltip instead of being chopped off at the window edge.
        self.dl_dir_label.setSizePolicy(QSizePolicy.Ignored,
                                        QSizePolicy.Preferred)
        self._dl_caption = QLabel(tr("set.lbl_save_to"))
        crow.addWidget(self._dl_caption)
        crow.addWidget(self.dl_dir_label, 1)
        cl.addLayout(crow)

        brow = QHBoxLayout()
        brow.setSpacing(self._px(8))
        self._browse_btn = QPushButton(tr("set.btn.browse"))
        self._browse_btn.clicked.connect(self._on_browse)
        self._icon_btn(self._browse_btn, "folder")
        brow.addWidget(self._browse_btn)
        self._reset_dir_btn = QPushButton(tr("set.btn.reset_dir"))
        self._reset_dir_btn.setToolTip(tr("tip.set.reset_dir"))
        self._reset_dir_btn.clicked.connect(self._on_reset_dir)
        self._icon_btn(self._reset_dir_btn, "undo")
        brow.addWidget(self._reset_dir_btn)
        brow.addStretch(1)
        cl.addLayout(brow)

        self._hint_downloads = self._hint(tr("set.hint.downloads"))
        cl.addWidget(self._hint_downloads)
        lay.addWidget(card)
        lay.addStretch(1)
        return page

    def _build_apps_page(self, header: QLabel) -> QWidget:
        page, lay = self._new_page(header)
        card, cl = self._new_card()
        hrow = QHBoxLayout()
        hrow.setSpacing(self._px(8))
        self.hidden_label = QLabel(objectName="settingsHint")
        self._restore_btn = QPushButton(tr("set.btn.restore_hidden"))
        self._restore_btn.setToolTip(tr("tip.set.restore_hidden"))
        self._restore_btn.clicked.connect(self._on_restore)
        self._icon_btn(self._restore_btn, "undo")
        hrow.addWidget(self.hidden_label)
        hrow.addStretch(1)
        hrow.addWidget(self._restore_btn)
        cl.addLayout(hrow)

        srow = QHBoxLayout()
        srow.setSpacing(self._px(8))
        self.skipped_label = QLabel(objectName="settingsHint")
        self._restore_skip_btn = QPushButton(tr("set.btn.restore_skip"))
        self._restore_skip_btn.setToolTip(tr("tip.set.restore_skip"))
        self._restore_skip_btn.clicked.connect(self._on_restore_skipped)
        self._icon_btn(self._restore_skip_btn, "undo")
        srow.addWidget(self.skipped_label)
        srow.addStretch(1)
        srow.addWidget(self._restore_skip_btn)
        cl.addLayout(srow)

        self._hint_apps = self._hint(tr("set.hint.apps"))
        cl.addWidget(self._hint_apps)
        lay.addWidget(card)
        lay.addStretch(1)
        return page

    def _build_backup_page(self, header: QLabel) -> QWidget:
        page, lay = self._new_page(header)
        card, cl = self._new_card()
        # A 2-column grid instead of one long row: three buttons side by
        # side overflowed the window width at large font sizes.
        grid = QGridLayout()
        grid.setHorizontalSpacing(self._px(8))
        grid.setVerticalSpacing(self._px(8))
        self._export_btn = QPushButton(tr("set.btn.export"))
        self._export_btn.setToolTip(tr("tip.set.export"))
        self._export_btn.clicked.connect(self.backup_export.emit)
        self._icon_btn(self._export_btn, "export")
        grid.addWidget(self._export_btn, 0, 0)
        self._import_btn = QPushButton(tr("set.btn.import"))
        self._import_btn.setToolTip(tr("tip.set.import"))
        self._import_btn.clicked.connect(self.backup_import.emit)
        self._icon_btn(self._import_btn, "import")
        grid.addWidget(self._import_btn, 0, 1)
        self._log_btn = QPushButton(tr("set.btn.log"))
        self._log_btn.setToolTip(tr("tip.set.log"))
        self._log_btn.clicked.connect(self.open_log_folder.emit)
        self._icon_btn(self._log_btn, "doc")
        grid.addWidget(self._log_btn, 1, 0)
        cl.addLayout(grid)
        self._hint_backup = self._hint(tr("set.hint.backup"))
        cl.addWidget(self._hint_backup)
        lay.addWidget(card)
        lay.addStretch(1)
        return page

    def _build_appearance_page(self, header: QLabel) -> QWidget:
        page, lay = self._new_page(header)
        card, cl = self._new_card()
        cl.setSpacing(self._px(10))

        # --- language (applies to the WHOLE app instantly, no restart)
        lrow = QHBoxLayout()
        lrow.setSpacing(self._px(10))
        self._lang_caption = QLabel(tr("set.lbl_language"))
        lrow.addWidget(self._lang_caption)
        lrow.addStretch(1)
        from .. import i18n

        self.cmb_language = QComboBox()
        for code, native in LANGUAGES:
            self.cmb_language.addItem(native, userData=code)
        idx = self.cmb_language.findData(i18n.current_language())
        if idx >= 0:
            self.cmb_language.setCurrentIndex(idx)
        self.cmb_language.setToolTip(tr("set.hint.language"))
        self.cmb_language.activated.connect(self._on_language_selected)
        lrow.addWidget(self.cmb_language)
        cl.addLayout(lrow)

        # --- font size
        frow = QHBoxLayout()
        frow.setSpacing(self._px(10))
        self._font_caption = QLabel(tr("set.lbl_font"))
        frow.addWidget(self._font_caption)
        frow.addStretch(1)
        self.value_label = QLabel(
            f"{self._original_pt}{tr('set.pt_suffix')}",
            objectName="settingsValue")
        frow.addWidget(self.value_label)
        cl.addLayout(frow)

        srow = QHBoxLayout()
        srow.setSpacing(self._px(10))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(theme.MIN_FONT_PT, theme.MAX_FONT_PT)
        self.slider.setValue(self._original_pt)
        # v1.1.4: _ArrowSpinBox paints the crisp WHITE triangle arrows
        # (the QSS border-trick rendered as two solid squares).
        self.spin = _ArrowSpinBox()
        self.spin.setRange(theme.MIN_FONT_PT, theme.MAX_FONT_PT)
        self.spin.setValue(self._original_pt)
        self.spin.setSuffix(tr("set.pt_suffix"))
        # No fixed pixel widths: both widgets size themselves from the live
        # font (the old 90px spinbox chopped off the value at large sizes).
        self.slider.valueChanged.connect(self._on_slider)
        self.spin.valueChanged.connect(self._on_spin)
        srow.addWidget(self.slider, 1)
        srow.addWidget(self.spin)
        cl.addLayout(srow)
        self._sync_slider_direction()

        # --- v1.1.4 PREVIEW box: the chosen size is shown HERE (sample
        # text), not on the whole app - the page can no longer tremble
        # while dragging. The box has a FIXED height (sized for the max
        # font) so the dialog never re-flows while the slider moves.
        self._preview_caption = QLabel(tr("set.lbl_preview"),
                                       objectName="settingsSection")
        cl.addWidget(self._preview_caption)
        self._preview_box = QLabel(tr("set.font.sample"),
                                   objectName="fontPreview")
        self._preview_box.setWordWrap(True)
        self._preview_box.setAlignment(Qt.AlignLeading | Qt.AlignVCenter)
        prev_font = self._preview_box.font()
        prev_font.setPixelSize(theme.scale_px(13, theme.MAX_FONT_PT))
        self._preview_box.setFixedHeight(
            QFontMetrics(prev_font).height() * 2 + self._px(16))
        self._update_preview_font(self._original_pt)
        cl.addWidget(self._preview_box)
        cl.addSpacing(self._px(6))   # a little air between box and hint

        self._hint_appearance = self._hint(tr("set.hint.appearance"))
        cl.addWidget(self._hint_appearance)

        # --- quick tour
        trow = QHBoxLayout()
        trow.setSpacing(self._px(10))
        self._tour_btn = QPushButton(tr("set.btn.tour"))
        self._tour_btn.setToolTip(tr("tip.set.tour"))
        self._tour_btn.setCursor(Qt.PointingHandCursor)
        self._tour_btn.clicked.connect(self.tour_requested.emit)
        self._icon_btn(self._tour_btn, "play")
        trow.addWidget(self._tour_btn)
        trow.addStretch(1)
        cl.addLayout(trow)

        lay.addWidget(card)
        lay.addStretch(1)
        return page

    # ---------------------------------------------------------- language
    def _on_language_selected(self, index: int) -> None:
        code = self.cmb_language.itemData(index)
        if not code:
            return
        from .. import i18n

        if code == i18n.current_language():
            return
        i18n.set_language(str(code))
        save_language(str(code))
        self.retranslate()          # this dialog re-texts itself in place
        self.language_changed.emit(str(code))

    def retranslate(self) -> None:
        """Re-text EVERY widget in place (live language switch, no rebuild)."""
        self.setWindowTitle(tr("set.title"))
        for index, (nav_key, header_key, _b) in enumerate(self._pages()):
            btn, header_lbl = self._nav_pages[index]
            btn.setText(tr(nav_key))
            header_lbl.setText(tr(header_key))
        self.chk_auto.setText(tr("set.chk_auto"))
        self.chk_auto.setToolTip(tr("tip.set.chk_auto"))
        self._interval_caption.setText(tr("set.lbl_interval"))
        self._fill_interval_combo()
        self.cmb_interval.setToolTip(tr("tip.set.interval"))
        self.chk_notify.setText(tr("set.chk_notify"))
        self.chk_notify.setToolTip(tr("tip.set.notify"))
        self._hint_checking.setText(tr("set.hint.checking"))
        self._dl_caption.setText(tr("set.lbl_save_to"))
        self._browse_btn.setText(tr("set.btn.browse"))
        self._reset_dir_btn.setText(tr("set.btn.reset_dir"))
        self._reset_dir_btn.setToolTip(tr("tip.set.reset_dir"))
        self._restore_btn.setText(tr("set.btn.restore_hidden"))
        self._restore_btn.setToolTip(tr("tip.set.restore_hidden"))
        self._restore_skip_btn.setText(tr("set.btn.restore_skip"))
        self._restore_skip_btn.setToolTip(tr("tip.set.restore_skip"))
        self._hint_apps.setText(tr("set.hint.apps"))
        self._export_btn.setText(tr("set.btn.export"))
        self._export_btn.setToolTip(tr("tip.set.export"))
        self._import_btn.setText(tr("set.btn.import"))
        self._import_btn.setToolTip(tr("tip.set.import"))
        self._log_btn.setText(tr("set.btn.log"))
        self._log_btn.setToolTip(tr("tip.set.log"))
        self._hint_backup.setText(tr("set.hint.backup"))
        self._lang_caption.setText(tr("set.lbl_language"))
        self.cmb_language.setToolTip(tr("set.hint.language"))
        self._font_caption.setText(tr("set.lbl_font"))
        self.spin.setSuffix(tr("set.pt_suffix"))
        self._sync_slider_direction()   # re-mirror the slider for the new language
        self.value_label.setText(
            f"{self._applied_pt}{tr('set.pt_suffix')}")
        self._preview_caption.setText(tr("set.lbl_preview"))
        self._preview_box.setText(tr("set.font.sample"))
        self._refit()                   # + relayout the dialog in place
        self._tour_btn.setText(tr("set.btn.tour"))
        self._tour_btn.setToolTip(tr("tip.set.tour"))
        self._hint_appearance.setText(tr("set.hint.appearance"))
        self._reset_btn.setText(tr("set.btn.reset_font"))
        self._reset_btn.setToolTip(tr(
            "tip.set.reset_font", default=theme.DEFAULT_FONT_PT))
        self._done_btn.setText(tr("set.btn.done"))
        # About page (signature + official links)
        self._about_tagline.setText(tr("set.about.tagline"))
        self._about_ver_cap.setText(tr("set.about.version"))
        self._about_ver_val.setText(app_version() or "-")
        self._about_dev_cap.setText(tr("set.about.dev"))
        self._about_src_btn.setText(tr("set.about.source"))
        self._about_src_btn.setToolTip(OFFICIAL_REPO_URL)
        self._about_license.setText(tr("set.about.license"))
        self._about_official.setText(tr("set.about.official"))
        self._refresh_dl_label()
        self._refresh_hidden_label()
        self._refresh_skipped_label()

    # ------------------------------------------------------------- sizing
    def _screen_rect(self):
        """Available screen area, or None when it cannot be determined."""
        try:
            scr = self.screen()
            if scr is not None:
                r = scr.availableGeometry()
                if r.isValid():
                    return r
        except Exception:
            pass
        return None

    def _refit(self) -> None:
        """Resize the dialog to fit the CURRENT font size.

        Root-cause fix for the overlap bug: the dialog used to keep the
        size it had when it opened, so growing the font squeezed every row
        into its neighbour. Re-fit after every font change; the sidebar
        minimum and the width floor scale with the font too, and the result
        never exceeds the available screen area."""
        if getattr(self, "_side", None) is not None:
            self._side.setMinimumWidth(self._px(132))
        hint = self.sizeHint()
        want_w = max(int(hint.width()), theme.scale_px(560, self._applied_pt))
        want_h = int(hint.height())
        scr = self._screen_rect()
        if scr is not None:
            want_w = min(want_w, max(scr.width() - 40, 320))
            want_h = min(want_h, max(scr.height() - 40, 240))
        self.resize(want_w, want_h)

    def resizeEvent(self, event):  # noqa: N802 - Qt override
        super().resizeEvent(event)
        # Children may not be re-laid-out yet at this point: refresh the
        # elided path once now and once more on the next event-loop turn.
        # NOTE: QTimer.singleShot(msec, receiver, member) is PySide-only -
        # PyQt5 (the Windows 7 build) has no such overload, so the portable
        # 2-argument form is used (the bound method dies with the dialog).
        self._refresh_dl_label()
        QTimer.singleShot(0, self._refresh_dl_label)

    # ---------------------------------------------------------- builders
    @staticmethod
    def _section(text: str) -> QLabel:
        lbl = QLabel(text, objectName="settingsSection")
        return lbl

    @staticmethod
    def _hint(text: str) -> QLabel:
        lbl = QLabel(text, objectName="settingsHint")
        lbl.setWordWrap(True)
        return lbl

    # ------------------------------------------------------------ slots
    def _sync_slider_direction(self) -> None:
        """v1.1.3 fix: for RTL languages (fa/ar) the font-size slider runs
        the OPPOSITE way of LTR languages - the minimum sits on the RIGHT
        and dragging LEFT increases the size (mirrored, like every proper
        RTL UI); LTR languages keep the normal left-to-right direction.

        The handle/drag mirroring comes from the slider's own RTL layout
        direction - set EXPLICITLY here so the behaviour never depends on
        how the direction happens to propagate from parent widgets. The
        accent fill side is mirrored by theme.build_qss(rtl=True), which
        moves the fill to the min side via the ::add-page rule."""
        self.slider.setLayoutDirection(
            Qt.RightToLeft if is_rtl() else Qt.LeftToRight)

    def _on_slider(self, value: int) -> None:
        self.spin.blockSignals(True)
        self.spin.setValue(value)
        self.spin.blockSignals(False)
        self._apply(value)

    def _on_spin(self, value: int) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self._apply(value)

    def _on_reset(self) -> None:
        self.slider.setValue(theme.DEFAULT_FONT_PT)  # routes through _on_slider

    def _apply(self, value: int) -> None:
        """v1.1.4: track + label the chosen size and grow/shrink ONLY the
        preview box - NOTHING is applied to the app while dragging, so the
        page can never tremble. The whole-app font changes exactly once,
        when the user presses Done (MainWindow._on_settings applies
        final_pt())."""
        self._applied_pt = int(value)
        self.value_label.setText(f"{value}{tr('set.pt_suffix')}")
        self._update_preview_font(value)

    def _update_preview_font(self, value: int) -> None:
        """Show the sample text at the chosen size inside the preview box.
        Same 13px-at-10pt scaling the QSS body text uses, so the preview
        matches what the app will look like after Done."""
        font = self._preview_box.font()
        font.setPixelSize(theme.scale_px(13, int(value)))
        self._preview_box.setFont(font)

    def _on_browse(self) -> None:
        start = self._dl_dir or ""
        chosen = QFileDialog.getExistingDirectory(
            self, tr("fd.choose_dir"), start)
        if chosen:
            self._dl_dir = chosen
            self._refresh_dl_label()

    def _on_reset_dir(self) -> None:
        self._dl_dir = ""
        self._refresh_dl_label()

    def _refresh_dl_label(self) -> None:
        full = self._dl_dir or tr("set.dl_default")
        self.dl_dir_label.setToolTip(full)
        font = self.dl_dir_label.font()
        # Mirror the exact QSS size of QLabel#settingsValue for correct
        # metrics (a widget's font() does not carry stylesheet sizes).
        font.setPixelSize(theme.scale_px(15, self._applied_pt))
        avail = self.dl_dir_label.width()
        if avail > 40:
            self.dl_dir_label.setText(
                QFontMetrics(font).elidedText(full, Qt.ElideMiddle, avail))
        else:
            # Not laid out yet - show the full text; the first resize
            # event re-elides it.
            self.dl_dir_label.setText(full)

    def _on_restore(self) -> None:
        save_hidden_apps([])
        self._hidden_count = 0
        self._refresh_hidden_label()
        self.hidden_restored.emit()

    def _on_restore_skipped(self) -> None:
        save_skipped_versions({})
        self._skipped_count = 0
        self._refresh_skipped_label()
        self.skipped_restored.emit()

    def _refresh_hidden_label(self) -> None:
        n = self._hidden_count
        self.hidden_label.setText(
            tr("set.lbl_hidden_n", n=n) if n else tr("set.lbl_hidden_none"))
        self._restore_btn.setEnabled(n > 0)

    def _refresh_skipped_label(self) -> None:
        n = self._skipped_count
        self.skipped_label.setText(
            tr("set.lbl_skip_n", n=n) if n else tr("set.lbl_skip_none"))
        self._restore_skip_btn.setEnabled(n > 0)

    def set_skipped_count(self, n: int) -> None:
        self._skipped_count = int(n)
        self._refresh_skipped_label()

    # -------------------------------------------------------------- API
    def final_pt(self) -> int:
        """The size chosen on the slider/spinbox - applied to the whole app
        by MainWindow._on_settings AFTER Done (never before)."""
        return self._applied_pt

    def final_auto_check(self) -> bool:
        return bool(self.chk_auto.isChecked())

    def final_download_dir(self) -> str:
        return self._dl_dir or ""

    def final_interval_hours(self) -> int:
        return int(self.cmb_interval.currentData() or 0)

    def final_notifications(self) -> bool:
        return bool(self.chk_notify.isChecked())
