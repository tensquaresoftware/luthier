"""About page: project identity and version."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.resources import resource_path

_LOGO_HEIGHT = 220
_LOGO_OFFSET_UP = 10                                           # shift logo up vs equal stretch centering
_LOGO_VIEWBOX = QRectF(109, 102, 281, 304)                     # tight crop; texts shifted up 36 SVG units
_LOGO_WIDTH = round(_LOGO_HEIGHT * _LOGO_VIEWBOX.width() / _LOGO_VIEWBOX.height())
_LINE_SPACING = 13
_CARD_SIZE = 500
_CARD_PADDING = 28
_INFO_WIDTH = round((_CARD_SIZE - 2 * _CARD_PADDING) * 0.6)  # 60 % of inner width


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._make_card())
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

    def _make_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("AboutCard")
        card.setFixedSize(_CARD_SIZE, _CARD_SIZE)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_CARD_PADDING, _CARD_PADDING, _CARD_PADDING, _CARD_PADDING)
        layout.setSpacing(0)
        layout.addStretch(1)
        layout.addWidget(self._make_logo(), 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(_LOGO_OFFSET_UP * 2)
        layout.addStretch(1)
        layout.addWidget(self._make_info(), 0, Qt.AlignmentFlag.AlignHCenter)
        return card

    def _make_logo(self) -> QSvgWidget:
        logo = QSvgWidget(resource_path("luthier.svg"))
        logo.renderer().setViewBox(_LOGO_VIEWBOX)
        logo.setFixedSize(_LOGO_WIDTH, _LOGO_HEIGHT)
        return logo

    def _make_info(self) -> QWidget:
        widget = QWidget()
        widget.setFixedWidth(_INFO_WIDTH)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        title = QLabel("Credits")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        layout.addSpacing(4)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setObjectName("SectionDivider")
        layout.addWidget(divider)
        layout.addSpacing(8)
        layout.addWidget(self._make_info_body())
        return widget

    def _make_info_body(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_LINE_SPACING)
        for text in self._info_lines():
            layout.addWidget(QLabel(text))
        return widget

    def _info_lines(self) -> list[str]:
        return [
            "Organization : Ten Square Software",
            "Author : Guillaume DUPONT",
            "GitHub : github.com/tensquaresoftware/Luthier",
            "Version : 1.0.0",
            "Revision date : 2026-06-24",
        ]
