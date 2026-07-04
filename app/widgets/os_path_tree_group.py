"""Decorative tree lines linking a section anchor to per-OS path rows."""

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.pages.path_specs import (
    OS_FIELD_LEFT_MARGIN,
    OS_TREE_BRANCH_END,
    OS_TREE_LINE_WIDTH,
    OS_TREE_TRUNK_X,
)
from app.theme import Palette

_REFRESH_EVENTS = (
    QEvent.Type.Resize,
    QEvent.Type.Move,
    QEvent.Type.Show,
    QEvent.Type.Hide,
)


class OsPathTreeGroup(QWidget):
    """Decorative tree lines linking an anchor to per-OS path rows."""

    def __init__(self, anchor: QWidget, children: list[QWidget], parent: QWidget | None = None):
        super().__init__(parent)
        self._anchor = anchor
        self._children = list(children)
        self._build_layout()
        self._anchor.installEventFilter(self)
        for child in self._children:
            child.installEventFilter(self)

    def eventFilter(self, watched, event) -> bool:
        if watched is self._anchor or watched in self._children:
            if event.type() in _REFRESH_EVENTS:
                self.update()
        return super().eventFilter(watched, event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._children:
            return
        branch_ys = self._child_branch_ys()
        if not branch_ys:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(self._line_pen())
        start_y = self._anchor.mapTo(self, self._anchor.rect().bottomLeft()).y()
        trunk_x = float(OS_TREE_TRUNK_X)
        branch_end = float(OS_TREE_BRANCH_END)
        self._draw_trunk(painter, trunk_x, start_y, branch_ys)
        self._draw_branches(painter, trunk_x, branch_end, branch_ys)
        painter.end()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._anchor)
        host = QWidget()
        host_layout = QVBoxLayout(host)
        host_layout.setContentsMargins(OS_FIELD_LEFT_MARGIN, 0, 0, 0)
        host_layout.setSpacing(2)
        for child in self._children:
            host_layout.addWidget(child)
        layout.addWidget(host)

    def _child_branch_ys(self) -> list[float]:
        ys = []
        for child in self._children:
            if not child.isVisible():
                continue
            branch_y = self._branch_y_for_child(child)
            if branch_y is not None:
                ys.append(branch_y)
        return ys

    def _branch_y_for_child(self, child: QWidget) -> float | None:
        label = child.findChild(QLabel, "FieldLabel")
        if label is not None and label.isVisible():
            return float(label.mapTo(self, label.rect().center()).y())
        return float(child.mapTo(self, child.rect().center()).y())

    def _line_pen(self):
        pen = QPen(QColor(Palette.BORDER))
        pen.setWidthF(OS_TREE_LINE_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        return pen

    def _draw_trunk(self, painter: QPainter, trunk_x: float, start_y: float, centers: list[float]) -> None:
        painter.drawLine(trunk_x, start_y, trunk_x, centers[-1])

    def _draw_branches(self, painter: QPainter, trunk_x: float, branch_end: float, centers: list[float]) -> None:
        for index, center_y in enumerate(centers):
            painter.drawLine(trunk_x, center_y, branch_end, center_y)
            if index < len(centers) - 1:
                painter.drawLine(trunk_x, center_y, trunk_x, centers[index + 1])
