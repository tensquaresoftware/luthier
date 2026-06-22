#!/usr/bin/env python3
"""Luthier: GUI front-end for the JUCE Project Generator."""

import sys

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
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


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Luthier")
    if "--check" in sys.argv:
        sys.exit(_self_check())
    app.setStyle("Fusion")
    app.setStyleSheet(build_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
