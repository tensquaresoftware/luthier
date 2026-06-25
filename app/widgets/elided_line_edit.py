"""QLineEdit that ellipsizes overflowing text when the field is not focused."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent, QPalette, QResizeEvent
from PySide6.QtWidgets import QLineEdit, QStyle, QStyleOptionFrame, QStylePainter


class ElidedLineEdit(QLineEdit):
    """Shows elided text (…) when unfocused; full text while editing."""

    def __init__(
        self,
        parent=None,
        *,
        elide_mode: Qt.TextElideMode = Qt.TextElideMode.ElideRight,
    ):
        super().__init__(parent)
        self._elide_mode = elide_mode

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.update()

    def _contents_rect(self):
        option = QStyleOptionFrame()
        self.initStyleOption(option)
        return self.style().subElementRect(
            QStyle.SubElement.SE_LineEditContents, option, self
        )

    def _should_elide(self) -> bool:
        text = self.text()
        if not text or self.hasFocus():
            return False
        return self.fontMetrics().horizontalAdvance(text) > self._contents_rect().width()

    def paintEvent(self, event) -> None:
        if not self._should_elide():
            super().paintEvent(event)
            return

        painter = QStylePainter(self)
        option = QStyleOptionFrame()
        self.initStyleOption(option)
        painter.drawPrimitive(QStyle.PrimitiveElement.PE_PanelLineEdit, option)

        contents = self._contents_rect()
        text = self.fontMetrics().elidedText(
            self.text(), self._elide_mode, max(0, contents.width())
        )
        painter.setPen(self.palette().color(QPalette.ColorRole.Text))
        painter.drawText(
            contents,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            text,
        )
