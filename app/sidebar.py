"""Left navigation panel switching between form sections."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QVBoxLayout, QWidget

SECTIONS = ["Project Info", "Plugin Type", "Formats", "Build Settings", "Preferences"]


class Sidebar(QWidget):
    sectionChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(190)
        self._list = QListWidget()
        self._list.addItems(SECTIONS)
        self._list.setCurrentRow(0)
        self._list.currentRowChanged.connect(self.sectionChanged)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.addWidget(self._list)
