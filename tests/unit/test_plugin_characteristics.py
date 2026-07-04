"""Unit tests for plugin preset defaults and characteristic validation."""

import sys

import pytest

from core.plugin_settings import (
    AUDIO_IO_PRESETS,
    LOCKED_OFF,
    LOCKED_ON,
    OPTIONAL,
    PLUGIN_TYPES,
    TYPE_AUDIO_EFFECT,
    TYPE_INSTRUMENT,
    TYPE_MIDI_EFFECT,
    characteristics_conflict,
    clamp_midi_count,
    flags_for_type,
    normalize_audio_io_preset,
    preset_audio_io,
    preset_characteristics,
    preset_checkbox_rules,
)

_EXPECTED_PRESET_BOOLS = {
    TYPE_INSTRUMENT: {
        "is_synth": True,
        "is_midi_effect": False,
        "needs_midi_input": True,
        "needs_midi_output": False,
    },
    TYPE_AUDIO_EFFECT: {
        "is_synth": False,
        "is_midi_effect": False,
        "needs_midi_input": False,
        "needs_midi_output": False,
    },
    TYPE_MIDI_EFFECT: {
        "is_synth": False,
        "is_midi_effect": True,
        "needs_midi_input": True,
        "needs_midi_output": True,
    },
}

_EXPECTED_AUDIO_IO = {
    TYPE_INSTRUMENT: "stereo",
    TYPE_AUDIO_EFFECT: "stereo",
    TYPE_MIDI_EFFECT: "midi-effect",
}


@pytest.mark.parametrize("type_key", [key for key, _ in PLUGIN_TYPES])
def test_preset_characteristics_defaults(type_key):
    assert preset_characteristics(type_key) == _EXPECTED_PRESET_BOOLS[type_key]


@pytest.mark.parametrize("type_key", [key for key, _ in PLUGIN_TYPES])
def test_preset_audio_io_defaults(type_key):
    assert preset_audio_io(type_key) == _EXPECTED_AUDIO_IO[type_key]


def test_instrument_preset_only_midi_output_is_optional():
    rules = preset_checkbox_rules(TYPE_INSTRUMENT)
    assert rules["needs_midi_output"] == OPTIONAL
    assert rules["is_synth"] == LOCKED_ON
    assert rules["is_midi_effect"] == LOCKED_OFF


def test_audio_effect_preset_only_locks_identity_characteristics():
    rules = preset_checkbox_rules(TYPE_AUDIO_EFFECT)
    assert rules["is_synth"] == LOCKED_OFF
    assert rules["is_midi_effect"] == LOCKED_OFF
    assert rules["needs_midi_input"] == OPTIONAL
    assert rules["needs_midi_output"] == OPTIONAL
    assert rules["editor_wants_keyboard_focus"] == OPTIONAL


def test_midi_effect_preset_locks_required_characteristics_on():
    rules = preset_checkbox_rules(TYPE_MIDI_EFFECT)
    assert rules["is_midi_effect"] == LOCKED_ON
    assert rules["needs_midi_input"] == LOCKED_ON
    assert rules["needs_midi_output"] == LOCKED_ON
    assert rules["is_synth"] == LOCKED_OFF


@pytest.mark.parametrize(
    "legacy,expected",
    [
        ("synth_no_input", "synth-no-input"),
        ("midi_effect", "midi-effect"),
        ("stereo", "stereo"),
        ("unknown", "stereo"),
    ],
)
def test_normalize_audio_io_preset(legacy, expected):
    assert normalize_audio_io_preset(legacy) == expected


def test_instrument_preset_allows_matrix_control_defaults():
    chars = preset_characteristics(TYPE_INSTRUMENT)
    assert chars["is_synth"] is True
    assert chars["needs_midi_input"] is True
    assert chars["needs_midi_output"] is False


def test_characteristics_conflict_rejects_synth_and_midi_effect():
    ok, message = characteristics_conflict(True, True)
    assert ok is False
    assert "Synth and MIDI Effect" in message


def test_characteristics_conflict_accepts_instrument_defaults():
    chars = preset_characteristics(TYPE_INSTRUMENT)
    ok, message = characteristics_conflict(chars["is_synth"], chars["is_midi_effect"])
    assert ok is True
    assert message == ""


def test_instrument_with_midi_output_matrix_control_valid():
    """Matrix-Control: instrument preset + needs_midi_output=True is valid."""
    from core.project_spec import ProjectSpec

    chars = preset_characteristics(TYPE_INSTRUMENT)
    assert chars["needs_midi_output"] is False
    spec = ProjectSpec(
        project_name="MatrixControl",
        project_version="1.0.0",
        plugin_type=TYPE_INSTRUMENT,
        is_synth=chars["is_synth"],
        is_midi_effect=chars["is_midi_effect"],
        needs_midi_input=chars["needs_midi_input"],
        needs_midi_output=True,
    )
    ok, message = characteristics_conflict(spec.is_synth, spec.is_midi_effect)
    assert ok is True
    assert message == ""
    assert spec.needs_midi_output is True


@pytest.mark.parametrize(
    "value,expected",
    [
        (16, 16),
        (1, 1),
        (0, 16),
        (17, 16),
        ("8", 8),
        ("bad", 16),
        (None, 16),
    ],
)
def test_clamp_midi_count(value, expected):
    assert clamp_midi_count(value) == expected


def test_flags_for_type_still_returns_cmake_strings_from_presets():
    flags = flags_for_type(TYPE_INSTRUMENT)
    assert flags == {
        "isSynth": "TRUE",
        "isMidiEffect": "FALSE",
        "needsMidiInput": "TRUE",
        "needsMidiOutput": "FALSE",
    }


def test_audio_io_presets_use_kebab_case():
    assert set(AUDIO_IO_PRESETS) == {
        "stereo",
        "mono",
        "synth-no-input",
        "midi-effect",
    }


def test_plugin_characteristics_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.plugin_settings  # noqa: F401

    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
