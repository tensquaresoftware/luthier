"""Centred status capsule with single-line message and dismiss control."""

from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt, Signal, QVariantAnimation
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from app.qss import repolish
from app.theme import Palette

BADGE_HEIGHT = 20                                              # matches #SavedIndicator
STATUS_BAR_V_PAD = 10                                          # vertical padding each side in StatusBar
BAR_MIN_HEIGHT = BADGE_HEIGHT + STATUS_BAR_V_PAD * 2
FIELD_LABEL_WIDTH = 150                                          # matches form field labels
STATUS_BAR_MARGIN_LEFT = 24                                    # matches Project / Preferences pages
STATUS_BAR_MARGIN_RIGHT = 16
ROW_SPACING = 8                                                # label column → content (Choose… gap)
_PENDING_MSG_COLOR = "#ffffff"
_PENDING_MSG_ICON_SIZE = 16
_PENDING_MSG_PULSE_MS = 1200
_PENDING_MSG_PULSE_MIN = 0.1
_PENDING_MSG_PULSE_MAX = 0.7
# Lucide "message-square-text" (ISC) — https://lucide.dev/icons/message-square-text
_LUCIDE_MESSAGE_SQUARE_TEXT_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
    ' stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5'
    'a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"/>'
    '<path d="M7 11h10"/><path d="M7 15h6"/><path d="M7 7h8"/>'
    '</svg>'
)
_pending_msg_icon_renderer: QSvgRenderer | None = None


def status_capsule_max_width(bar_width: int) -> int:
    """Width available for the pill after heading column and margins."""
    if bar_width <= 0:
        return 0
    used = (
        STATUS_BAR_MARGIN_LEFT
        + FIELD_LABEL_WIDTH
        + ROW_SPACING
        + STATUS_BAR_MARGIN_RIGHT
    )
    return max(120, bar_width - used)


_PAD_LEFT = 14
_PAD_RIGHT = 6
_TEXT_GAP = 6
_DISMISS_SIZE = 12


def _pending_message_icon_renderer() -> QSvgRenderer:
    global _pending_msg_icon_renderer
    if _pending_msg_icon_renderer is None:
        svg = _LUCIDE_MESSAGE_SQUARE_TEXT_SVG.format(color=_PENDING_MSG_COLOR)
        _pending_msg_icon_renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    return _pending_msg_icon_renderer


class _PendingMessageIcon(QWidget):
    """Lucide message-square-text with a gentle opacity pulse."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._pulse = _PENDING_MSG_PULSE_MAX
        self._renderer = _pending_message_icon_renderer()
        self.setFixedSize(_PENDING_MSG_ICON_SIZE, _PENDING_MSG_ICON_SIZE)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(_PENDING_MSG_PULSE_MS)
        self._anim.setKeyValueAt(0.0, _PENDING_MSG_PULSE_MAX)
        self._anim.setKeyValueAt(0.5, _PENDING_MSG_PULSE_MIN)
        self._anim.setKeyValueAt(1.0, _PENDING_MSG_PULSE_MAX)
        self._anim.setLoopCount(-1)
        self._anim.valueChanged.connect(self._on_pulse)
        self._anim.start()

    def _on_pulse(self, value) -> None:
        self._pulse = float(value)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._pulse)
        side = float(min(self.width(), self.height()))
        ox = (self.width() - side) / 2.0
        oy = (self.height() - side) / 2.0
        self._renderer.render(painter, QRectF(ox, oy, side, side))


class StatusMessageHeading(QWidget):
    """User Message label + pending-message icon, aligned with form field labels."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedWidth(FIELD_LABEL_WIDTH)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        text = QLabel("User Message")
        text.setObjectName("FieldLabel")
        text.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        icon = _PendingMessageIcon()
        row.addWidget(text, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addStretch(1)


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
