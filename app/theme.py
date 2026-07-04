"""Projucer-inspired dark theme: palette and Qt stylesheet."""

from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QGuiApplication

from core.accent_colors import DEFAULT_ACCENT_COLOR, normalize_accent_color

_CHECK_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
              '<path d="M3.5 8.4 L6.6 11.4 L12.5 4.8" fill="none" stroke="{color}" '
              'stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round"/></svg>')

_CARET_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
              '<path d="M2.5 4.5 L6 8 L9.5 4.5" fill="none" stroke="{color}" '
              'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

_current_accent = DEFAULT_ACCENT_COLOR


def accent_color() -> str:
    """Return the active UI accent colour."""
    return _current_accent


def set_accent_color(color: str) -> str:
    """Set the active accent colour; returns the normalized preset used."""
    global _current_accent
    _current_accent = normalize_accent_color(color)
    return _current_accent


def apply_accent_theme(app: QGuiApplication, color: str) -> str:
    """Update accent colour and re-apply the global stylesheet."""
    normalized = set_accent_color(color)
    app.setStyleSheet(build_stylesheet())
    return normalized


def _lighten(color: str, amount: float) -> str:
    """Mix a hex colour toward white by `amount` (0..1)."""
    channels = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    mixed = (round(c + (255 - c) * amount) for c in channels)
    return "#" + "".join(f"{value:02X}" for value in mixed)


def _darken(color: str, amount: float) -> str:
    """Mix a hex colour toward black by `amount` (0..1)."""
    channels = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    mixed = (round(c * (1.0 - amount)) for c in channels)
    return "#" + "".join(f"{value:02X}" for value in mixed)


def _blend(color_a: str, color_b: str, ratio: float) -> str:
    """Blend color_a toward color_b; ratio 0 keeps a, 1 returns b."""
    pairs = zip(
        (int(color_a[i: i + 2], 16) for i in (1, 3, 5)),
        (int(color_b[i: i + 2], 16) for i in (1, 3, 5)),
    )
    return "#" + "".join(f"{round(a + (b - a) * ratio):02X}" for a, b in pairs)


def _icon_url(name: str, svg: str, color: str) -> str:
    """Write a colour-themed SVG into the cache dir and return its file URL path."""
    cache = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation))
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / name
    path.write_text(svg.format(color=color), encoding="utf-8")
    return path.as_posix()


class Palette:
    BG_MAIN = "#323e44"
    BG_SIDEBAR = "#2b343a"
    BG_BAR = "#2b343a"
    BG_INPUT = "#262f34"
    BG_DISABLED = "#3a444a"
    BORDER = "#44525a"
    TEXT = "#e8eaeb"
    TEXT_DIM = "#9aa6ac"
    ERR = "#f44336"
    ERR_DARK = _darken("#f44336", 0.22)

    @classmethod
    def ACCENT(cls) -> str:
        return _current_accent

    @classmethod
    def PRIMARY(cls) -> str:
        return _current_accent

    @classmethod
    def PRIMARY_HOVER(cls) -> str:
        return _lighten(_current_accent, 0.12)

    @classmethod
    def PRIMARY_DARK(cls) -> str:
        return _darken(_current_accent, 0.28)


