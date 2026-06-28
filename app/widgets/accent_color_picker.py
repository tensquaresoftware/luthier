"""Preset accent colour picker — FluidVoice-inspired pill of swatches."""

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from app.widgets.validated_field import _LABEL_WIDTH
from core.accent_colors import ACCENT_PRESETS, normalize_accent_color

_ROW_SPACING = 8
_MARK_WIDTH = 16
_SWATCH_DIAM = 14
_RING_COLOR = "#40535B"
_RING_GAP = 2.0
_RING_WIDTH = 2.0
_SWATCH_GAP = 10
_PILL_PAD_H = 8
_PILL_PAD_V = 5
_SWATCH_RADIUS = _SWATCH_DIAM / 2.0
_RING_MID_RADIUS = _SWATCH_RADIUS + _RING_GAP + _RING_WIDTH / 2.0
_OUTER_RADIUS = _SWATCH_RADIUS + _RING_GAP + _RING_WIDTH
_WIDGET_SIZE = int(_OUTER_RADIUS * 2) + 2


class _SwatchButton(QWidget):
    """Circular colour swatch with optional selection ring."""

    clicked = Signal(str)

    def __init__(self, color: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._color = color
        self._selected = False
        self.setObjectName("AccentColorSwatch")
        self.setFixedSize(_WIDGET_SIZE, _WIDGET_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(color)

    def color(self) -> str:
        return self._color

    def set_selected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._color)
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self._color))
        painter.drawEllipse(center, _SWATCH_RADIUS, _SWATCH_RADIUS)
        if self._selected:
            pen = QPen(QColor(_RING_COLOR))
            pen.setWidthF(_RING_WIDTH)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.drawEllipse(center, _RING_MID_RADIUS, _RING_MID_RADIUS)


class AccentColorPicker(QWidget):
    """Row of preset swatches inside a rounded pill container."""

    colorChanged = Signal(str)

    def __init__(self, initial: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._color = normalize_accent_color(initial)
        self._swatches: list[_SwatchButton] = []
        self._sync_guard = False
        self._build_ui()
        self._sync_selection()

    def color(self) -> str:
        return self._color

    def set_color(self, color: str, *, notify: bool = False) -> None:
        normalized = normalize_accent_color(color)
        if normalized == self._color and not notify:
            self._sync_selection()
            return
        self._color = normalized
        self._sync_selection()
        if notify:
            self.colorChanged.emit(self._color)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        pill = QWidget()
        pill.setObjectName("AccentColorPill")
        pill.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        pill_layout = QHBoxLayout(pill)
        pill_layout.setContentsMargins(_PILL_PAD_H, _PILL_PAD_V, _PILL_PAD_H, _PILL_PAD_V)
        pill_layout.setSpacing(_SWATCH_GAP)
        for _name, hex_color in ACCENT_PRESETS:
            swatch = _SwatchButton(hex_color)
            swatch.clicked.connect(self._on_swatch_clicked)
            self._swatches.append(swatch)
            pill_layout.addWidget(swatch)
        layout.addWidget(pill)

    def _on_swatch_clicked(self, color: str) -> None:
        if self._sync_guard:
            return
        normalized = normalize_accent_color(color)
        if normalized == self._color:
            return
        self._color = normalized
        self._sync_selection()
        self.colorChanged.emit(self._color)

    def _sync_selection(self) -> None:
        self._sync_guard = True
        try:
            for swatch in self._swatches:
                swatch.set_selected(swatch.color() == self._color)
        finally:
            self._sync_guard = False


class AccentColorSection(QWidget):
    """Settings row aligned with form fields: label column, pill flush right."""

    colorChanged = Signal(str)

    def __init__(self, initial: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._picker = AccentColorPicker(initial)
        self._picker.colorChanged.connect(self.colorChanged.emit)
        self._build_ui()

    def color(self) -> str:
        return self._picker.color()

    def set_color(self, color: str, *, notify: bool = False) -> None:
        self._picker.set_color(color, notify=notify)

    def _build_ui(self) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(_ROW_SPACING)

        title = QLabel("Luthier Accent Color")
        title.setObjectName("AccentColorTitle")
        hint = QLabel("Pick a preset accent color for the app.")
        hint.setObjectName("AccentColorHint")
        hint.setWordWrap(False)

        labels = QVBoxLayout()
        labels.setContentsMargins(0, 0, 0, 0)
        labels.setSpacing(2)
        labels.addWidget(title)
        labels.addWidget(hint)

        label_host = QWidget()
        hint_width = hint.fontMetrics().horizontalAdvance(hint.text())
        label_host.setFixedWidth(max(_LABEL_WIDTH, hint_width))
        label_host.setLayout(labels)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addStretch(1)
        content_layout.addWidget(self._picker, 0, Qt.AlignmentFlag.AlignRight)

        mark_spacer = QWidget()
        mark_spacer.setFixedWidth(_MARK_WIDTH)

        row.addWidget(label_host, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(content, 1)
        row.addWidget(mark_spacer)
