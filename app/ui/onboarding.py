"""First-run quick tour - a few elegant tips, shown ONCE (by default).

The dialog appears on the first launch only (a few pages, in order:
welcome -> right-click power features -> downloads -> personalize).
The user's "don't show these tips again" choice is stored permanently
in QSettings; the uninstaller wipes that key, so a fresh install after
removing the app shows the tour again - exactly as requested.

Everything is drawn with QPainter (no external assets), follows the
app's dark glassmorphism, and inherits the global layout direction
(right-to-left included) automatically.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..i18n import is_rtl, tr
from . import settings as app_settings
from . import theme
from . import ui_icons

# (title key prefix, glyph kind) per page - body key = prefix + ".body"
_PAGES = (
    ("ob.welcome", "welcome"),
    ("ob.ctx", "ctx"),
    ("ob.dl", "dl"),
    ("ob.done", "sliders"),
)


def maybe_show_tour(parent=None) -> None:
    """Show the quick tour when it was never seen (and never opted out)."""
    try:
        if app_settings.load_tour_done():
            return
        dlg = TourDialog(parent)
        dlg.exec()
    except Exception:
        pass


class TourDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("ob.title"))
        self._page = 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(theme.scale_px(28), theme.scale_px(24),
                                 theme.scale_px(28), theme.scale_px(20))
        outer.setSpacing(theme.scale_px(14))

        # --- page stack (one glass card per tip)
        self._stack = QStackedWidget()
        for title_key, glyph in _PAGES:
            self._stack.addWidget(self._build_page(title_key, glyph))
        outer.addWidget(self._stack, 1)

        # --- dots + page counter
        dots_row = QHBoxLayout()
        dots_row.setSpacing(theme.scale_px(8))
        self._dots = QLabel(objectName="tourDots")
        dots_row.addWidget(self._dots, 0, Qt.AlignHCenter)
        self._page_of = QLabel(objectName="tourDots")
        dots_row.addWidget(self._page_of, 0, Qt.AlignHCenter)
        outer.addLayout(dots_row)

        # --- bottom row: "don't show again" + navigation
        bottom = QHBoxLayout()
        bottom.setSpacing(theme.scale_px(8))
        self._chk = QCheckBox(tr("ob.chk.never"))
        bottom.addWidget(self._chk)
        bottom.addStretch(1)
        self._btn_back = QPushButton(tr("ob.btn.back"), objectName="compact")
        self._btn_back.clicked.connect(self._go_back)
        bottom.addWidget(self._btn_back)
        self._btn_skip = QPushButton(tr("ob.btn.skip"), objectName="compact")
        self._btn_skip.clicked.connect(self._skip)
        bottom.addWidget(self._btn_skip)
        self._btn_next = QPushButton(tr("ob.btn.next"), objectName="primary")
        self._btn_next.setDefault(True)
        self._btn_next.clicked.connect(self._go_next)
        bottom.addWidget(self._btn_next)
        outer.addLayout(bottom)
        self._style_nav_buttons()

        self.resize(theme.scale_px(640), theme.scale_px(480))
        self._refresh()

    def _style_nav_buttons(self) -> None:
        """Vector icons on the tour's nav buttons. Direction-aware chevrons:
        'back' points left in LTR and right in RTL (mirrored drawing),
        'next' the opposite way; the final page's button shows a check."""
        try:
            px = theme.scale_px(13)
            self._btn_back.setIcon(ui_icons.icon(
                "chevron", px, "text", mirror=not is_rtl()))
            self._btn_back.setIconSize(QSize(px, px))
            self._btn_skip.setIcon(ui_icons.icon("close", px, "dim"))
            self._btn_skip.setIconSize(QSize(px, px))
            last = self._page >= len(_PAGES) - 1
            self._btn_next.setIcon(ui_icons.icon(
                "check" if last else "chevron", px, "on_primary",
                mirror=(not last) and is_rtl()))
            self._btn_next.setIconSize(QSize(px, px))
        except Exception:
            pass

    # ------------------------------------------------------------------ UI
    def _build_page(self, key_prefix: str, glyph: str) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(theme.scale_px(14))

        icon_lbl = QLabel()
        icon_lbl.setPixmap(_glyph_pixmap(glyph))
        icon_lbl.setAlignment(Qt.AlignHCenter)
        lay.addWidget(icon_lbl)

        title = QLabel(tr(key_prefix + ".title"), objectName="tourTitle")
        title.setAlignment(Qt.AlignHCenter)
        title.setWordWrap(True)
        lay.addWidget(title)

        body = QLabel(tr(key_prefix + ".body"), objectName="tourBody")
        body.setAlignment(Qt.AlignHCenter)
        body.setWordWrap(True)
        lay.addWidget(body, 1)
        return page

    # ------------------------------------------------------------- paging
    def _go_next(self) -> None:
        if self._page >= len(_PAGES) - 1:
            # Tour fully completed: never show it again automatically.
            app_settings.save_tour_done(True)
            self.accept()
            return
        self._page += 1
        self._refresh()

    def _go_back(self) -> None:
        if self._page > 0:
            self._page -= 1
            self._refresh()

    def _skip(self) -> None:
        self._close_with_choice()

    def _close_with_choice(self) -> None:
        # Only the explicit checkbox opts out permanently; a plain skip
        # shows the tour again on the next launch.
        if self._chk.isChecked():
            app_settings.save_tour_done(True)
        self.reject()

    def closeEvent(self, event):  # noqa: N802 - Qt override
        self._close_with_choice()
        event.accept()

    def _refresh(self) -> None:
        self._stack.setCurrentIndex(self._page)
        last = self._page >= len(_PAGES) - 1
        self._btn_back.setEnabled(self._page > 0)
        self._btn_skip.setVisible(not last)
        self._btn_next.setText(
            tr("ob.btn.finish") if last else tr("ob.btn.next"))
        self._style_nav_buttons()   # chevron <-> check on the last page
        dots = []
        for i in range(len(_PAGES)):
            dots.append("\u25cf" if i == self._page else "\u25cb")
        self._dots.setText(" ".join(dots))
        self._page_of.setText(tr("ob.page_of", n=self._page + 1,
                                 total=len(_PAGES)))


