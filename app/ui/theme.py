"""Dark glassmorphism stylesheet (pure QSS - no custom painting = crash-safe).

All font sizes and paddings scale with the user's font-size setting so the
Settings dialog can make the whole app bigger or smaller.
"""
from __future__ import annotations

ACCENT = "#2dd4a7"
ACCENT_HOVER = "#3ee6b8"
BG_0 = "#0e1116"
BG_1 = "#151a22"
CARD = "rgba(255, 255, 255, 0.055)"
CARD_BORDER = "rgba(255, 255, 255, 0.10)"
TEXT = "#e8ecf1"
TEXT_DIM = "#98a2b3"
DANGER = "#e5484d"

# The QSS pixel values below were designed for a 10 pt base font.
QSS_BASE_PT = 10
# v1.1.4 (user request): the font size is restricted to 14-20 pt.
# 14 is also the DEFAULT, so an old saved value (e.g. 11) simply clamps
# up to 14 on the next start (load_font_pt clamps into this range).
DEFAULT_FONT_PT = 14
MIN_FONT_PT = 14
MAX_FONT_PT = 20


def _scale(px_value: int, pt: int) -> int:
    return max(7, round(px_value * pt / float(QSS_BASE_PT)))


def scale_px(px_value: int, pt: int | None = None) -> int:
    """Public pixel scaler for non-QSS UI geometry (icon slots, row heights)
    so hand-set sizes follow the user's font-size setting like the QSS does."""
    return _scale(px_value, DEFAULT_FONT_PT if pt is None else pt)


