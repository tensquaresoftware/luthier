"""Inline 'Saved' capsule badge overlaid inside an input widget."""

from PySide6.QtCore import QPropertyAnimation, QTimer, Qt
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QPlainTextEdit,
    QWidget,
)


class BadgedInputHost(QWidget):
    """Hosts an input widget with a right-aligned Saved capsule overlaid inside it."""

    def __init__(
        self,
        inner: QWidget,
        parent: QWidget | None = None,
        *,
        badge_at_top: bool = False,
    ):
        super().__init__(parent)
        self._badge_at_top = badge_at_top
        self._inner = inner
        self._inner.setParent(self)
        self._inner.setObjectName("BadgedLineEdit")
        policy = inner.sizePolicy()
        self.setSizePolicy(policy.horizontalPolicy(), policy.verticalPolicy())
        self._badge = QLabel("Saved", self)
        self._badge.setObjectName("SavedIndicator")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setFixedHeight(20)
        self._badge.hide()
        self._badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._opacity = QGraphicsOpacityEffect(self._badge)
        self._badge.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(500)
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.finished.connect(self._hide_badge)

    def inner(self) -> QWidget:
        return self._inner

    def sizeHint(self):
        return self._inner.sizeHint()

    def minimumSizeHint(self):
        return self._inner.minimumSizeHint()

    def flash_saved(self) -> None:
        self._fade.stop()
        self._opacity.setOpacity(1.0)
        self._position_badge()
        self._badge.show()
        self._badge.raise_()
        self._sync_badge_padding()
        QTimer.singleShot(400, self._fade.start)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._inner.setGeometry(0, 0, self.width(), self.height())
        self._position_badge()

    def _position_badge(self) -> None:
        self._badge.adjustSize()
        badge_w = max(self._badge.sizeHint().width(), self._badge.width())
        badge_h = self._badge.height()
        if self._badge_at_top:
            y = 6
        else:
            y = max(0, (self.height() - badge_h) // 2)
        x = max(0, self.width() - badge_w - 8)
        self._badge.setGeometry(x, y, badge_w, badge_h)

    def _sync_badge_padding(self) -> None:
        right = self._badge.width() + 10 if self._badge.isVisible() else 0
        if right:
            self._inner.setStyleSheet(f"padding-right: {right}px;")
        else:
            self._inner.setStyleSheet("")

    def _hide_badge(self) -> None:
        self._badge.hide()
        self._opacity.setOpacity(1.0)
        self._sync_badge_padding()


class MultilineBadgedEditor(QWidget):
    """Fixed-height plain-text editor with a Saved badge in the top-right corner."""

    HEIGHT = 64

    def __init__(self, placeholder: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self._edit = QPlainTextEdit(self)
        self._edit.setPlaceholderText(placeholder)
        self._badge = QLabel("Saved", self)
        self._badge.setObjectName("SavedIndicator")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setFixedHeight(20)
        self._badge.hide()
        self._badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._opacity = QGraphicsOpacityEffect(self._badge)
        self._badge.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(500)
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.finished.connect(self._hide_badge)

    @property
    def edit(self) -> QPlainTextEdit:
        return self._edit

    def flash_saved(self) -> None:
        self._fade.stop()
        self._opacity.setOpacity(1.0)
        self._position_badge()
        self._badge.show()
        self._badge.raise_()
        self._sync_badge_padding()
        QTimer.singleShot(400, self._fade.start)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._edit.setGeometry(0, 0, self.width(), self.height())
        self._position_badge()

    def _position_badge(self) -> None:
        self._badge.adjustSize()
        badge_w = max(self._badge.sizeHint().width(), self._badge.width())
        badge_h = self._badge.height()
        x = max(0, self.width() - badge_w - 8)
        self._badge.setGeometry(x, 6, badge_w, badge_h)

    def _sync_badge_padding(self) -> None:
        right = self._badge.width() + 10 if self._badge.isVisible() else 0
        if right:
            self._edit.setStyleSheet(f"padding-right: {right}px;")
        else:
            self._edit.setStyleSheet("")

    def _hide_badge(self) -> None:
        self._badge.hide()
        self._opacity.setOpacity(1.0)
        self._sync_badge_padding()
