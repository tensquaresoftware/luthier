#!/usr/bin/env python3
"""Generate app icon assets from Resources/luthier-icon.svg."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = PROJECT_ROOT / "Resources" / "luthier-icon.svg"
RESOURCES = PROJECT_ROOT / "Resources"
ICONSET = PROJECT_ROOT / "Build" / "luthier.iconset"

# macOS iconset sizes (px): name suffix -> side length
_ICONSET_SIZES = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def _render_png(svg_path: Path, size: int, out_path: Path) -> None:
    renderer = QSvgRenderer(str(svg_path))
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(out_path)):
        raise RuntimeError(f"failed to write {out_path}")


def main() -> int:
    if not SVG_PATH.is_file():
        print(f"missing {SVG_PATH}", file=sys.stderr)
        return 1

    app = QApplication([])
    _render_png(SVG_PATH, 512, RESOURCES / "luthier.png")

    if ICONSET.exists():
        for child in ICONSET.iterdir():
            child.unlink()
    else:
        ICONSET.mkdir(parents=True)

    for name, size in _ICONSET_SIZES.items():
        _render_png(SVG_PATH, size, ICONSET / name)

    icns_path = RESOURCES / "luthier.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET), "-o", str(icns_path)],
        check=True,
    )
    print(f"wrote {RESOURCES / 'luthier.png'}")
    print(f"wrote {icns_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