def build_stylesheet() -> str:
    p = Palette
    accent = p.ACCENT()
    primary = p.PRIMARY()
    primary_hover = p.PRIMARY_HOVER()
    primary_dark = p.PRIMARY_DARK()
    accent_muted = _blend(accent, p.TEXT_DIM, 0.55)
    check = _icon_url("check.svg", _CHECK_SVG, accent)
    check_disabled = _icon_url("check-disabled.svg", _CHECK_SVG, accent_muted)
    caret = _icon_url("caret.svg", _CARET_SVG, p.TEXT_DIM)
    return f"""
    QWidget {{
        color: {p.TEXT};
        font-size: 13px;
    }}
    QMainWindow, QDialog {{ background: {p.BG_MAIN}; }}
    QScrollArea {{ background: transparent; border: none; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}

    QLineEdit, QPlainTextEdit {{
        background: {p.BG_INPUT};
        border: 1px solid {p.BORDER};
        border-radius: 4px;
        padding: 6px 8px;
        selection-background-color: {accent};
        selection-color: white;
    }}
    QLineEdit:focus, QPlainTextEdit:focus {{ border: 1px solid {accent}; }}
    QLineEdit:read-only {{ color: {p.TEXT_DIM}; }}
    QLineEdit:disabled {{
        background: {p.BG_DISABLED};
        color: {p.TEXT_DIM};
        border: 1px solid {p.BG_DISABLED};
    }}

    QComboBox {{
        background: {p.BG_INPUT};
        border: 1px solid {p.BORDER};
        border-radius: 4px;
        padding: 6px 8px;
    }}
    QComboBox:focus {{ border: 1px solid {accent}; }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{ image: url("{caret}"); width: 12px; height: 12px; }}
    QComboBox QAbstractItemView {{
        background: {p.BG_INPUT};
        color: {p.TEXT};
        border: 1px solid {p.BORDER};
        outline: 0;
        margin: 0;
        padding: 0;
    }}
    QComboBox QAbstractScrollArea,
    QComboBox QAbstractScrollArea > QWidget,
    QComboBox QAbstractScrollArea > QWidget > QWidget,
    QComboBox QFrame,
    QComboBoxPrivateContainer {{
        background: {p.BG_INPUT};
        border: none;
    }}
    QComboBoxPrivateScroller {{
        background: {p.BG_INPUT};
        border: none;
        max-height: 0px;
    }}
    QComboBox QAbstractItemView::item {{ min-height: 24px; padding: 3px 8px; border: none; }}
    QComboBox QAbstractItemView::item:hover,
    QComboBox QAbstractItemView::item:selected {{
        background: {accent};
        color: white;
    }}

    QCheckBox, QRadioButton {{ spacing: 8px; padding: 4px 2px; }}
    QCheckBox:disabled, QRadioButton:disabled {{ color: {p.TEXT_DIM}; }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {p.BORDER};
        background: {p.BG_INPUT};
    }}
    QCheckBox::indicator {{ border-radius: 3px; }}
    QRadioButton::indicator {{ border-radius: 9px; }}
    QCheckBox::indicator:checked {{
        border: 1px solid {p.BORDER};
        image: url("{check}");
    }}
    QCheckBox::indicator:checked:disabled {{
        border: 1px solid {p.BG_DISABLED};
        background: {p.BG_DISABLED};
        image: url("{check_disabled}");
    }}
    QRadioButton::indicator:checked {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 {accent}, stop:0.4 {accent}, stop:0.46 {p.BG_INPUT}, stop:1 {p.BG_INPUT});
    }}
    QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
        border: 1px solid {p.BG_DISABLED};
    }}

    #TabBarContainer {{
        background: {p.BG_SIDEBAR};
        border-bottom: 1px solid {p.BORDER};
    }}
    #TopTabBar {{
        background: transparent;
        border: none;
        qproperty-drawBase: 0;
    }}
    #TopTabBar::tab {{
        background: transparent;
        color: {p.TEXT_DIM};
        padding: 10px 20px;
        border: none;
        margin: 0;
        min-width: 80px;
        font-size: 13px;
    }}
    #TopTabBar::tab:selected {{
        background: {accent};
        color: white;
        font-weight: bold;
        border: none;
        margin: 0;
    }}
    #TopTabBar::tab:hover:!selected {{
        background: {p.BG_INPUT};
        color: {p.TEXT};
        border: none;
        margin: 0;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {p.BORDER};
        border-radius: 3px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p.TEXT_DIM};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

    QPushButton {{
        background: {p.BG_INPUT};
        color: {p.TEXT};
        border: 1px solid {p.BORDER};
        border-radius: 4px;
        padding: 7px 20px;
    }}
    QPushButton:hover {{ background: {p.BG_INPUT}; border: 1px solid {accent}; }}
    QPushButton:disabled {{ color: {p.TEXT_DIM}; }}

    #BottomBar {{ background: {p.BG_BAR}; border-top: 1px solid {p.BORDER}; }}
    #PluginTypeHintPanel {{
        background: {p.BG_BAR};
        border: 1px solid {p.BORDER};
        border-radius: 6px;
    }}
    #PluginTypeHintTitle {{
        color: white;
        font-weight: bold;
    }}
    #StatusBar {{
        background: {p.BG_INPUT};
        border-top: 1px solid {p.BORDER};
    }}
    #StatusOk, #StatusErr {{
        color: white;
        font-size: 11px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 10px;
    }}
    #StatusOk {{ background-color: {primary}; }}
    #StatusErr {{ background-color: {p.ERR}; }}
    #StatusCapsule[state="ok"] {{
        background-color: {primary};
        border-radius: 10px;
    }}
    #StatusCapsule[state="err"] {{
        background-color: {p.ERR};
        border-radius: 10px;
    }}
    #StatusCapsuleText {{
        color: white;
        background: transparent;
        font-size: 11px;
        font-weight: 600;
    }}
    #StatusDismiss {{
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
    }}
    #AboutCard {{ background: {p.BG_BAR}; border: 1px solid {p.BORDER}; border-radius: 10px; }}
    #GenerateButton {{
        background: {primary};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 9px 20px;
        font-weight: bold;
    }}
    #GenerateButton:hover {{ background: {primary_hover}; }}
    #GenerateButton:disabled {{ background: {p.BG_DISABLED}; color: {p.TEXT_DIM}; }}

    #SaveButton, #ActionButton {{
        background: {primary};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 7px 20px;
        font-weight: bold;
    }}
    #SaveButton:hover, #ActionButton:hover {{ background: {primary_hover}; }}

    #SectionTitle {{
        font-size: 18px;
        font-weight: bold;
        color: {p.TEXT};
        padding: 0;
        margin: 0;
    }}
    #SectionDivider {{
        background: {p.BORDER};
        border: none;
    }}
    #AboutInfoLine {{ color: {p.TEXT_DIM}; }}
    #AboutInfoValue {{ color: {p.TEXT}; }}
    #AboutInfoLinkValue {{ color: {p.TEXT}; }}
    #AboutInfoLinkValue:hover {{ color: {accent}; }}
    #AboutFieldHint {{ color: {p.TEXT_DIM}; font-size: 11px; font-style: italic; }}
    #AboutHintLink {{ color: {p.TEXT_DIM}; font-size: 11px; font-style: italic; }}
    #AboutHintLink:hover {{ color: {accent}; }}
    #FieldLabel {{ color: {p.TEXT_DIM}; }}
    #FieldHint {{ color: {p.TEXT_DIM}; font-size: 11px; }}
    #FieldMark[state="ok"] {{ color: {accent}; }}
    #FieldMark[state="err"] {{ color: {p.ERR}; }}
    #FieldError {{ color: {p.ERR}; font-size: 11px; }}
    #SavedIndicator {{
        background-color: {accent};
        color: white;
        font-size: 11px;
        font-weight: 600;
        padding: 0 14px;
        min-height: 20px;
        max-height: 20px;
        border-radius: 10px;
    }}
    #AccentColorTitle {{
        font-size: 13px;
        font-weight: bold;
        color: {p.TEXT};
    }}
    #AccentColorHint {{
        color: {p.TEXT_DIM};
        font-size: 11px;
    }}
    #AccentColorPill {{
        background: {p.BG_INPUT};
        border: 1px solid {p.BORDER};
        border-radius: 14px;
    }}
    #AccentColorSwatch {{
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
    }}
    """