# ---------------------------------------------------------------- glyphs
def _glyph_pixmap(kind: str) -> QPixmap:
    """Draw the page glyph with QPainter - a rounded dark tile with a
    simple accent symbol (mirrors the tray-icon style, no assets)."""
    size = theme.scale_px(112)
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    try:
        tile = QRectF(6, 6, size - 12, size - 12)
        p.setPen(QPen(QColor(255, 255, 255, 26), 1))
        grad = QLinearGradient(0, 0, size, size)
        grad.setColorAt(0.0, QColor(21, 26, 34))
        grad.setColorAt(1.0, QColor(14, 17, 22))
        p.setBrush(grad)
        p.drawRoundedRect(tile, 22, 22)

        accent = QColor(theme.ACCENT)
        dim = QColor(theme.TEXT_DIM)
        cx = size / 2.0
        cy = size / 2.0
        s = size / 112.0   # design at 112px

        if kind == "welcome":
            # big green up-arrow (same silhouette as the tray icon)
            p.setPen(Qt.NoPen)
            p.setBrush(accent)
            p.drawPolygon(QPolygonF([
                QPointF(cx, 24 * s), QPointF(cx + 27 * s, 60 * s),
                QPointF(cx + 12 * s, 60 * s), QPointF(cx + 12 * s, 86 * s),
                QPointF(cx - 12 * s, 86 * s), QPointF(cx - 12 * s, 60 * s),
                QPointF(cx - 27 * s, 60 * s)]))
        elif kind == "ctx":
            # menu card with three lines + a cursor arrow
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 22))
            p.drawRoundedRect(QRectF(cx - 34 * s, cy - 30 * s,
                                     62 * s, 60 * s), 9, 9)
            p.setBrush(dim)
            for i, w in enumerate((40, 30, 36)):
                p.drawRoundedRect(QRectF(cx - 26 * s, cy - 20 * s + i * 15 * s,
                                         w * s, 5 * s), 2.5, 2.5)
            p.setBrush(accent)
            p.drawPolygon(QPolygonF([
                QPointF(cx + 22 * s, cy + 6 * s), QPointF(cx + 22 * s, cy + 34 * s),
                QPointF(cx + 29 * s, cy + 26 * s), QPointF(cx + 38 * s, cy + 38 * s),
                QPointF(cx + 43 * s, cy + 33 * s), QPointF(cx + 34 * s, cy + 22 * s),
                QPointF(cx + 42 * s, cy + 22 * s)]))
        elif kind == "dl":
            # down arrow into an open box
            p.setPen(Qt.NoPen)
            p.setBrush(accent)
            p.drawPolygon(QPolygonF([
                QPointF(cx, 22 * s), QPointF(cx + 16 * s, 40 * s),
                QPointF(cx + 7 * s, 40 * s), QPointF(cx + 7 * s, 58 * s),
                QPointF(cx - 7 * s, 58 * s), QPointF(cx - 7 * s, 40 * s),
                QPointF(cx - 16 * s, 40 * s)]))
            pen = QPen(accent, 5 * s)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            path = QPainterPath()
            path.moveTo(cx - 26 * s, cy + 8 * s)
            path.lineTo(cx - 26 * s, cy + 30 * s)
            path.lineTo(cx + 26 * s, cy + 30 * s)
            path.lineTo(cx + 26 * s, cy + 8 * s)
            p.drawPath(path)
        else:  # sliders (personalize)
            pen = QPen(dim, 5 * s)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            for i, frac in enumerate((0.28, 0.62, 0.42)):
                y = cy - 22 * s + i * 22 * s
                p.drawLine(QPointF(cx - 30 * s, y), QPointF(cx + 30 * s, y))
                p.setPen(Qt.NoPen)
                p.setBrush(accent)
                kx = cx - 30 * s + frac * 60 * s
                p.drawEllipse(QPointF(kx, y), 8 * s, 8 * s)
                p.setPen(pen)
    finally:
        p.end()
    return pm
