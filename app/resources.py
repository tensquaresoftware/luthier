"""Locate bundled resource files in dev and in a frozen (PyInstaller) build."""

import sys
from pathlib import Path


def resource_path(name: str) -> str:
    bundle = getattr(sys, "_MEIPASS", None)
    root = Path(bundle) if bundle else Path(__file__).resolve().parent.parent
    return str(root / "resources" / name)
