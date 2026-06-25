"""Unit tests for core.render_context — build_context and build_tokens."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

from core.project_spec import ProjectSpec
from core.render_context import build_context, build_tokens

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
    "synth": {
        "isSynth": "TRUE",
        "isMidiEffect": "FALSE",
        "needsMidiInput": "TRUE",
        "needsMidiOutput": "FALSE",
    },
    "effect": {
        "isSynth": "FALSE",
        "isMidiEffect": "FALSE",
        "needsMidiInput": "FALSE",
        "needsMidiOutput": "FALSE",
    },
    "midi": {
        "isSynth": "FALSE",
        "isMidiEffect": "TRUE",
        "needsMidiInput": "TRUE",
        "needsMidiOutput": "TRUE",
    },
}

_EXPECTED_CATEGORIES = {
    "synth": ("kAudioUnitType_MusicDevice", "Instrument|Synth"),
    "effect": ("kAudioUnitType_Effect", "Fx"),
    "midi": ("kAudioUnitType_MIDIProcessor", "Fx|MIDI"),
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
        destination_dir=str(Path(tempfile.gettempdir())),
        plugin_type="synth",
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
    defaults.update(kwargs)
    return ProjectSpec(**defaults)


def test_build_context_empty_optional_cmake_blocks():
    spec = _make_spec(
        plugin_type="synth",
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


@pytest.mark.parametrize("plugin_type", ["synth", "effect", "midi"])
def test_build_context_plugin_type_flags_and_categories(plugin_type):
    spec = _make_spec(plugin_type=plugin_type)
    ctx = build_context(spec)
    for key, value in _EXPECTED_FLAGS[plugin_type].items():
        assert ctx[key] == value
    au_main_type, vst3_categories = _EXPECTED_CATEGORIES[plugin_type]
    assert ctx["auMainType"] == au_main_type
    assert ctx["vst3Categories"] == vst3_categories


def test_build_context_value_keys_passthrough():
    spec = _make_spec()
    ctx = build_context(spec)
    d = spec.to_dict()
    for key in _VALUE_KEYS:
        assert ctx[key] == d[key]


def test_build_context_juce_dir_empty():
    spec = _make_spec(juce_dir="")
    assert build_context(spec)["juceDirSetLine"] == ""
    spec_whitespace = _make_spec(juce_dir="   ")
    assert build_context(spec_whitespace)["juceDirSetLine"] == ""


def test_build_context_juce_dir_set():
    spec = _make_spec(juce_dir="/Applications/JUCE")
    line = build_context(spec)["juceDirSetLine"]
    assert line == 'set(JUCE_DIR "/Applications/JUCE")\n'


def test_build_tokens_returns_project_keys():
    spec = _make_spec(project_name="Alpha", project_display_name="Alpha Display")
    tokens = build_tokens(spec)
    assert tokens == {
        "PROJECT_NAME": "Alpha",
        "PROJECT_DISPLAY_NAME": "Alpha Display",
    }


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
