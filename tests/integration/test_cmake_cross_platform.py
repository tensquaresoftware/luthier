"""Cross-platform CMake configure and preset portability (Story 4.3, NFR3)."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import (
    assert_spec_equal,
    canonical_cross_platform_spec,
    cmake_available,
    generate_project,
    juce_dir_for_tests,
    make_spec,
)

_ALL_PRESET_NAMES = (
    "macos-debug-arm64",
    "macos-release-arm64",
    "macos-debug-x86_64",
    "macos-release-x86_64",
    "macos-debug-universal",
    "macos-release-universal",
    "windows-debug",
    "windows-release",
    "linux-debug",
    "linux-release",
)


def _require_cmake_and_juce() -> str:
    if not cmake_available():
        pytest.skip("cmake not on PATH")
    juce = juce_dir_for_tests()
    if juce is None:
        pytest.skip("JUCE_DIR not set and no platform default JUCE install found")
    return juce


def _cmake_configure_args(juce_path: str) -> list[str]:
    """Platform extras when bare ``cmake -B build`` is insufficient (see story Dev Notes)."""
    if sys.platform == "win32":
        return [
            "-G",
            "Visual Studio 17 2022",
            "-A",
            "x64",
            f"-DJUCE_DIR={juce_path}",
        ]
    return [
        "-G",
        "Ninja",
        "-DCMAKE_BUILD_TYPE=Debug",
        f"-DJUCE_DIR={juce_path}",
    ]


def _run_cmake_configure(project_dir: Path, juce_path: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["JUCE_DIR"] = juce_path
    base = ["cmake", "-B", "build"]
    try:
        if sys.platform == "win32":
            return subprocess.run(
                base + _cmake_configure_args(juce_path),
                cwd=project_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
        result = subprocess.run(
            base,
            cwd=project_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode == 0:
            return result
        return subprocess.run(
            base + _cmake_configure_args(juce_path),
            cwd=project_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        pytest.fail(f"cmake configure timed out after {exc.timeout}s")


def _load_presets(project_dir: Path) -> dict:
    path = project_dir / "CMakeUserPresets.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _preset_by_name(presets: dict, name: str) -> dict:
    for preset in presets["configurePresets"]:
        if preset["name"] == name:
            return preset
    raise AssertionError(f"preset {name!r} not found")


@pytest.mark.skipif(sys.platform != "win32", reason="AC1 requires Windows host")
@pytest.mark.skipif(not cmake_available(), reason="cmake not on PATH")
def test_cmake_configure_windows_ac1(tmp_path):
    """AC1: project generated on any OS configures on Windows x64."""
    juce = _require_cmake_and_juce()
    project_dir, _ = generate_project(
        tmp_path, spec=canonical_cross_platform_spec(tmp_path, juce_dir=juce)
    )
    result = _run_cmake_configure(project_dir, juce)
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(sys.platform != "linux", reason="AC2 requires Linux host")
@pytest.mark.skipif(not cmake_available(), reason="cmake not on PATH")
def test_cmake_configure_linux_ac2(tmp_path):
    """AC2: project generated on any OS configures on Linux x86_64."""
    juce = _require_cmake_and_juce()
    project_dir, _ = generate_project(
        tmp_path, spec=canonical_cross_platform_spec(tmp_path, juce_dir=juce)
    )
    result = _run_cmake_configure(project_dir, juce)
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(sys.platform != "darwin", reason="dev baseline: macOS host only")
@pytest.mark.skipif(not cmake_available(), reason="cmake not on PATH")
def test_cmake_configure_macos_dev_baseline(tmp_path):
    """Dev-machine baseline: ``cmake -B build`` on macOS (Story 4.1 learning)."""
    juce = _require_cmake_and_juce()
    project_dir, _ = generate_project(
        tmp_path, spec=canonical_cross_platform_spec(tmp_path, juce_dir=juce)
    )
    result = _run_cmake_configure(project_dir, juce)
    assert result.returncode == 0, result.stderr


def test_cmake_user_presets_json_valid_ac3(tmp_path):
    """AC3 (partial): rendered CMakeUserPresets.json is valid JSON with all 10 presets."""
    project_dir, _ = generate_project(tmp_path, spec=canonical_cross_platform_spec(tmp_path))
    presets = _load_presets(project_dir)
    names = {p["name"] for p in presets["configurePresets"]}
    assert names == set(_ALL_PRESET_NAMES)
    for name in _ALL_PRESET_NAMES:
        _preset_by_name(presets, name)


def test_windows_debug_preset_structure_ac3(tmp_path):
    """AC3: windows-debug preset references only Windows-appropriate settings."""
    project_dir, _ = generate_project(tmp_path, spec=canonical_cross_platform_spec(tmp_path))
    preset = _preset_by_name(_load_presets(project_dir), "windows-debug")

    assert preset["condition"]["rhs"] == "Windows"
    assert preset["generator"] == "Visual Studio 17 2022"
    assert preset["architecture"]["value"] == "x64"
    assert "Builds/macOS/" not in preset["binaryDir"]

    cache = preset["cacheVariables"]
    assert "ARTEFACTS_DIR_MACOS" not in cache
    assert "ARTEFACTS_DIR_LINUX" not in cache
    assert cache["ARTEFACTS_DIR_WINDOWS"] == "C:/out/win"


def test_cross_origin_sidecar_round_trip_ac4(tmp_path):
    """AC4: Windows-oriented ProjectSpec survives clone via .luthier.json sidecar."""
    from core import project_reader

    spec = make_spec(
        tmp_path,
        artefacts_dir_windows="C:/team/out",
        artefacts_dir_macos="/team/mac",
        artefacts_dir_linux="/team/linux",
        juce_dir="C:/Program Files/JUCE",
        copy_to_artefacts_dir=True,
    )
    project_dir, spec = generate_project(tmp_path, spec=spec)

    clone_dir = tmp_path / "clone"
    shutil.copytree(project_dir, clone_dir)

    loaded = project_reader.read_project_result(clone_dir).spec
    assert loaded is not None
    assert_spec_equal(loaded, spec)


def test_sidecar_required_for_cross_origin_juce_dir(tmp_path):
    """AD-3: juce_dir from a Windows-oriented spec is only restored via sidecar."""
    from core import project_reader

    spec = make_spec(
        tmp_path,
        artefacts_dir_windows="C:/team/out",
        juce_dir="C:/Program Files/JUCE",
        copy_to_artefacts_dir=True,
    )
    project_dir, spec = generate_project(tmp_path, spec=spec)

    loaded = project_reader.read_project_result(project_dir).spec
    assert loaded is not None
    assert loaded.host_juce_dir() == "C:/Program Files/JUCE"

    (project_dir / ".luthier.json").unlink()
    fallback = project_reader.read_project_result(project_dir)
    assert fallback.spec is None
    assert fallback.error
    assert ".luthier.json" in fallback.error
