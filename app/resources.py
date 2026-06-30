"""Locate bundled resource files in dev and in a frozen (PyInstaller) build."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap

_LOGO_1X = "luthier-logo.png"
_LOGO_2X = "luthier-logo@2x.png"
_APP_ICON = "icons/luthier.png"


def resource_path(name: str) -> str:
    bundle = getattr(sys, "_MEIPASS", None)
    root = Path(bundle) if bundle else Path(__file__).resolve().parent.parent
    return str(root / "resources" / name)


def app_icon() -> QIcon:
    """Return the bundled Luthier window icon, or a null icon when missing."""
    path = resource_path(_APP_ICON)
    if not Path(path).is_file():
        return QIcon()
    return QIcon(path)


def load_about_logo_pixmap(device_pixel_ratio: float) -> QPixmap:
    """Load the About logo at native @1x or @2x resolution (no scaling)."""
    use_2x = device_pixel_ratio >= 2.0
    name = _LOGO_2X if use_2x else _LOGO_1X
    pixmap = QPixmap(resource_path(name))
    if pixmap.isNull():
        return pixmap
    pixmap.setDevicePixelRatio(2.0 if use_2x else 1.0)
    return pixmap
