#!/usr/bin/env python3
"""Generate app icon assets from resources/icons/luthier-icon.png."""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ICONS = PROJECT_ROOT / "resources" / "icons"
SOURCE_PATH = ICONS / "luthier-icon.png"
SOURCE_SIZE = 1024                                              # master icon from Figma (square)
ICONSET = PROJECT_ROOT / "build" / "luthier.iconset"

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


def _load_source() -> QImage:
    image = QImage(str(SOURCE_PATH))
    if image.isNull():
        raise RuntimeError(f"failed to read {SOURCE_PATH}")
    if image.width() != image.height():
        raise RuntimeError(f"{SOURCE_PATH} must be square, got {image.width()}x{image.height()}")
    if image.width() != SOURCE_SIZE:
        raise RuntimeError(
            f"{SOURCE_PATH} must be {SOURCE_SIZE}x{SOURCE_SIZE} "
            f"(export from Figma at 1x), got {image.width()}x{image.height()}"
        )
    return image


def _render_png(source: QImage, size: int, out_path: Path) -> None:
    scaled = source.scaled(
        size,
        size,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not scaled.save(str(out_path)):
        raise RuntimeError(f"failed to write {out_path}")


def _write_ico(png_paths: list[Path], out_path: Path) -> None:
    """Pack PNGs into a Windows .ico (Vista+ embedded PNG)."""
    entries: list[tuple[int, bytes]] = []
    for path in png_paths:
        data = path.read_bytes()
        image = QImage()
        if not image.load(str(path)):
            raise RuntimeError(f"failed to read {path}")
        size = image.width()
        entries.append((size, data))

    header = struct.pack("<HHH", 0, 1, len(entries))
    offset = 6 + 16 * len(entries)
    directory = bytearray()
    blobs = bytearray()
    for size, data in entries:
        dim = 0 if size >= 256 else size
        directory.extend(struct.pack(
            "<BBBBHHII",
            dim,
            dim,
            0,
            0,
            1,
            32,
            len(data),
            offset,
        ))
        blobs.extend(data)
        offset += len(data)
    out_path.write_bytes(header + directory + blobs)


def main() -> int:
    if not SOURCE_PATH.is_file():
        print(f"missing {SOURCE_PATH}", file=sys.stderr)
        return 1

    app = QApplication([])
    source = _load_source()
    _render_png(source, 512, ICONS / "luthier.png")

    if ICONSET.exists():
        for child in ICONSET.iterdir():
            child.unlink()
    else:
        ICONSET.mkdir(parents=True)

    for name, size in _ICONSET_SIZES.items():
        _render_png(source, size, ICONSET / name)

    icns_path = ICONS / "luthier.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET), "-o", str(icns_path)],
        check=True,
    )
    ico_path = ICONS / "luthier.ico"
    _write_ico(
        [ICONSET / "icon_16x16.png", ICONSET / "icon_32x32.png", ICONSET / "icon_256x256.png"],
        ico_path,
    )
    print(f"wrote {ICONS / 'luthier.png'}")
    print(f"wrote {icns_path}")
    print(f"wrote {ico_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
