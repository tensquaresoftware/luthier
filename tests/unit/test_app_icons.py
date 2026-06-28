"""App icon assets required for dev UI and PyInstaller bundles."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCES = PROJECT_ROOT / "resources"
ICONS = RESOURCES / "icons"


def test_app_icon_assets_present():
    logos = (
        "luthier-logo.png",
        "luthier-logo@2x.png",
        "luthier-icon.png",
    )
    icons = (
        "luthier.png",
        "luthier.icns",
        "luthier.ico",
    )
    missing = [name for name in logos if not (RESOURCES / name).is_file()]
    missing += [name for name in icons if not (ICONS / name).is_file()]
    assert not missing, f"missing icon assets: {', '.join(missing)}"
