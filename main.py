#!/usr/bin/env python3
"""Luthier: GUI front-end for the JUCE Project Generator."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.resources import resource_path
from app.theme import build_stylesheet


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
    """Set window/Dock icon from bundled PNG except on frozen macOS (.icns in bundle)."""
    icon_path = resource_path("icons/luthier.png")
    if not Path(icon_path).is_file():
        return
    if sys.platform == "darwin" and getattr(sys, "frozen", False):
        return
    app.setWindowIcon(QIcon(icon_path))


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Luthier")
    if "--check" in sys.argv:
        sys.exit(_self_check())
    app.setStyle("Fusion")
    app.setStyleSheet(build_stylesheet())
    _apply_app_icon(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
