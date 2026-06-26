"""About page: project identity and version."""

from PySide6.QtCore import Qt, QRectF, QUrl
from PySide6.QtGui import QDesktopServices, QFontMetrics, QMouseEvent
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.resources import resource_path

_LOGO_HEIGHT = 160                                              # 80% of original 200px
_LOGO_VIEWBOX = QRectF(109, 102, 281, 304)                     # tight crop; texts shifted up 36 SVG units
_LOGO_WIDTH = round(_LOGO_HEIGHT * _LOGO_VIEWBOX.width() / _LOGO_VIEWBOX.height())
_LOGO_TOP_OFFSET = 10
_LOGO_TO_CREDITS_GAP = 28                                        # below logo, above "Credits" title
_CARD_SIZE = 500
_CARD_PADDING = 28
_CREDIT_INTERLINE_EM = 1.0
_CREDITS_EXTRA_WIDTH = 20
_CREDITS_BEFORE_BOTTOM_RULE = 10                                  # room above bottom divider (descenders)
_BMAD_PREFIX = "Yet another project successfully completed with "


def _credit_font_px(font) -> int:
    px = font.pixelSize()
    if px > 0:
        return px
    return max(1, round(font.pointSizeF() * 96.0 / 72.0))


def _credit_line_height(font) -> int:
    metrics = QFontMetrics(font)
    px = _credit_font_px(font)
    return max(metrics.height(), px)


def _align_credit_label(label: QLabel, line_height: int) -> None:
    label.setFixedHeight(line_height)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)


class _AboutLinkLabel(QLabel):
    """Clickable value label; QSS handles normal/hover colours (Qt ignores QSS on <a> tags)."""

    def __init__(self, text: str, url: str, *, object_name: str = "AboutInfoLinkValue"):
        super().__init__(text)
        self._url = QUrl(url)
        self.setObjectName(object_name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(self._url)
        super().mouseReleaseEvent(event)


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
        layout.addStretch(2)
        layout.addSpacing(_LOGO_TOP_OFFSET)
        layout.addWidget(self._make_logo(), 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(_LOGO_TO_CREDITS_GAP)
        layout.addStretch(1)
        layout.addWidget(self._make_info(), 0, Qt.AlignmentFlag.AlignHCenter)
        return card

    def _make_logo(self) -> QSvgWidget:
        logo = QSvgWidget(resource_path("luthier.svg"))
        logo.renderer().setViewBox(_LOGO_VIEWBOX)
        logo.setFixedSize(_LOGO_WIDTH, _LOGO_HEIGHT)
        return logo

    def _make_info(self) -> QWidget:
        bmad_line = self._make_bmad_line()
        widget = QWidget()
        widget.setFixedWidth(bmad_line.sizeHint().width() + _CREDITS_EXTRA_WIDTH)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        title = QLabel("Credits")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        layout.addSpacing(4)
        layout.addWidget(self._make_divider())
        layout.addSpacing(8)
        layout.addWidget(self._make_info_body())
        layout.addSpacing(_CREDITS_BEFORE_BOTTOM_RULE)
        layout.addWidget(self._make_divider())
        layout.addSpacing(6)
        layout.addWidget(bmad_line)
        return widget

    def _make_divider(self) -> QFrame:
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setObjectName("SectionDivider")
        return divider

    def _make_info_body(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("AboutCreditsBody")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        probe = QLabel()
        probe.setObjectName("AboutInfoLine")
        font = probe.font()
        layout.setSpacing(max(1, round(_credit_font_px(font) * _CREDIT_INTERLINE_EM)))
        for text, url in self._info_lines():
            layout.addWidget(self._make_info_line(text, url, font))
        return widget

    def _make_info_line(self, text: str, url: str | None, font) -> QWidget:
        line_height = _credit_line_height(font)
        widget = QWidget()
        widget.setObjectName("AboutCreditsRow")
        widget.setFixedHeight(line_height)
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        prefix, value = text.split(" : ", 1)
        prefix_label = QLabel(f"{prefix} : ")
        prefix_label.setObjectName("AboutInfoLine")
        _align_credit_label(prefix_label, line_height)
        row.addWidget(prefix_label)
        if url:
            link = _AboutLinkLabel(value, url)
            _align_credit_label(link, line_height)
            row.addWidget(link)
        else:
            value_label = QLabel(value)
            value_label.setObjectName("AboutInfoValue")
            _align_credit_label(value_label, line_height)
            row.addWidget(value_label)
        row.addStretch(1)
        return widget

    def _make_bmad_line(self) -> QWidget:
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        prefix = QLabel(_BMAD_PREFIX)
        prefix.setObjectName("AboutFieldHint")
        link = _AboutLinkLabel(
            "BMad",
            "https://github.com/bmad-code-org/bmad-method",
            object_name="AboutHintLink",
        )
        suffix = QLabel("!")
        suffix.setObjectName("AboutFieldHint")
        row.addWidget(prefix)
        row.addWidget(link)
        row.addWidget(suffix)
        row.addStretch(1)
        return widget

    def _info_lines(self) -> list[tuple[str, str | None]]:
        return [
            ("Organization : Ten Square Software", None),
            ("Author : Guillaume DUPONT", None),
            ("Email : tensquaresoftware@gmail.com", "mailto:tensquaresoftware@gmail.com"),
            ("GitHub : github.com/tensquaresoftware/Luthier", "https://github.com/tensquaresoftware/Luthier"),
            ("Version : 1.0.0", None),
            ("Revision date : 2026-06-25", None),
        ]
