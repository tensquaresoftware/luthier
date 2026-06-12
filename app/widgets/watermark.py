"""Central panel that paints the Luthier logo as a faint background watermark."""

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget

from app.theme import Palette

_OPACITY = 0.10
_SIZE_RATIO = 0.62


class WatermarkBackground(QWidget):
    """Fills the area with the base colour and overlays the logo, centered."""

    def __init__(self, svg_path: str):
        super().__init__()
        self._renderer = QSvgRenderer(svg_path)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(Palette.BG_MAIN))
        self._draw_logo(painter)
        painter.end()

    def _draw_logo(self, painter: QPainter) -> None:
        if not self._renderer.isValid():
            return
        side = min(self.width(), self.height()) * _SIZE_RATIO
        x = (self.width() - side) / 2
        y = (self.height() - side) / 2
        painter.setOpacity(_OPACITY)
        self._renderer.render(painter, QRectF(x, y, side, side))
