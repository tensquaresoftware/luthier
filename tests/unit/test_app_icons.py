"""App icon assets required for dev UI and PyInstaller bundles."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCES = PROJECT_ROOT / "Resources"


def test_app_icon_assets_present():
    required = (
        "luthier-logo.png",
        "luthier-logo@2x.png",
        "luthier-icon.png",
        "luthier.png",
        "luthier.icns",
        "luthier.ico",
    )
    missing = [name for name in required if not (RESOURCES / name).is_file()]
    assert not missing, f"missing icon assets: {', '.join(missing)}"
