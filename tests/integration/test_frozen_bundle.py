"""Integration tests for PyInstaller frozen macOS bundle (Story 4.1)."""

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MACOS_BUNDLE = REPO_ROOT / "Dist" / "Luthier.app"
MACOS_BINARY = MACOS_BUNDLE / "Contents" / "MacOS" / "Luthier"

bundle_exists = MACOS_BINARY.is_file()


def _require_macos_bundle() -> None:
    if not MACOS_BINARY.is_file():
        pytest.skip("Dist/Luthier.app not built")


@pytest.mark.skipif(not bundle_exists, reason="Dist/Luthier.app not built")
def test_frozen_self_check_exits_zero():
    _require_macos_bundle()
    try:
        result = subprocess.run(
            [str(MACOS_BINARY), "--check"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        pytest.fail(f"--check timed out after {exc.timeout}s")
    assert result.returncode == 0, result.stderr
    assert "frozen: True" in result.stdout
    assert "error: None" in result.stdout
    assert "_MEIPASS:" in result.stdout
    assert "Contents/Frameworks" in result.stdout
    assert "templates_dir:" in result.stdout
    assert "exists: True" in result.stdout


@pytest.mark.skipif(not bundle_exists, reason="Dist/Luthier.app not built")
def test_frozen_bundle_assets_present():
    _require_macos_bundle()
    frameworks = MACOS_BUNDLE / "Contents" / "Frameworks"
    assert (frameworks / "Templates" / "CMakeLists.txt").is_file()
    assert (frameworks / "Templates" / "Source").is_dir()
    assert (frameworks / "Templates" / "CMakeUserPresets.json").is_file()
    assert (frameworks / "Templates" / ".gitignore").is_file()
    assert (frameworks / "Resources" / "luthier.svg").is_file()


@pytest.mark.skipif(not bundle_exists, reason="Dist/Luthier.app not built")
def test_generate_project_from_bundled_templates(tmp_path):
    """Validate bundled Templates/ tree under the .app (not the frozen GUI Generate path)."""
    _require_macos_bundle()
    from core import project_reader, render_context
    from core.project_writer import ProjectWriter

    from tests.conftest import make_spec

    bundled_templates = MACOS_BUNDLE / "Contents" / "Frameworks" / "Templates"
    spec = make_spec(tmp_path)
    dest = Path(spec.destination_dir) / spec.project_name
    writer = ProjectWriter(bundled_templates, dest, overrides=None)
    writer.write(
        render_context.build_context(spec),
        render_context.build_tokens(spec),
        spec,
    )
    assert (dest / "CMakeLists.txt").is_file()
    assert (dest / ".luthier.json").is_file()
    reloaded = project_reader.read_project(dest)
    assert reloaded.project_name == spec.project_name
