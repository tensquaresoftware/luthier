"""Integration tests for PyInstaller frozen bundle (Stories 4.1–4.2)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _frozen_bundle_layout() -> tuple[Path, Path, Path, str]:
    """Return (bundle_root, binary, bundled_assets_root, meipass_stdout_marker)."""
    if sys.platform == "darwin":
        bundle = REPO_ROOT / "dist" / "Luthier.app"
        binary = bundle / "Contents" / "MacOS" / "Luthier"
        assets_root = bundle / "Contents" / "Frameworks"
        return bundle, binary, assets_root, "Contents/Frameworks"
    bundle = REPO_ROOT / "dist" / "Luthier"
    if sys.platform == "win32":
        binary = bundle / "Luthier.exe"
    else:
        binary = bundle / "Luthier"
    assets_root = bundle / "_internal"
    return bundle, binary, assets_root, "_internal"


FROZEN_BUNDLE, FROZEN_BINARY, BUNDLED_ASSETS_ROOT, MEIPASS_MARKER = _frozen_bundle_layout()
bundle_exists = FROZEN_BINARY.is_file()


def _require_frozen_bundle() -> None:
    if not FROZEN_BINARY.is_file():
        pytest.skip(f"Frozen bundle not built ({FROZEN_BINARY})")
    if sys.platform != "win32" and not os.access(FROZEN_BINARY, os.X_OK):
        pytest.skip(f"Frozen binary not executable ({FROZEN_BINARY})")


@pytest.mark.skipif(not bundle_exists, reason="Frozen bundle not built")
def test_frozen_self_check_exits_zero():
    _require_frozen_bundle()
    try:
        result = subprocess.run(
            [str(FROZEN_BINARY), "--check"],
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
    assert MEIPASS_MARKER in result.stdout
    assert "templates_dir:" in result.stdout
    assert "exists: True" in result.stdout


@pytest.mark.skipif(not bundle_exists, reason="Frozen bundle not built")
def test_frozen_bundle_assets_present():
    _require_frozen_bundle()
    assert (BUNDLED_ASSETS_ROOT / "templates" / "CMakeLists.txt").is_file()
    assert (BUNDLED_ASSETS_ROOT / "templates" / "Source").is_dir()
    assert (BUNDLED_ASSETS_ROOT / "templates" / "CMakeUserPresets.json").is_file()
    assert (BUNDLED_ASSETS_ROOT / "templates" / ".gitignore").is_file()
    assert (BUNDLED_ASSETS_ROOT / "resources" / "luthier-logo.png").is_file()
    assert (BUNDLED_ASSETS_ROOT / "resources" / "luthier-logo@2x.png").is_file()


@pytest.mark.skipif(not bundle_exists, reason="Frozen bundle not built")
def test_generate_project_from_bundled_templates(tmp_path):
    """Validate bundled templates/ tree in the frozen bundle (not the frozen GUI Generate path)."""
    _require_frozen_bundle()
    from core import project_reader, render_context
    from core.project_writer import ProjectWriter

    from tests.conftest import make_spec

    bundled_templates = BUNDLED_ASSETS_ROOT / "templates"
    spec = make_spec(tmp_path)
    dest = Path(spec.host_destination_dir()) / spec.project_name
    writer = ProjectWriter(bundled_templates, dest, overrides=None)
    writer.write(
        render_context.build_context(spec),
        render_context.build_tokens(spec),
        spec,
    )
    assert (dest / "CMakeLists.txt").is_file()
    assert (dest / ".luthier.json").is_file()
    reloaded = project_reader.read_project_result(dest).spec
    assert reloaded.project_name == spec.project_name
