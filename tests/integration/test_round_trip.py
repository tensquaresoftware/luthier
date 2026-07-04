"""Integration tests for ProjectSpec → generate → sidecar fidelity."""

import json

import pytest

from core.paths import host_workspace_field_key
from core.plugin_settings import (
    TYPE_AUDIO_EFFECT,
    TYPE_INSTRUMENT,
    TYPE_MIDI_EFFECT,
    preset_audio_io,
    preset_characteristics,
)
from core.project_spec import ProjectSpec
from tests.conftest import (
    assert_sidecar_omits_accent,
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
    assert_sidecar_omits_accent(data)


def test_sidecar_json_round_trip(tmp_path):
    project_dir, spec = generate_project(tmp_path)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert_sidecar_omits_accent(data)
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
    assert_sidecar_omits_accent(data)
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


def test_matrix_control_midi_output_in_cmake(tmp_path):
    spec = make_spec(
        tmp_path,
        plugin_type=TYPE_INSTRUMENT,
        needs_midi_output=True,
        is_synth=True,
        needs_midi_input=True,
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cmake = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "NEEDS_MIDI_OUTPUT TRUE" in cmake
    assert "NEEDS_MIDI_INPUT TRUE" in cmake
    assert "IS_SYNTH TRUE" in cmake


def test_generated_plugin_description_in_cmake(tmp_path):
    spec = make_spec(tmp_path, plugin_description='My "Plugin" v1')
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cmake = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'DESCRIPTION "My \\"Plugin\\" v1"' in cmake


def test_generated_mono_effect_buses_in_processor_cpp(tmp_path):
    spec = make_spec(
        tmp_path,
        plugin_type=TYPE_AUDIO_EFFECT,
        is_synth=False,
        is_midi_effect=False,
        audio_io_preset="mono",
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cpp = (project_dir / "Source/PluginProcessor.cpp").read_text(encoding="utf-8")
    assert 'withInput("Input", juce::AudioChannelSet::mono(), true)' in cpp
    assert 'withOutput("Output", juce::AudioChannelSet::mono(), true)' in cpp


def test_generated_midi_effect_empty_buses(tmp_path):
    spec = make_spec(
        tmp_path,
        plugin_type=TYPE_MIDI_EFFECT,
        is_synth=False,
        is_midi_effect=True,
        audio_io_preset="midi-effect",
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cmake = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    cpp = (project_dir / "Source/PluginProcessor.cpp").read_text(encoding="utf-8")
    assert "IS_MIDI_EFFECT TRUE" in cmake
    assert "return {};" in cpp


def test_session_regenerate_updates_characteristics(tmp_path):
    spec = make_spec(
        tmp_path,
        plugin_type=TYPE_INSTRUMENT,
        is_synth=True,
        needs_midi_output=False,
        editor_wants_keyboard_focus=False,
        audio_io_preset="stereo",
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cmake_before = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    cpp_before = (project_dir / "Source/PluginProcessor.cpp").read_text(encoding="utf-8")
    assert "NEEDS_MIDI_OUTPUT FALSE" in cmake_before
    assert "EDITOR_WANTS_KEYBOARD_FOCUS FALSE" in cmake_before
    assert 'withOutput("Output", juce::AudioChannelSet::stereo(), true)' in cpp_before
    assert "withInput" not in cpp_before

    spec.needs_midi_output = True
    spec.editor_wants_keyboard_focus = True
    spec.audio_io_preset = "mono"
    generate_project(tmp_path, spec=spec, allow_overwrite=True)
    cmake_after = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    cpp_after = (project_dir / "Source/PluginProcessor.cpp").read_text(encoding="utf-8")
    assert "NEEDS_MIDI_OUTPUT TRUE" in cmake_after
    assert "EDITOR_WANTS_KEYBOARD_FOCUS TRUE" in cmake_after
    assert 'withOutput("Output", juce::AudioChannelSet::mono(), true)' in cpp_after
    assert "withInput" not in cpp_after
    sidecar = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert_sidecar_omits_accent(sidecar)
    assert_spec_equal(ProjectSpec.from_dict(sidecar), spec)


@pytest.mark.parametrize(
    "plugin_type,cmake_flags",
    [
        (
            TYPE_INSTRUMENT,
            ["IS_SYNTH TRUE", "NEEDS_MIDI_INPUT TRUE", "NEEDS_MIDI_OUTPUT FALSE"],
        ),
        (
            TYPE_AUDIO_EFFECT,
            ["IS_SYNTH FALSE", "IS_MIDI_EFFECT FALSE"],
        ),
        (
            TYPE_MIDI_EFFECT,
            [
                "IS_MIDI_EFFECT TRUE",
                "NEEDS_MIDI_INPUT TRUE",
                "NEEDS_MIDI_OUTPUT TRUE",
            ],
        ),
    ],
)
def test_scaffold_cmake_flags_match_plugin_type_preset(
    tmp_path, plugin_type, cmake_flags
):
    chars = preset_characteristics(plugin_type)
    spec = make_spec(
        tmp_path,
        plugin_type=plugin_type,
        audio_io_preset=preset_audio_io(plugin_type),
        **chars,
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cmake = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    for flag in cmake_flags:
        assert flag in cmake

