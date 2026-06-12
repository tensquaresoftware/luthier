#!/usr/bin/env python3
"""Luthier: GUI front-end for the JUCE Project Generator."""

import sys

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.theme import build_stylesheet


def _self_check() -> int:
    """Headless check that the (possibly bundled) generator loads."""
    from core.generator_bridge import GeneratorBridge, default_generator_root

    bridge = GeneratorBridge()
    bridge.ensure_loaded()
    print("frozen:", getattr(sys, "frozen", False))
    print("_MEIPASS:", getattr(sys, "_MEIPASS", None))
    print("default_root:", default_generator_root())
    print("bridge.root:", bridge.root, "exists:", bridge.root.exists())
    print("is_loaded:", bridge.is_loaded, "load_error:", bridge.load_error)
    return 0 if bridge.is_loaded else 1


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Luthier")
    if "--check" in sys.argv:
        sys.exit(_self_check())
    app.setStyleSheet(build_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
