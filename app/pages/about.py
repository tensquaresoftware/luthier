"""About page: project identity and version."""

from PySide6.QtCore import QEvent, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QMouseEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from app.resources import load_about_logo_pixmap

_LOGO_WIDTH = 193
_LOGO_HEIGHT = 280
_CARD_SIZE = 600
_LOGO_ZONE_HEIGHT = 360                                           # 40 + logo + 40
_CREDITS_ZONE_HEIGHT = 240
_LOGO_ZONE_PADDING_V = 40
_CREDITS_H_PADDING = 28
_CREDIT_INTERLINE_EM = 0.5
_CREDIT_PROBE_TEXT = "Hg"  # ascenders + descenders for QLabel sizeHint, not raw font metrics
_CREDITS_EXTRA_WIDTH = 20
_CREDITS_BEFORE_BOTTOM_RULE = 10                                  # room above bottom divider (descenders)
_BMAD_PREFIX = "Yet another project successfully completed with "


def _credit_font_px(font) -> int:
    px = font.pixelSize()
    if px > 0:
        return px
    return max(1, round(font.pointSizeF() * 96.0 / 72.0))


def _credit_line_height(probe: QLabel) -> int:
    """QLabel sizeHint includes style padding beyond QFontMetrics (e.g. +2 px on Windows)."""
    return probe.sizeHint().height()


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


class _AboutLogo(QLabel):
    """About logo from pre-rendered @1x / @2x PNG assets (no scaling)."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(_LOGO_WIDTH, _LOGO_HEIGHT)
        self._apply_pixmap()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.DevicePixelRatioChange:
            self._apply_pixmap()
        return super().event(event)

    def _apply_pixmap(self) -> None:
        pixmap = load_about_logo_pixmap(self.devicePixelRatioF())
        if pixmap.isNull():
            self.clear()
            return
        self.setPixmap(pixmap)


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)
        card = self._make_card()
        outer.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        outer.addStretch(1)

    def _make_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("AboutCard")
        card.setFixedSize(_CARD_SIZE, _CARD_SIZE)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._make_logo_zone())
        layout.addWidget(self._make_credits_zone())
        return card

    def _make_logo_zone(self) -> QWidget:
        zone = QWidget()
        zone.setFixedHeight(_LOGO_ZONE_HEIGHT)
        layout = QVBoxLayout(zone)
        layout.setContentsMargins(0, _LOGO_ZONE_PADDING_V, 0, _LOGO_ZONE_PADDING_V)
        layout.setSpacing(0)
        layout.addWidget(_AboutLogo(), 0, Qt.AlignmentFlag.AlignHCenter)
        return zone

    def _make_credits_zone(self) -> QWidget:
        zone = QWidget()
        zone.setFixedHeight(_CREDITS_ZONE_HEIGHT)
        layout = QVBoxLayout(zone)
        layout.setContentsMargins(_CREDITS_H_PADDING, 0, _CREDITS_H_PADDING, 0)
        layout.setSpacing(0)
        info = self._make_info()
        info.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        layout.addWidget(info, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.addStretch(1)
        return zone

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
        divider.setFrameShape(QFrame.Shape.NoFrame)
        divider.setFixedHeight(1)
        divider.setObjectName("SectionDivider")
        return divider

    def _make_info_body(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("AboutCreditsBody")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        probe = QLabel(_CREDIT_PROBE_TEXT)
        probe.setObjectName("AboutInfoLine")
        font = probe.font()
        line_height = _credit_line_height(probe)
        layout.setSpacing(max(1, round(_credit_font_px(font) * _CREDIT_INTERLINE_EM)))
        for text, url in self._info_lines():
            layout.addWidget(self._make_info_line(text, url, line_height))
        return widget

    def _make_info_line(self, text: str, url: str | None, line_height: int) -> QWidget:
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
            ("GitHub : github.com/tensquaresoftware/luthier", "https://github.com/tensquaresoftware/luthier"),
            ("Version : 1.0.0", None),
            ("Revision date : 2026-06-25", None),
        ]
