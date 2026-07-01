"""Integration tests for ProjectSpec → generate → read round-trip fidelity."""

import json

from core.paths import host_workspace_field_key
from core.project_spec import ProjectSpec
from tests.conftest import (
    all_files,
    assert_spec_equal,
    assert_trees_equal,
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


def test_read_project_returns_equivalent_spec(tmp_path):
    from core import project_reader

    project_dir, spec = generate_project(tmp_path)
    loaded = project_reader.read_project_result(project_dir).spec
    assert loaded is not None
    assert_spec_equal(loaded, spec)


def test_sidecar_json_round_trip(tmp_path):
    project_dir, spec = generate_project(tmp_path)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    host_dest = host_workspace_field_key("destination")
    data[host_dest] = str(project_dir.parent)
    restored = ProjectSpec.from_dict(data)
    assert_spec_equal(restored, spec)


def test_regenerate_produces_identical_tree(tmp_path):
    from core import project_reader
    from core.project_generator import ProjectGenerator

    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec)
    before = all_files(project_dir)

    loaded = project_reader.read_project_result(project_dir).spec
    assert loaded is not None
    project_dir = generator.generate(loaded)
    assert_trees_equal(before, all_files(project_dir))


def test_open_without_sidecar_returns_error(tmp_path):
    from core import project_reader

    project_dir, _ = generate_project(tmp_path)
    (project_dir / ".luthier.json").unlink()
    result = project_reader.read_project_result(project_dir)
    assert result.spec is None
    assert result.error
    assert ".luthier.json" in result.error


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


def test_juce_dir_sidecar_round_trip(tmp_path):
    from core import project_reader

    juce_path = "/tmp/juce-test"
    host_juce = host_workspace_field_key("juce")
    spec = make_spec(tmp_path, juce_dir=juce_path)
    project_dir, _ = generate_project(tmp_path, spec=spec)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert data[host_juce] == juce_path
    loaded = project_reader.read_project_result(project_dir).spec
    assert loaded is not None
    assert loaded.host_juce_dir() == juce_path


def test_regenerate_preserves_juce_dir(tmp_path):
    from core import project_reader
    from core.project_generator import ProjectGenerator

    juce_path = "/Applications/JUCE"
    spec = make_spec(tmp_path, juce_dir=juce_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec)
    cmake_before = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert f'set(JUCE_DIR "{juce_path}")' in cmake_before
    sidecar_before = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))

    loaded = project_reader.read_project_result(project_dir).spec
    assert loaded is not None
    generator.generate(loaded)
    sidecar_after = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert sidecar_after == sidecar_before
    cmake_after = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert f'set(JUCE_DIR "{juce_path}")' in cmake_after
