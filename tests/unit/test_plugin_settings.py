"""Unit tests for core.plugin_settings — type flags, categories, bundle ID."""

import sys

import pytest

from core.plugin_settings import (
    PLUGIN_TYPES,
    TYPE_AUDIO_EFFECT,
    TYPE_INSTRUMENT,
    TYPE_MIDI_EFFECT,
    au_and_vst3_categories,
    bundle_id,
    flags_for_type,
    type_for_flags,
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


@pytest.mark.parametrize("type_key", [key for key, _ in PLUGIN_TYPES])
def test_flags_for_type(type_key):
    assert flags_for_type(type_key) == _EXPECTED_FLAGS[type_key]


@pytest.mark.parametrize("type_key", [key for key, _ in PLUGIN_TYPES])
def test_au_and_vst3_categories(type_key):
    flags = flags_for_type(type_key)
    result = au_and_vst3_categories(flags["isSynth"], flags["isMidiEffect"])
    assert result == _EXPECTED_CATEGORIES[type_key]


@pytest.mark.parametrize(
    "manufacturer, project, expected",
    [
        ("Acme Corp", "MyPlugin", "com.AcmeCorp.MyPlugin"),
        ("123Sound", "MyPlugin", "com.Company123Sound.MyPlugin"),
        ("Acme", "my-plugin_v2", "com.Acme.my-plugin_v2"),
    ],
)
def test_bundle_id(manufacturer, project, expected):
    assert bundle_id(manufacturer, project) == expected


@pytest.mark.parametrize("type_key", [key for key, _ in PLUGIN_TYPES])
def test_type_for_flags_round_trip(type_key):
    flags = flags_for_type(type_key)
    assert type_for_flags(flags["isSynth"], flags["isMidiEffect"]) == type_key


def test_plugin_settings_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.plugin_settings  # noqa: F401

    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
