"""Projucer-inspired dark theme: palette and Qt stylesheet."""


class Palette:
    BG_MAIN = "#323e44"
    BG_SIDEBAR = "#2b343a"
    BG_BAR = "#2b343a"
    BG_INPUT = "#262f34"
    BG_DISABLED = "#5a4450"
    BORDER = "#44525a"
    TEXT = "#e8eaeb"
    TEXT_DIM = "#9aa6ac"
    ACCENT = "#c46fd9"
    PRIMARY = "#e2568f"
    PRIMARY_HOVER = "#ef6b9f"
    OK = "#5fbf73"
    ERR = "#e2686d"


def build_stylesheet() -> str:
    p = Palette
    return f"""
    QWidget {{
        background: {p.BG_MAIN};
        color: {p.TEXT};
        font-size: 13px;
    }}
    QLineEdit {{
        background: {p.BG_INPUT};
        border: 1px solid {p.BORDER};
        border-radius: 4px;
        padding: 6px 8px;
        selection-background-color: {p.ACCENT};
    }}
    QLineEdit:focus {{ border: 1px solid {p.ACCENT}; }}
    QLineEdit:read-only {{ color: {p.TEXT_DIM}; }}

    #Sidebar {{ background: {p.BG_SIDEBAR}; }}
    #Sidebar QListWidget {{ background: {p.BG_SIDEBAR}; border: none; outline: 0; }}
    #Sidebar QListWidget::item {{ padding: 10px 14px; border-radius: 4px; }}
    #Sidebar QListWidget::item:selected {{ background: {p.ACCENT}; color: white; }}
    #Sidebar QListWidget::item:hover:!selected {{ background: {p.BG_INPUT}; }}

    QPushButton {{
        background: {p.BG_INPUT};
        color: {p.TEXT};
        border: 1px solid {p.BORDER};
        border-radius: 4px;
        padding: 7px 16px;
    }}
    QPushButton:hover {{ border: 1px solid {p.ACCENT}; }}
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
    #GenerateButton:disabled {{ background: {p.BG_DISABLED}; color: #9a8a90; }}

    #PageTitle {{ font-size: 18px; font-weight: bold; }}
    #FieldLabel {{ color: {p.TEXT_DIM}; }}
    #FieldHint {{ color: {p.TEXT_DIM}; font-size: 11px; }}
    #FieldMark[state="ok"] {{ color: {p.OK}; }}
    #FieldMark[state="err"] {{ color: {p.ERR}; }}
    #FieldError {{ color: {p.ERR}; font-size: 11px; }}
    #StatusOk {{ color: {p.OK}; }}
    #StatusErr {{ color: {p.ERR}; }}
    """
