"""Projucer-inspired dark theme: palette and Qt stylesheet."""

from pathlib import Path

from PySide6.QtCore import QStandardPaths

kMainColor_ = "#FF6633"

_CHECK_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
              '<path d="M3.5 8.4 L6.6 11.4 L12.5 4.8" fill="none" stroke="{color}" '
              'stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round"/></svg>')

_CARET_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
              '<path d="M2.5 4.5 L6 8 L9.5 4.5" fill="none" stroke="{color}" '
              'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _lighten(color: str, amount: float) -> str:
    """Mix a hex colour toward white by `amount` (0..1)."""
    channels = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    mixed = (round(c + (255 - c) * amount) for c in channels)
    return "#" + "".join(f"{value:02X}" for value in mixed)


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
    ACCENT = kMainColor_
    PRIMARY = kMainColor_
    PRIMARY_HOVER = "#FF6600"
    OK = "#5fbf73"
    ERR = "#e2686d"


def build_stylesheet() -> str:
    p = Palette
    check = _icon_url("check.svg", _CHECK_SVG, p.ACCENT)
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
        selection-background-color: {p.ACCENT};
        selection-color: white;
    }}
    QLineEdit:focus, QPlainTextEdit:focus {{ border: 1px solid {p.ACCENT}; }}
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
    QComboBox:focus {{ border: 1px solid {p.ACCENT}; }}
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
        background: {p.ACCENT};
        color: white;
    }}

    QCheckBox, QRadioButton {{ spacing: 8px; padding: 4px 2px; }}
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
    QRadioButton::indicator:checked {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 {p.ACCENT}, stop:0.4 {p.ACCENT}, stop:0.46 {p.BG_INPUT}, stop:1 {p.BG_INPUT});
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
        background: {p.ACCENT};
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
        padding: 7px 16px;
    }}
    QPushButton:hover {{ background: {p.BG_INPUT}; border: 1px solid {p.ACCENT}; }}
    QPushButton:disabled {{ color: {p.TEXT_DIM}; }}

    #BottomBar {{ background: {p.BG_BAR}; border-top: 1px solid {p.BORDER}; }}
    #GenerateButton {{
        background: {p.PRIMARY};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 9px 22px;
        font-weight: bold;
    }}
    #GenerateButton:hover {{ background: {p.PRIMARY_HOVER}; }}
    #GenerateButton:disabled {{ background: {p.BG_DISABLED}; color: {p.TEXT_DIM}; }}

    #OpenButton {{
        background: {p.PRIMARY};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 7px 16px;
        font-weight: bold;
    }}
    #OpenButton:hover {{ background: {p.PRIMARY_HOVER}; }}

    #SaveButton, #ActionButton {{
        background: {p.PRIMARY};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 7px 16px;
        font-weight: bold;
    }}
    #SaveButton:hover, #ActionButton:hover {{ background: {p.PRIMARY_HOVER}; }}

    #PageTitle {{ font-size: 18px; font-weight: bold; }}
    #AboutTitle {{ font-size: 15px; font-weight: bold; }}
    #SectionTitle {{
        font-size: 14px;
        font-weight: bold;
        color: {p.TEXT};
        padding: 0;
        margin: 0;
    }}
    #SectionDivider {{
        background: {p.BORDER};
        border: none;
    }}
    #FieldLabel {{ color: {p.TEXT_DIM}; }}
    #FieldHint {{ color: {p.TEXT_DIM}; font-size: 11px; }}
    #FieldMark[state="ok"] {{ color: {p.OK}; }}
    #FieldMark[state="err"] {{ color: {p.ERR}; }}
    #FieldError {{ color: {p.ERR}; font-size: 11px; }}
    #StatusOk {{ color: {p.OK}; }}
    #StatusErr {{ color: {p.ERR}; }}
    """
