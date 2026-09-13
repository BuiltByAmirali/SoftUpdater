"""Fluent-style UI icon factory - pure QPainter, ZERO dependencies.

UniGetUI looks polished largely because every button/menu/nav item carries
a crisp monochrome icon (Segoe Fluent Icons). We get the same look without
an icon FONT (the earlier QSS glyph experiment rendered as white squares -
fonts are simply not reliable across Win7/Win11 + two Qt engines) and
without any bundled asset: every icon here is a small vector drawing made
of QPainter strokes/fills on a 24x24 design grid, rendered supersampled
(devicePixelRatio 2) so it stays razor-sharp at any font size and DPI.

Properties that matter for this project:
  * identical pixels on PySide6/Qt6 (x64 build) and PyQt5/Qt5 (Win7/32-bit)
  * nothing to bundle, nothing to load -> PyInstaller-safe, offline-safe
  * every icon scales with the user's font-size setting (14-20 pt)
  * RTL: direction-aware icons take a mirror=True flag (chevrons, undo);
    Qt itself flips the icon/text sides inside buttons and menus.
  * OPTICAL vertical alignment (v1.1.6): Qt centers icons on the font box
    (ascent+descent), but the visible text mass (the cap band) sits lower
    inside that box, so a geometrically centered icon reads a hair HIGH
    next to its label (user report on Segoe UI). pixmap() therefore nudges
    every glyph DOWN by (ascent - capHeight - descent) / 2 of the current
    app font - font-, size- and language-aware, zero call-site churn.
  * a small lru_cache so context menus / re-styles don't re-render.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)

from . import theme

# Color roles (theme-aware; "on_primary" = icons sitting on a filled accent).
COLORS = {
    "text": theme.TEXT,
    "dim": theme.TEXT_DIM,
    "accent": theme.ACCENT,
    "on_primary": "#07120d",
    "danger": theme.DANGER,
    "amber": "#f0b429",
}

# Status-bar dot kinds -> colors (used by MainWindow._set_status).
DOT_COLORS = {
    "dim": theme.TEXT_DIM,
    "accent": theme.ACCENT,
    "amber": "#f0b429",
    "danger": theme.DANGER,
}

_NAMES = (
    "refresh", "folder", "gear", "search", "download", "shield_check",
    "check_square", "pause", "play", "close", "copy", "globe", "grid",
    "database", "palette", "undo", "export", "import", "doc", "eye_off",
    "ban", "check_circle", "info", "chevron", "check", "logo", "dot",
)


def available() -> tuple:
    """Every drawable icon name (used by the offline test to cover all)."""
    return _NAMES


# ----------------------------------------------------------------- helpers
def _color(role) -> QColor:
    if isinstance(role, QColor):
        return role
    spec = COLORS.get(role, role)
    c = QColor(spec if isinstance(spec, str) else theme.TEXT)
    if not c.isValid():
        c = QColor(theme.TEXT)
    return c


def _stroke_pen(p: QPainter, c: QColor, s: float, width: float = 1.7) -> QPen:
    pen = QPen(c, max(1.15, width * s))
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    return pen


def _poly(p: QPainter, pts, c: QColor) -> None:
    """Filled polygon (arrowheads, play glyphs...)."""
    p.setPen(Qt.NoPen)
    p.setBrush(c)
    p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
    p.setBrush(Qt.NoBrush)


def _rrect(p: QPainter, x, y, w, h, r, c: QColor, fill: bool = False) -> None:
    p.drawRoundedRect(QRectF(x, y, w, h), r, r)
    if fill:
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(QRectF(x, y, w, h), r, r)
        p.setBrush(Qt.NoBrush)


def _line_path(p: QPainter, pts) -> None:
    path = QPainterPath()
    path.moveTo(QPointF(pts[0][0], pts[0][1]))
    for x, y in pts[1:]:
        path.lineTo(QPointF(x, y))
    p.drawPath(path)


def _arc_arrow(p: QPainter, cx, cy, r, a0, span, c: QColor,
               head: float = 3.4, wide: float = 2.6) -> None:
    """Circular arc (CCW) + a filled arrowhead at its end - the 'sync'
    refresh glyph and the undo hook are both built from this."""
    p.drawArc(QRectF(cx - r, cy - r, 2 * r, 2 * r), int(a0 * 16),
              int(span * 16))
    a1 = math.radians(a0 + span)
    ex, ey = cx + r * math.cos(a1), cy - r * math.sin(a1)
    dx, dy = -math.sin(a1), -math.cos(a1)     # CCW tangent (screen coords)
    px_, py_ = -dy, dx
    _poly(p, [
        (ex + dx * head, ey + dy * head),
        (ex + px_ * wide - dx * 0.9, ey + py_ * wide - dy * 0.9),
        (ex - px_ * wide - dx * 0.9, ey - py_ * wide - dy * 0.9),
    ], c)


def _check_mark(p: QPainter, c: QColor, shift_x: float = 0.0) -> None:
    _line_path(p, [(8.4 + shift_x, 12.2), (10.8 + shift_x, 14.6),
                   (15.7 + shift_x, 9.2)])


# ------------------------------------------------------------ the drawings
def _draw(p: QPainter, name: str, s: float, c: QColor) -> None:
    """One icon on the 24x24 grid (s = pixel size of one grid unit)."""
    if name == "refresh":
        _stroke_pen(p, c, s)
        _arc_arrow(p, 12, 12, 7.0, 60, 300, c)
    elif name == "folder":
        _stroke_pen(p, c, s)
        path = QPainterPath()
        path.moveTo(QPointF(3.5 * s, 17.5 * s))
        path.lineTo(QPointF(3.5 * s, 6.8 * s))
        path.quadTo(QPointF(3.5 * s, 5.8 * s), QPointF(4.5 * s, 5.8 * s))
        path.lineTo(QPointF(9.2 * s, 5.8 * s))
        path.quadTo(QPointF(9.9 * s, 5.8 * s), QPointF(10.3 * s, 6.4 * s))
        path.lineTo(QPointF(11.2 * s, 7.8 * s))
        path.lineTo(QPointF(19.5 * s, 7.8 * s))
        path.quadTo(QPointF(20.5 * s, 7.8 * s), QPointF(20.5 * s, 8.8 * s))
        path.lineTo(QPointF(20.5 * s, 17.5 * s))
        path.quadTo(QPointF(20.5 * s, 18.5 * s), QPointF(19.5 * s, 18.5 * s))
        path.lineTo(QPointF(4.5 * s, 18.5 * s))
        path.quadTo(QPointF(3.5 * s, 18.5 * s), QPointF(3.5 * s, 17.5 * s))
        path.closeSubpath()
        p.drawPath(path)
    elif name == "gear":
        # Solid gear: core disc + 8 flat-ended teeth, center punched out.
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawEllipse(QPointF(12 * s, 12 * s), 5.9 * s, 5.9 * s)
        tooth = QPen(c, 2.6 * s)
        tooth.setCapStyle(Qt.FlatCap)
        p.setPen(tooth)
        for i in range(8):
            a = math.radians(i * 45)
            p.drawLine(QPointF(12 * s + 5.2 * s * math.cos(a),
                               12 * s + 5.2 * s * math.sin(a)),
                       QPointF(12 * s + 8.4 * s * math.cos(a),
                               12 * s + 8.4 * s * math.sin(a)))
        # punch the hub hole (transparent, so any background shows through)
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0))
        p.drawEllipse(QPointF(12 * s, 12 * s), 2.5 * s, 2.5 * s)
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
    elif name == "search":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(10.6 * s, 10.6 * s), 5.2 * s, 5.2 * s)
        _line_path(p, [(14.7 * s, 14.7 * s), (19.2 * s, 19.2 * s)])
    elif name == "download":
        _stroke_pen(p, c, s)
        _line_path(p, [(5.5 * s, 13.5 * s), (5.5 * s, 19.0 * s),
                       (18.5 * s, 19.0 * s), (18.5 * s, 13.5 * s)])
        _line_path(p, [(12 * s, 4.2 * s), (12 * s, 12.3 * s)])
        _poly(p, [(12 * s, 15.6 * s), (8.8 * s, 10.4 * s),
                  (15.2 * s, 10.4 * s)], c)
    elif name == "shield_check":
        _stroke_pen(p, c, s)
        path = QPainterPath()
        path.moveTo(QPointF(12 * s, 3.2 * s))
        path.lineTo(QPointF(18.6 * s, 5.8 * s))
        path.lineTo(QPointF(18.6 * s, 11.2 * s))
        path.quadTo(QPointF(18.6 * s, 15.6 * s), QPointF(12 * s, 20.2 * s))
        path.quadTo(QPointF(5.4 * s, 15.6 * s), QPointF(5.4 * s, 11.2 * s))
        path.lineTo(QPointF(5.4 * s, 5.8 * s))
        path.closeSubpath()
        p.drawPath(path)
        _line_path(p, [(8.7 * s, 11.6 * s), (10.9 * s, 13.8 * s),
                       (15.3 * s, 8.6 * s)])
    elif name == "check_square":
        _stroke_pen(p, c, s)
        p.drawRoundedRect(QRectF(4.2 * s, 4.2 * s, 15.6 * s, 15.6 * s),
                          3.4 * s, 3.4 * s)
        _line_path(p, [(8.3 * s, 12.2 * s), (10.7 * s, 14.6 * s),
                       (15.8 * s, 8.8 * s)])
    elif name == "pause":
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(QRectF(7.0 * s, 5.8 * s, 3.4 * s, 12.4 * s),
                          1.7 * s, 1.7 * s)
        p.drawRoundedRect(QRectF(13.6 * s, 5.8 * s, 3.4 * s, 12.4 * s),
                          1.7 * s, 1.7 * s)
        p.setBrush(Qt.NoBrush)
    elif name == "play":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(12 * s, 12 * s), 8 * s, 8 * s)
        _poly(p, [(10.2 * s, 8.2 * s), (10.2 * s, 15.8 * s),
                  (16.4 * s, 12.0 * s)], c)
    elif name == "close":
        _stroke_pen(p, c, s, 1.9)
        _line_path(p, [(6.6 * s, 6.6 * s), (17.4 * s, 17.4 * s)])
        _line_path(p, [(17.4 * s, 6.6 * s), (6.6 * s, 17.4 * s)])
    elif name == "copy":
        _stroke_pen(p, c, s)
        p.drawRoundedRect(QRectF(9.0 * s, 4.4 * s, 10.2 * s, 10.2 * s),
                          2.2 * s, 2.2 * s)
        p.drawRoundedRect(QRectF(4.8 * s, 9.4 * s, 10.2 * s, 10.2 * s),
                          2.2 * s, 2.2 * s)
    elif name == "globe":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(12 * s, 12 * s), 8 * s, 8 * s)
        _line_path(p, [(4 * s, 12 * s), (20 * s, 12 * s)])
        p.save()
        p.translate(12 * s, 12 * s)
        p.scale(0.46, 1.0)
        p.translate(-12 * s, -12 * s)
        p.drawEllipse(QPointF(12 * s, 12 * s), 8 * s, 8 * s)
        p.restore()
    elif name == "grid":
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        for gx in (4.0, 13.0):
            for gy in (4.0, 13.0):
                p.drawRoundedRect(QRectF(gx * s, gy * s, 7 * s, 7 * s),
                                  1.9 * s, 1.9 * s)
        p.setBrush(Qt.NoBrush)
    elif name == "database":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(12 * s, 5.8 * s), 7 * s, 2.7 * s)
        _line_path(p, [(5 * s, 5.8 * s), (5 * s, 18.2 * s)])
        _line_path(p, [(19 * s, 5.8 * s), (19 * s, 18.2 * s)])
        p.drawArc(QRectF(5 * s, 9.1 * s, 14 * s, 5.4 * s),
                  180 * 16, 180 * 16)
        p.drawArc(QRectF(5 * s, 15.5 * s, 14 * s, 5.4 * s),
                  180 * 16, 180 * 16)
    elif name == "palette":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(12 * s, 12 * s), 8 * s, 8 * s)
        # thumb notch punched into the rim
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0))
        # thumb notch that actually bites through the rim (r=8 ring)
        p.drawEllipse(QPointF(7.4 * s, 16.6 * s), 3.1 * s, 3.1 * s)
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        p.setBrush(c)
        for dx, dy in ((9.6, 8.4), (13.6, 6.9), (16.3, 10.0), (16.1, 14.1)):
            p.drawEllipse(QPointF(dx * s, dy * s), 1.15 * s, 1.15 * s)
        p.setBrush(Qt.NoBrush)
    elif name == "undo":
        _stroke_pen(p, c, s)
        _arc_arrow(p, 12.6, 12.8, 5.7, 300, 220, c, head=3.5)
    elif name == "export":
        _stroke_pen(p, c, s)
        _line_path(p, [(5.5 * s, 13.0 * s), (5.5 * s, 19.4 * s),
                       (18.5 * s, 19.4 * s), (18.5 * s, 13.0 * s)])
        _line_path(p, [(12 * s, 12.6 * s), (12 * s, 6.8 * s)])
        _poly(p, [(12 * s, 3.8 * s), (9.1 * s, 8.1 * s),
                  (14.9 * s, 8.1 * s)], c)
    elif name == "import":
        _stroke_pen(p, c, s)
        _line_path(p, [(5.5 * s, 13.0 * s), (5.5 * s, 19.4 * s),
                       (18.5 * s, 19.4 * s), (18.5 * s, 13.0 * s)])
        _line_path(p, [(12 * s, 4.0 * s), (12 * s, 9.6 * s)])
        _poly(p, [(12 * s, 13.2 * s), (9.1 * s, 8.9 * s),
                  (14.9 * s, 8.9 * s)], c)
    elif name == "doc":
        _stroke_pen(p, c, s)
        p.drawRoundedRect(QRectF(5.5 * s, 3.5 * s, 13 * s, 17 * s),
                          2.4 * s, 2.4 * s)
        _line_path(p, [(8.8 * s, 9.2 * s), (15.2 * s, 9.2 * s)])
        _line_path(p, [(8.8 * s, 12.6 * s), (15.2 * s, 12.6 * s)])
        _line_path(p, [(8.8 * s, 16.0 * s), (13.2 * s, 16.0 * s)])
    elif name == "eye_off":
        _stroke_pen(p, c, s)
        path = QPainterPath()
        path.moveTo(QPointF(3.8 * s, 12 * s))
        path.quadTo(QPointF(12 * s, 5.6 * s), QPointF(20.2 * s, 12 * s))
        path.quadTo(QPointF(12 * s, 18.4 * s), QPointF(3.8 * s, 12 * s))
        path.closeSubpath()
        p.drawPath(path)
        # no pupil: outline + slash stay legible at 16px
        _stroke_pen(p, c, s, 1.9)
        _line_path(p, [(5.4 * s, 18.6 * s), (18.6 * s, 5.4 * s)])
    elif name == "ban":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(12 * s, 12 * s), 7.2 * s, 7.2 * s)
        _line_path(p, [(6.9 * s, 17.1 * s), (17.1 * s, 6.9 * s)])
    elif name == "check_circle":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(12 * s, 12 * s), 8 * s, 8 * s)
        _check_mark(p, c)
    elif name == "info":
        _stroke_pen(p, c, s)
        p.drawEllipse(QPointF(12 * s, 12 * s), 8 * s, 8 * s)
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawEllipse(QPointF(12 * s, 8.3 * s), 1.15 * s, 1.15 * s)
        p.setBrush(Qt.NoBrush)
        _line_path(p, [(12 * s, 11.4 * s), (12 * s, 16.4 * s)])
    elif name == "chevron":
        _stroke_pen(p, c, s, 1.9)
        _line_path(p, [(9.6 * s, 5.6 * s), (16.2 * s, 12 * s),
                       (9.6 * s, 18.4 * s)])
    elif name == "check":
        _stroke_pen(p, c, s, 2.1)
        _line_path(p, [(5.4 * s, 12.8 * s), (9.8 * s, 17.0 * s),
                       (18.6 * s, 7.0 * s)])
    elif name == "logo":
        # App-logo tile: accent gradient square + dark UP arrow (brand mark,
        # same silhouette as the tray icon so the app reads as one product).
        p.setPen(Qt.NoPen)
        grad = QLinearGradient(QPointF(0, 0), QPointF(0, 24 * s))
        grad.setColorAt(0.0, QColor("#34e2b5"))
        grad.setColorAt(1.0, QColor("#1da87f"))
        p.setBrush(grad)
        p.drawRoundedRect(QRectF(0.5 * s, 0.5 * s, 23 * s, 23 * s),
                          6.0 * s, 6.0 * s)
        p.setBrush(QColor(255, 255, 255, 46))
        p.drawRoundedRect(QRectF(0.5 * s, 0.5 * s, 23 * s, 10 * s),
                          6.0 * s, 6.0 * s)
        p.setBrush(QColor("#07120d"))
        cx = 12 * s
        p.drawPolygon(QPolygonF([
            QPointF(cx, 5.4 * s), QPointF(cx + 6.6 * s, 12.6 * s),
            QPointF(cx + 2.6 * s, 12.6 * s), QPointF(cx + 2.6 * s, 18.6 * s),
            QPointF(cx - 2.6 * s, 18.6 * s), QPointF(cx - 2.6 * s, 12.6 * s),
            QPointF(cx - 6.6 * s, 12.6 * s)]))
    elif name == "dot":
        # status dot: soft halo + solid core (color = DOT_COLORS kind)
        p.setPen(Qt.NoPen)
        halo = QColor(c)
        halo.setAlpha(72)
        p.setBrush(halo)
        p.drawEllipse(QPointF(12 * s, 12 * s), 10.0 * s, 10.0 * s)
        p.setBrush(c)
        p.drawEllipse(QPointF(12 * s, 12 * s), 6.0 * s, 6.0 * s)


# -------------------------------------------------------------- public API
_pixmap_cache: dict = {}


def font_shift(font) -> float:
    """Optical vertical shift (logical px, >0 = down) that lines an icon up
    with the text beside it.

    Qt vertically centers both the icon and the text line on the font box
    (ascent + descent). The eye, however, reads the text at its CAP band
    (baseline - capHeight .. baseline), whose center lies
    (ascent - capHeight - descent) / 2 BELOW the box center on most UI
    fonts (Segoe UI: ~1.0-1.5 px at 14-20 pt) - exactly the 'icon sits a
    bit higher than the text' the v1.1.5 user report described. The raw
    ink center is NOT the target: labels with descenders ('updates',
    Persian tails) would drag it around per label, making buttons look
    inconsistent with each other. Cap-band centering is the typographic
    standard and keeps every button identical."""
    try:
        from PySide6.QtGui import QFontMetrics
        fm = QFontMetrics(font)
        asc, desc = float(fm.ascent()), float(fm.descent())
        try:
            cap = float(fm.capHeight())
        except Exception:
            cap = 0.0
        if cap <= 0.0:
            cap = asc * 0.72   # metric-less fallback fonts
        return max(-1.5, min(3.0, (asc - cap - desc) / 2.0))
    except Exception:
        return 0.0


def shift_for_pt(pt: int) -> float:
    """font_shift() for the app font at a specific point size - for the
    dialogs that render at their own size (Settings) instead of the
    application-wide font."""
    try:
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        f = QFont(app.font()) if app is not None else QFont()
        f.setPointSize(int(pt))
        return font_shift(f)
    except Exception:
        return 0.0


def _auto_shift() -> float:
    """font_shift() of the current application font (the icon default)."""
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            return font_shift(app.font())
    except Exception:
        pass
    return 0.0


def pixmap(name: str, px: int, color="text", mirror: bool = False,
           vshift: float | None = None) -> QPixmap:
    """Render one icon to a supersampled, transparent QPixmap.

    vshift: optical downward nudge in logical px. None (default) = the
    cap-band auto alignment from the current app font (see font_shift);
    pass 0.0 for full-bleed drawings that must not move (the logo tile)."""
    px = max(8, int(px))
    vs = _auto_shift() if vshift is None else float(vshift)
    vs = max(-1.5, min(3.0, vs))
    vs = round(vs * 4.0) / 4.0     # quarter-px steps keep the cache tight
    vs = min(vs, px * 0.08)        # never clip the glyph's bottom edge
    key = (name, px, str(color), bool(mirror), vs)
    cached = _pixmap_cache.get(key)
    if cached is not None:
        return cached
    c = _color(color)
    dpr = 2.0   # supersample: crisp on 100% and 200% DPI alike
    pm = QPixmap(int(px * dpr), int(px * dpr))
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    try:
        if mirror:
            p.translate(px, 0)
            p.scale(-1.0, 1.0)
        if abs(vs) >= 0.25:
            p.translate(0.0, vs)
        if name == "dot":
            kind = str(color)
            c = _color(DOT_COLORS.get(kind, kind if kind in DOT_COLORS
                                      else "dim"))
        _draw(p, name, px / 24.0, c)
    except Exception:
        pass
    finally:
        p.end()
    if len(_pixmap_cache) > 512:
        _pixmap_cache.clear()
    _pixmap_cache[key] = pm
    return pm


def icon(name: str, px: int, color="text", mirror: bool = False,
         vshift: float | None = None) -> QIcon:
    """QIcon wrapper around pixmap() - for buttons, menus and actions."""
    return QIcon(pixmap(name, px, color, mirror, vshift))
