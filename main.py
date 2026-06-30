#!/usr/bin/env python3
"""Luthier: GUI front-end for the JUCE Project Generator."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.resources import app_icon
from app.theme import build_stylesheet, set_accent_color
from core.preferences import Preferences


def _self_check() -> int:
    """Headless check that the bundled templates are reachable."""
    from core.project_generator import ProjectGenerator, templates_dir

    generator = ProjectGenerator()
    print("frozen:", getattr(sys, "frozen", False))
    print("_MEIPASS:", getattr(sys, "_MEIPASS", None))
    print("templates_dir:", templates_dir(), "exists:", templates_dir().is_dir())
    print("error:", generator.error)
    return 0 if generator.error is None else 1


def _apply_app_icon(app: QApplication) -> None:
    """Set the application icon (bundle .icns on frozen macOS handles the Dock)."""
    if sys.platform == "darwin" and getattr(sys, "frozen", False):
        return
    icon = app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Luthier")
    if "--check" in sys.argv:
        sys.exit(_self_check())
    app.setStyle("Fusion")
    prefs = Preferences(Preferences.default_path())
    prefs.bootstrap()
    set_accent_color(prefs.accent_color)
    app.setStyleSheet(build_stylesheet())
    _apply_app_icon(app)
    window = MainWindow(prefs)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
