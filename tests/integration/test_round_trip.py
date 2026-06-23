"""Integration tests for ProjectSpec → generate → read round-trip fidelity."""

import json
import re

import pytest

from core.project_spec import ProjectSpec
from tests.conftest import (
    all_files,
    assert_spec_equal,
    assert_trees_equal,
    generate_project,
    install_legacy_project_configuration_cmake,
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


def test_read_project_returns_equivalent_spec(tmp_path):
    from core import project_reader

    project_dir, spec = generate_project(tmp_path)
    loaded = project_reader.read_project(project_dir)
    assert loaded is not None
    assert_spec_equal(loaded, spec)


def test_sidecar_json_round_trip(tmp_path):
    project_dir, spec = generate_project(tmp_path)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    data["destinationDir"] = str(project_dir.parent)
    restored = ProjectSpec.from_dict(data)
    assert_spec_equal(restored, spec)


def test_regenerate_produces_identical_tree(tmp_path):
    from core import project_reader
    from core.project_generator import ProjectGenerator

    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec, juce_dir="")
    before = all_files(project_dir)

    loaded = project_reader.read_project(project_dir)
    assert loaded is not None
    project_dir = generator.generate(loaded, juce_dir="")
    assert_trees_equal(before, all_files(project_dir))


def test_cmake_fallback_returns_complete_spec(tmp_path):
    from core import project_reader

    project_dir, spec = generate_project(tmp_path)
    (project_dir / ".luthier.json").unlink()
    result = project_reader.read_project_result(project_dir)
    assert result.spec is not None
    assert result.missing_fields == ()
    assert_spec_equal(result.spec, spec)


def test_cmake_fallback_regenerate_identical_tree(tmp_path):
    from core import project_reader
    from core.project_generator import ProjectGenerator

    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec, juce_dir="")
    before = all_files(project_dir)
    (project_dir / ".luthier.json").unlink()

    loaded = project_reader.read_project_result(project_dir)
    assert loaded.spec is not None
    assert loaded.missing_fields == ()
    project_dir = generator.generate(loaded.spec, juce_dir="")
    assert_trees_equal(before, all_files(project_dir))


def test_partial_cmake_returns_none_not_partial_spec(tmp_path):
    from core import project_reader

    project_dir, _ = generate_project(tmp_path)
    (project_dir / ".luthier.json").unlink()
    cmake = project_dir / "CMakeLists.txt"
    text = cmake.read_text(encoding="utf-8")
    text = re.sub(r'^\s*COMPANY_NAME\s+"[^"]*"\s*$', "", text, flags=re.MULTILINE)
    cmake.write_text(text, encoding="utf-8")

    result = project_reader.read_project_result(project_dir)
    assert result.spec is None
    assert "Company Name" in result.missing_fields


def test_no_cmakelists_returns_none(tmp_path):
    from core import project_reader

    result = project_reader.read_project_result(tmp_path)
    assert result.spec is None
    assert result.missing_fields == ()


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


def test_legacy_project_configuration_cmake_compat(tmp_path):
    from core import project_reader

    project_dir, original = generate_project(tmp_path)
    install_legacy_project_configuration_cmake(project_dir)

    result = project_reader.read_project_result(project_dir)
    assert result.spec is not None
    assert result.missing_fields == ()
    assert result.spec.copy_to_system_folders
    assert not result.spec.copy_to_artefacts_dir
    assert result.spec.artefacts_dir_windows == "C:\\legacy\\win"
    assert result.spec.artefacts_dir_macos == "/legacy/mac"
    assert result.spec.artefacts_dir_linux == "/legacy/linux"
    assert result.spec.project_name == original.project_name
