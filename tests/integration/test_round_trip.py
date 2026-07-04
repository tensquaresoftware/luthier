"""Integration tests for ProjectSpec → generate → sidecar fidelity."""

import json

from core.paths import host_workspace_field_key
from core.project_spec import ProjectSpec
from tests.conftest import (
    assert_spec_equal,
    generate_project,
    make_spec,
    write_project,
)

_REQUIRED_WRITER_PATHS = (
    "CMakeLists.txt",
    "CMakeUserPresets.json",
    ".luthier.json",
    "Source/PluginProcessor.h",
    "Source/PluginProcessor.cpp",
    "Source/PluginEditor.h",
    "Source/PluginEditor.cpp",
)


def test_writer_output_contains_required_files(tmp_path):
    spec = make_spec(tmp_path)
    dest, _ = write_project(tmp_path, spec)
    for rel in _REQUIRED_WRITER_PATHS:
        assert (dest / rel).is_file(), rel


def test_sidecar_json_matches_spec(tmp_path):
    project_dir, spec = generate_project(tmp_path)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert data == spec.to_dict()
    assert "accentColor" not in data


def test_sidecar_json_round_trip(tmp_path):
    project_dir, spec = generate_project(tmp_path)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    host_dest = host_workspace_field_key("destination")
    data[host_dest] = str(project_dir.parent)
    restored = ProjectSpec.from_dict(data)
    assert_spec_equal(restored, spec)


def test_generated_cmakelists_has_no_project_configuration_reference(tmp_path):
    project_dir, _ = generate_project(tmp_path)
    content = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "project-configuration.cmake" not in content


def test_template_override_applied_at_generation(tmp_path):
    overrides = tmp_path / "overrides"
    overrides.mkdir()
    marker = "// CUSTOM_OVERRIDE_MARKER"
    (overrides / "PluginProcessor.h").write_text(marker, encoding="utf-8")
    project_dir, _ = generate_project(tmp_path, overrides=overrides)
    content = (project_dir / "Source/PluginProcessor.h").read_text(encoding="utf-8")
    assert marker in content


def test_juce_dir_written_to_sidecar(tmp_path):
    juce_path = "/tmp/juce-test"
    host_juce = host_workspace_field_key("juce")
    spec = make_spec(tmp_path, juce_dir=juce_path)
    project_dir, _ = generate_project(tmp_path, spec=spec)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert data[host_juce] == juce_path
    assert "accentColor" not in data
    restored = ProjectSpec.from_dict(data)
    assert restored.host_juce_dir() == juce_path


def test_generated_cmake_uses_per_os_juce_workspace(tmp_path):
    spec = make_spec(
        tmp_path,
        juce_dir_windows="C:/Users/Guillaume/Dev/SDKs/JUCE",
        juce_dir_macos="/Volumes/Guillaume/Dev/SDKs/JUCE",
        juce_dir_linux="/home/guillaume/Dev/SDKs/JUCE",
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cmake = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'set(JUCE_DIR_WINDOWS "C:/Users/Guillaume/Dev/SDKs/JUCE")' in cmake
    assert 'set(JUCE_DIR_MACOS   "/Volumes/Guillaume/Dev/SDKs/JUCE")' in cmake
    assert 'set(JUCE_DIR_LINUX   "/home/guillaume/Dev/SDKs/JUCE")' in cmake
    assert 'set(JUCE_DIR "/Volumes' not in cmake


