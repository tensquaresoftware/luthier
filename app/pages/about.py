"""About page: project identity and version."""

from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.resources import resource_path

_LOGO_WIDTH = 300


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._make_logo(), 0, Qt.AlignmentFlag.AlignVCenter)
        row.addSpacing(32)
        row.addLayout(self._make_info(), 0)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

    def _make_logo(self) -> QSvgWidget:
        logo = QSvgWidget(resource_path("luthier.svg"))
        size = logo.renderer().defaultSize()
        height = round(size.height() * _LOGO_WIDTH / size.width())
        logo.setFixedSize(_LOGO_WIDTH, height)
        return logo

    def _make_info(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("LUTHIER — JUCE Project Generator")
        title.setObjectName("AboutTitle")
        layout.addWidget(title)
        layout.addSpacing(12)
        for text in [
            "Organization : Ten Square Software",
            "Author : Guillaume DUPONT",
            "Version : 1.0.0",
        ]:
            layout.addWidget(QLabel(text))
        return layout
