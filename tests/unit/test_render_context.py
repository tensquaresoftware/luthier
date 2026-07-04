"""Unit tests for core.render_context — build_context and build_tokens."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

from core.paths import host_workspace_field_key
from core.plugin_settings import (
    TYPE_AUDIO_EFFECT,
    TYPE_INSTRUMENT,
    TYPE_MIDI_EFFECT,
    buses_properties_body,
    preset_characteristics,
)
from core.project_spec import ProjectSpec
from core.render_context import build_context, build_tokens, characteristics_cmake_context
from tests.conftest import workspace_attr

_VALUE_KEYS = (
    "projectName",
    "projectDisplayName",
    "projectVersion",
    "manufacturerName",
    "manufacturerCode",
    "pluginCode",
    "pluginFormats",
)

_EXPECTED_FLAGS = {
    TYPE_INSTRUMENT: {
        "isSynth": "TRUE",
        "isMidiEffect": "FALSE",
        "needsMidiInput": "TRUE",
        "needsMidiOutput": "FALSE",
    },
    TYPE_AUDIO_EFFECT: {
        "isSynth": "FALSE",
        "isMidiEffect": "FALSE",
        "needsMidiInput": "FALSE",
        "needsMidiOutput": "FALSE",
    },
    TYPE_MIDI_EFFECT: {
        "isSynth": "FALSE",
        "isMidiEffect": "TRUE",
        "needsMidiInput": "TRUE",
        "needsMidiOutput": "TRUE",
    },
}

_EXPECTED_CATEGORIES = {
    TYPE_INSTRUMENT: ("kAudioUnitType_MusicDevice", "Instrument|Synth"),
    TYPE_AUDIO_EFFECT: ("kAudioUnitType_Effect", "Fx"),
    TYPE_MIDI_EFFECT: ("kAudioUnitType_MIDIProcessor", "Fx|MIDI"),
}


def _make_spec(**kwargs):
    defaults = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        project_version="1.0.0",
        manufacturer_name="Acme",
        manufacturer_code="Acme",
        plugin_code="Mypl",
        company_copyright="Copyright 2026",
        company_website="https://acme.example",
        company_email="dev@acme.example",
        destination_dir_windows="",
        destination_dir_macos="",
        destination_dir_linux="",
        juce_dir_windows="",
        juce_dir_macos="",
        juce_dir_linux="",
        plugin_type=TYPE_INSTRUMENT,
        plugin_formats="VST3",
        cxx_standard="C++20",
        preprocessor_definitions="FOO=1",
        header_search_paths="/extra/include",
        copy_to_system_folders=True,
        copy_to_artefacts_dir=False,
        artefacts_dir_windows="C:\\out",
        artefacts_dir_macos="/out/mac",
        artefacts_dir_linux="/out/linux",
    )
    host_dest = host_workspace_field_key("destination")
    defaults[workspace_attr(host_dest)] = str(Path(tempfile.gettempdir()))
    if "destination_dir" in kwargs:
        dest = kwargs.pop("destination_dir")
        defaults[workspace_attr(host_dest)] = dest
    if "juce_dir" in kwargs:
        juce = kwargs.pop("juce_dir")
        defaults[workspace_attr(host_workspace_field_key("juce"))] = juce
    defaults.update(kwargs)
    return ProjectSpec(**defaults)


def test_build_context_empty_optional_cmake_blocks():
    spec = _make_spec(
        plugin_type=TYPE_INSTRUMENT,
        preprocessor_definitions="",
        header_search_paths="",
    )
    ctx = build_context(spec)
    assert ctx["headerSearchPathsBlock"] == ""
    assert ctx["extraDefinitionsBlock"] == ""


def test_build_context_populated_cmake_blocks():
    spec = _make_spec(
        preprocessor_definitions="FOO=1\nBAR=2",
        header_search_paths="/path/a\n/path/b",
    )
    ctx = build_context(spec)
    assert "target_compile_definitions" in ctx["extraDefinitionsBlock"]
    assert "target_include_directories" in ctx["headerSearchPathsBlock"]
    assert "MyPlugin" in ctx["extraDefinitionsBlock"]
    assert "MyPlugin" in ctx["headerSearchPathsBlock"]


def _spec_with_preset(plugin_type: str, **kwargs):
    chars = preset_characteristics(plugin_type)
    return _make_spec(plugin_type=plugin_type, **chars, **kwargs)


@pytest.mark.parametrize(
    "plugin_type",
    [TYPE_INSTRUMENT, TYPE_AUDIO_EFFECT, TYPE_MIDI_EFFECT],
)
def test_build_context_plugin_type_flags_and_categories(plugin_type):
    spec = _spec_with_preset(plugin_type)
    ctx = build_context(spec)
    for key, value in _EXPECTED_FLAGS[plugin_type].items():
        assert ctx[key] == value
    au_main_type, vst3_categories = _EXPECTED_CATEGORIES[plugin_type]
    assert ctx["auMainType"] == au_main_type
    assert ctx["vst3Categories"] == vst3_categories


def test_build_context_spec_override_matrix_control_midi_output():
    spec = _make_spec(
        plugin_type=TYPE_INSTRUMENT,
        is_synth=True,
        needs_midi_input=True,
        needs_midi_output=True,
    )
    ctx = build_context(spec)
    assert ctx["needsMidiOutput"] == "TRUE"
    assert ctx["needsMidiInput"] == "TRUE"
    assert ctx["isSynth"] == "TRUE"
    assert ctx["auMainType"] == "kAudioUnitType_MusicDevice"
    assert ctx["vst3Categories"] == "Instrument|Synth"


def test_characteristics_cmake_context_plugin_description_quoting():
    spec = _make_spec(plugin_description='Say "hello" \\ world $HOME')
    ctx = characteristics_cmake_context(spec)
    assert ctx["pluginDescription"] == '"Say \\"hello\\" \\\\ world \\$HOME"'


def test_build_context_editor_wants_keyboard_focus_and_midi_counts():
    spec = _make_spec(
        editor_wants_keyboard_focus=True,
        vst_num_midi_ins=4,
        vst_num_midi_outs=8,
    )
    ctx = build_context(spec)
    assert ctx["editorWantsKeyboardFocus"] == "TRUE"
    assert ctx["vstNumMidiIns"] == "4"
    assert ctx["vstNumMidiOuts"] == "8"


def test_build_context_empty_plugin_description():
    spec = _make_spec(plugin_description="")
    ctx = build_context(spec)
    assert ctx["pluginDescription"] == '""'


def test_build_context_value_keys_passthrough():
    spec = _make_spec()
    ctx = build_context(spec)
    d = spec.to_dict()
    for key in _VALUE_KEYS:
        assert ctx[key] == d[key]


def test_build_context_juce_workspace_paths_empty():
    spec = _make_spec(juce_dir="")
    ctx = build_context(spec)
    assert ctx["juceDirWindows"] == '""'
    assert ctx["juceDirMacos"] == '""'
    assert ctx["juceDirLinux"] == '""'


def test_build_context_juce_workspace_paths_set():
    spec = _make_spec(
        juce_dir_windows="C:/JUCE",
        juce_dir_macos="/Applications/JUCE",
        juce_dir_linux="/usr/local/JUCE",
    )
    ctx = build_context(spec)
    assert ctx["juceDirWindows"] == '"C:/JUCE"'
    assert ctx["juceDirMacos"] == '"/Applications/JUCE"'
    assert ctx["juceDirLinux"] == '"/usr/local/JUCE"'


@pytest.mark.parametrize(
    "field_kwargs,expected_key,expected_fragment",
    [
        ({"juce_dir_windows": 'C:/JUCE"bad'}, "juceDirWindows", '"C:/JUCE\\"bad"'),
        ({"juce_dir_macos": "/Applications/My JUCE"}, "juceDirMacos", '"/Applications/My JUCE"'),
        ({"juce_dir_linux": "$ENV{HOME}/JUCE"}, "juceDirLinux", '"\\$ENV{HOME}/JUCE"'),
    ],
)
def test_build_context_juce_workspace_special_characters(field_kwargs, expected_key, expected_fragment):
    spec = _make_spec(**field_kwargs)
    assert build_context(spec)[expected_key] == expected_fragment


def test_build_context_unknown_plugin_type_uses_spec_fields():
    spec = _make_spec(
        plugin_type="Instrument",
        is_synth=False,
        is_midi_effect=False,
        needs_midi_input=False,
        needs_midi_output=True,
    )
    ctx = build_context(spec)
    assert ctx["needsMidiOutput"] == "TRUE"
    assert ctx["isSynth"] == "FALSE"


def test_artefact_entry_escapes_quotes_and_control_chars():
    spec = _make_spec(
        copy_to_artefacts_dir=True,
        artefacts_dir_windows='C:/out"bad\nline',
    )
    entry = build_context(spec)["windowsArtefactEntry"]
    fragment = "{" + entry.lstrip(",\n ") + "}"
    parsed = json.loads(fragment)
    assert parsed["ARTEFACTS_DIR_WINDOWS"] == 'C:/out"bad\nline'


def test_rendered_presets_json_is_valid(tmp_path):
    from core import rendering
    from core.project_generator import templates_dir

    spec = _make_spec(
        copy_to_artefacts_dir=True,
        artefacts_dir_macos='/out/mac"quote',
        juce_dir="/Applications/JUCE",
    )
    ctx = build_context(spec)
    template = (templates_dir() / "CMakeUserPresets.json").read_text(encoding="utf-8")
    rendered = rendering.render(template, ctx)
    json.loads(rendered)


def test_build_tokens_returns_project_keys_and_buses_body():
    spec = _make_spec(
        project_name="Alpha",
        project_display_name="Alpha Display",
        is_synth=True,
        audio_io_preset="stereo",
    )
    tokens = build_tokens(spec)
    assert tokens["PROJECT_NAME"] == "Alpha"
    assert tokens["PROJECT_DISPLAY_NAME"] == "Alpha Display"
    assert tokens["CREATE_BUSES_PROPERTIES_BODY"] == buses_properties_body(
        True, False, "stereo"
    )


def test_render_context_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.render_context  # noqa: F401

    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after


def test_artefact_entry_normalizes_windows_backslashes():
    spec = _make_spec(
        copy_to_artefacts_dir=True,
        artefacts_dir_windows=r"C:\Plugins\out",
    )
    entry = build_context(spec)["windowsArtefactEntry"]
    assert r"C:\Plugins" not in entry
    assert "C:/Plugins/out" in entry
    fragment = "{" + entry.lstrip(",\n ") + "}"
    parsed = json.loads(fragment)
    assert parsed["ARTEFACTS_DIR_WINDOWS"] == "C:/Plugins/out"
