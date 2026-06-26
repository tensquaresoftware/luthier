"""Centred status capsule with single-line message and dismiss control."""

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from app.qss import repolish
from app.theme import Palette

BADGE_HEIGHT = 20                                              # matches #SavedIndicator
BAR_MIN_HEIGHT = BADGE_HEIGHT + 12                             # 6 px StatusBar padding each side
_PAD_LEFT = 14
_PAD_RIGHT = 6
_TEXT_GAP = 6
_DISMISS_SIZE = 12


class _DismissButton(QWidget):
    """Small filled circle with a centred white ×."""

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("StatusDismiss")
        self.setFixedSize(_DISMISS_SIZE, _DISMISS_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fill = QColor(Palette.PRIMARY_DARK)
        self._hover = False
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

    def set_tone(self, ok: bool) -> None:
        hex_color = Palette.PRIMARY_DARK if ok else Palette.ERR_DARK
        self._fill = QColor(hex_color)
        self.update()

    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        fill = self._fill.lighter(115) if self._hover else self._fill
        side = float(min(self.width(), self.height()))
        ox = (self.width() - side) / 2.0
        oy = (self.height() - side) / 2.0
        painter.setBrush(fill)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(ox, oy, side, side))
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        arm = side * 0.19
        pen = QPen(QColor(Qt.GlobalColor.white))
        pen.setWidthF(max(1.0, side * 0.09))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(cx - arm, cy - arm), QPointF(cx + arm, cy + arm))
        painter.drawLine(QPointF(cx + arm, cy - arm), QPointF(cx - arm, cy + arm))


class StatusCapsule(QFrame):
    """Pill badge: white single-line text + round × dismiss on the right."""

    dismissed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._full_text = ""
        self._ok = True
        self._max_width = 0
        self._build_ui()
        self.setVisible(False)

    def set_message(self, text: str, ok: bool) -> None:
        self._full_text = text
        self._ok = ok
        state = "ok" if ok else "err"
        self.setProperty("state", state)
        self._dismiss.set_tone(ok)
        repolish(self)
        if text:
            self.setVisible(True)
            self._apply_text()
        else:
            self.clear()

    def set_max_width(self, width: int) -> None:
        self._max_width = max(0, width)
        if self._max_width > 0:
            self.setMaximumWidth(self._max_width)
        self._apply_text()

    def clear(self) -> None:
        self._full_text = ""
        self._label.setText("")
        self.setVisible(False)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_dismiss()

    def _build_ui(self) -> None:
        self.setObjectName("StatusCapsule")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(BADGE_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            _PAD_LEFT, 0, _PAD_RIGHT + _DISMISS_SIZE + _TEXT_GAP, 0,
        )
        layout.setSpacing(0)
        self._label = QLabel("")
        self._label.setObjectName("StatusCapsuleText")
        self._label.setWordWrap(False)
        self._label.setFixedHeight(BADGE_HEIGHT)
        self._label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        self._label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._label)
        self._dismiss = _DismissButton(self)
        self._dismiss.clicked.connect(self._on_dismiss)
        self._dismiss.raise_()

    def _position_dismiss(self) -> None:
        y = (self.height() - _DISMISS_SIZE) // 2
        x = self.width() - _PAD_RIGHT - _DISMISS_SIZE
        self._dismiss.move(x, y)

    def _chrome_width(self) -> int:
        return _PAD_LEFT + _PAD_RIGHT + _TEXT_GAP + _DISMISS_SIZE

    def _apply_text(self) -> None:
        if not self._full_text:
            return
        metrics = self._label.fontMetrics()
        text = self._full_text
        if self._max_width > 0:
            budget = self._max_width - self._chrome_width()
            if budget > 0 and metrics.horizontalAdvance(text) > budget:
                text = metrics.elidedText(text, Qt.TextElideMode.ElideMiddle, budget)
        self._label.setText(text)
        self.adjustSize()
        self._position_dismiss()

    def _on_dismiss(self) -> None:
        self.dismissed.emit()
        self.clear()
