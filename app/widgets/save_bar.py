"""Action row with a status message and a save button."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from app.qss import repolish


class SaveBar(QWidget):
    """Status label + button, emitting saveRequested on click."""

    saveRequested = Signal()

    def __init__(self, label: str = "Save"):
        super().__init__()
        self._build_ui(label)

    def set_status(self, text: str, ok: bool) -> None:
        self._status.setText(text)
        self._status.setObjectName("StatusOk" if ok else "StatusErr")
        repolish(self._status)

    def _build_ui(self, label: str) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 8, 0, 0)
        self._status = QLabel("")
        button = QPushButton(label)
        button.clicked.connect(self.saveRequested)
        row.addWidget(self._status, 1)
        row.addWidget(button)
