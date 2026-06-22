"""A titled section: a header label above a body widget."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class Section(QWidget):
    """Groups related fields under a bold section header."""

    def __init__(self, title: str, body: QWidget):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        header = QLabel(title)
        header.setObjectName("SectionTitle")
        layout.addWidget(header)
        layout.addSpacing(4)
        line = QFrame()
        line.setObjectName("SectionDivider")
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        layout.addWidget(line)
        layout.addSpacing(8)
        layout.addWidget(body)