def build_qss(pt: int = DEFAULT_FONT_PT, rtl: bool = False) -> str:
    """Build the full stylesheet for a given base font size (in points).

    rtl=True mirrors the few direction-aware rules (sidebar nav text,
    combo arrow, hairline borders) for right-to-left languages so the
    glassmorphism stays correct when the whole UI flips."""

    def p(v: int) -> int:
        return _scale(v, pt)

    nav_align = "right" if rtl else "left"
    # The hairline between table cells / header sections sits on the
    # row's end side; mirror it for RTL.
    cell_border_side = "left" if rtl else "right"
    combo_arrow_margin = "margin-left" if rtl else "margin-right"
    # v1.1.3 (RTL slider): Qt anchors the QSS "sub-page" fill to the LEFT
    # groove edge even when the handle itself mirrors, which kept the
    # font-size slider looking LTR in fa/ar (user-reported: "the direction
    # never flips"). For RTL the accent therefore moves to ::add-page,
    # which Qt places on the MIN side (= the right edge), so the fill
    # grows leftwards - a true mirror of the LTR slider. Pure QSS, so
    # both the x64 and the Win7/32-bit builds render identically.
    rtl_slider_fill = ""
    if rtl:
        rtl_slider_fill = f"""
/* RTL slider fill (v1.1.3): see the comment near rtl_slider_fill above. */
QSlider::sub-page:horizontal {{
    background: transparent;
}}
QSlider::add-page:horizontal {{
    background: {ACCENT};
    border-radius: 3px;
}}
"""

    return f"""
* {{
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    color: {TEXT};
    outline: none;
}}
QMainWindow, QWidget#root, QDialog {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0e1116, stop:0.55 #12161f, stop:1 #0b1018);
}}
QFrame#card {{
    background: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: {p(14)}px;
}}
QLabel#appTitle {{
    font-size: {p(22)}px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#appSubtitle {{
    font-size: {p(12)}px;
    color: {TEXT_DIM};
}}
QLabel#chip {{
    background: rgba(45, 212, 167, 0.12);
    border: 1px solid rgba(45, 212, 167, 0.35);
    border-radius: {p(10)}px;
    padding: {p(4)}px {p(10)}px;
    font-size: {p(12)}px;
    color: {ACCENT};
}}
QLabel#statusLabel, QLabel#countsLabel {{
    font-size: {p(12)}px;
    color: {TEXT_DIM};
}}
QLabel#settingsValue {{
    font-size: {p(15)}px;
    font-weight: 700;
    color: {ACCENT};
}}
QLabel#settingsHint {{
    font-size: {p(12)}px;
    color: {TEXT_DIM};
}}
/* v1.1.4: font-size PREVIEW box (Appearance page) - shows the sample text
   at the chosen size BEFORE anything is applied to the app (the whole-app
   font only changes on Done, so dragging can no longer tremble the page).
   No font-size here on purpose: the dialog drives it via setFont so the
   slider can grow/shrink the sample live. */
QLabel#fontPreview {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {CARD_BORDER};
    border-radius: {p(10)}px;
    padding: {p(8)}px {p(12)}px;
    color: {TEXT};
}}
QLabel#dlTitle {{
    font-size: {p(13)}px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel#detailKey {{
    font-size: {p(12)}px;
    color: {TEXT_DIM};
}}
QLabel#detailValue {{
    font-size: {p(13)}px;
    color: {TEXT};
}}
QLabel#detailTitle {{
    font-size: {p(17)}px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#dlMeta {{
    font-size: {p(12)}px;
    color: {TEXT_DIM};
}}
QLabel#settingsSection {{
    font-size: {p(12)}px;
    font-weight: 700;
    color: {ACCENT};
    padding: {p(2)}px {p(2)}px 0 {p(2)}px;
}}
/* Quick tour dialog (first-run tips) */
QLabel#tourTitle {{
    font-size: {p(21)}px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#tourBody {{
    font-size: {p(14)}px;
    color: {TEXT};
}}
QLabel#tourDots {{
    font-size: {p(13)}px;
    color: {TEXT_DIM};
    letter-spacing: {p(2)}px;
}}
/* Settings dialog: horizontal layout - a frosted navigation panel on the
   left, one section page at a time on the right (the old single tall
   column clipped/overlapped at large font sizes). */
QFrame#sidePanel {{
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid {CARD_BORDER};
    border-radius: {p(14)}px;
}}
QPushButton#sideNav {{
    background: transparent;
    border: none;
    border-radius: {p(9)}px;
    padding: {p(9)}px {p(12)}px;
    text-align: {nav_align};
    font-size: {p(13)}px;
    font-weight: 600;
    color: {TEXT_DIM};
}}
QPushButton#sideNav:hover {{
    background: rgba(255, 255, 255, 0.07);
    color: {TEXT};
}}
QPushButton#sideNav:checked {{
    background: rgba(45, 212, 167, 0.14);
    color: {ACCENT};
}}
QPushButton#compact {{
    padding: {p(4)}px {p(14)}px;
    font-size: {p(12)}px;
}}
QLineEdit, QSpinBox {{
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid {CARD_BORDER};
    border-radius: {p(10)}px;
    padding: {p(8)}px {p(12)}px;
    font-size: {p(13)}px;
    selection-background-color: rgba(45, 212, 167, 0.35);
}}
QLineEdit:focus, QSpinBox:focus {{
    border: 1px solid rgba(45, 212, 167, 0.55);
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: rgba(255, 255, 255, 0.08);
    border: none;
    width: {p(16)}px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: rgba(255, 255, 255, 0.16);
}}
/* v1.1.4: the native/QSS arrows rendered as solid white SQUARES (Qt QSS
   cannot draw border-triangles - user screenshot). The arrows are now
   completely HIDDEN here and painted as clean antialiased WHITE triangles
   by the _ArrowSpinBox subclass in settings.py (real QPainter polygons,
   resolution-independent, identical on Qt6/PySide6 and Qt5/PyQt5).
   Up = bigger, down = smaller in every language. */
QSpinBox::up-arrow {{
    image: none;
    width: 0px;
    height: 0px;
}}
QSpinBox::down-arrow {{
    image: none;
    width: 0px;
    height: 0px;
}}
QPushButton {{
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid {CARD_BORDER};
    border-radius: {p(10)}px;
    padding: {p(9)}px {p(16)}px;
    font-size: {p(13)}px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: rgba(255, 255, 255, 0.13);
    border: 1px solid rgba(255, 255, 255, 0.18);
}}
QPushButton:pressed {{
    background: rgba(255, 255, 255, 0.05);
}}
QPushButton:disabled {{
    color: rgba(232, 236, 241, 0.35);
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
}}
QPushButton#primary {{
    background: {ACCENT};
    color: #07120d;
    border: none;
}}
QPushButton#primary:hover {{
    background: {ACCENT_HOVER};
}}
QPushButton#primary:pressed {{
    background: #26bd93;
}}
QPushButton#primary:disabled {{
    background: rgba(45, 212, 167, 0.25);
    color: rgba(7, 18, 13, 0.55);
}}
QCheckBox {{
    background: transparent;
    color: {TEXT};
    font-size: {p(13)}px;
    spacing: {p(8)}px;
    padding: {p(4)}px {p(2)}px;
}}
QCheckBox::indicator {{
    width: {p(17)}px;
    height: {p(17)}px;
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: {p(5)}px;
    background: rgba(255, 255, 255, 0.07);
}}
QCheckBox::indicator:hover {{
    border: 1px solid rgba(45, 212, 167, 0.55);
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border: 1px solid {ACCENT};
}}
QCheckBox::indicator:disabled {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.12);
}}
QTableWidget {{
    background: transparent;
    border: none;
    gridline-color: rgba(255, 255, 255, 0.06);
    alternate-background-color: rgba(255, 255, 255, 0.03);
    selection-background-color: rgba(255, 255, 255, 0.16);
    selection-color: #ffffff;
    font-size: {p(13)}px;
}}
QTableWidget::item {{
    padding: {p(7)}px {p(14)}px;
    border: none;
    border-{cell_border_side}: 1px solid rgba(255, 255, 255, 0.05);
}}
/* Row selection = a frosted white 'glass' band (user request: the old
   faint teal wash was barely visible). Hover = a dimmer preview wash.
   The left glass edge bar of the selected row is painted by the column-0
   delegate (_RowAccentDelegate). */
QTableWidget::item:hover {{
    background: rgba(255, 255, 255, 0.06);
}}
QTableWidget::item:selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.22), stop:1 rgba(255, 255, 255, 0.11));
    color: #ffffff;
}}
/* Right-click context menu: dark glass to match the app (a native white
   menu would look broken on this theme). */
QMenu {{
    background-color: #161c26;
    color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: {p(10)}px;
    padding: {p(6)}px;
    font-size: {p(13)}px;
}}
QMenu::item {{
    background: transparent;
    padding: {p(7)}px {p(20)}px;
    border-radius: {p(7)}px;
}}
QMenu::item:selected {{
    background: rgba(255, 255, 255, 0.14);
    color: #ffffff;
}}
QMenu::item:disabled {{
    color: rgba(232, 236, 241, 0.35);
}}
QMenu::separator {{
    height: 1px;
    background: rgba(255, 255, 255, 0.10);
    margin: {p(5)}px {p(8)}px;
}}
QHeaderView::section {{
    background: rgba(255, 255, 255, 0.04);
    color: {TEXT_DIM};
    border: none;
    border-bottom: 1px solid {CARD_BORDER};
    border-{cell_border_side}: 1px solid rgba(255, 255, 255, 0.06);
    padding: {p(9)}px {p(14)}px;
    font-size: {p(12)}px;
    font-weight: 600;
}}
QTableCornerButton::section {{
    background: transparent;
    border: none;
}}
/* Scrollbar: wide, dim slate handle - easy on the eyes */
QScrollBar:vertical {{
    background: transparent;
    width: {p(14)}px;
    margin: 3px;
}}
QScrollBar::handle:vertical {{
    background: #39424f;
    border-radius: {p(6)}px;
    min-height: {p(36)}px;
}}
QScrollBar::handle:vertical:hover {{
    background: #465163;
}}
QScrollBar::handle:vertical:pressed {{
    background: #526072;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: {p(14)}px;
    margin: 3px;
}}
QScrollBar::handle:horizontal {{
    background: #39424f;
    border-radius: {p(6)}px;
    min-width: {p(36)}px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #465163;
}}
QScrollBar::handle:horizontal:pressed {{
    background: #526072;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
}}
QProgressBar {{
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid {CARD_BORDER};
    border-radius: {p(8)}px;
    height: {p(16)}px;
    text-align: center;
    font-size: {p(11)}px;
    color: {TEXT_DIM};
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: {p(7)}px;
}}
/* Interval combo (Settings): dark glass drop-down matching QLineEdit */
QComboBox {{
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid {CARD_BORDER};
    border-radius: {p(10)}px;
    padding: {p(8)}px {p(12)}px;
    font-size: {p(13)}px;
}}
QComboBox:hover, QComboBox:focus {{
    border: 1px solid rgba(45, 212, 167, 0.55);
}}
QComboBox::drop-down {{
    border: none;
    width: {p(24)}px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: {p(5)}px solid transparent;
    border-right: {p(5)}px solid transparent;
    border-top: {p(6)}px solid {TEXT_DIM};
    {combo_arrow_margin}: {p(10)}px;
}}
QComboBox QAbstractItemView {{
    background-color: #161c26;
    color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: {p(8)}px;
    selection-background-color: rgba(255, 255, 255, 0.14);
    selection-color: #ffffff;
    outline: none;
}}
QStatusBar {{
    background: transparent;
    color: {TEXT_DIM};
    font-size: {p(12)}px;
}}
QStatusBar::item {{
    border: none;
}}
/* Tooltips: with a global stylesheet Qt loses the native tooltip colors
   (white box with nearly-white text = looks empty). Style them explicitly.
   Solid background only - tooltip windows do not support translucency. */
QToolTip {{
    background-color: #1b2230;
    color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 0.20);
    padding: {p(6)}px {p(10)}px;
    font-size: {p(12)}px;
}}
QSlider::groove:horizontal {{
    height: 6px;
    background: rgba(255, 255, 255, 0.14);
    border-radius: 3px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 3px;
}}
{rtl_slider_fill}QSlider::handle:horizontal {{
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 9px;
    background: {ACCENT};
    border: 2px solid #0e1116;
}}
QSlider::handle:horizontal:hover {{
    background: {ACCENT_HOVER};
}}
QSlider::groove:horizontal:disabled, QSlider::sub-page:horizontal:disabled {{
    background: rgba(255, 255, 255, 0.06);
}}
QSlider::handle:horizontal:disabled {{
    background: rgba(255, 255, 255, 0.20);
}}
"""


# Default stylesheet (used until the app applies the saved font size).
QSS = build_qss(DEFAULT_FONT_PT)
