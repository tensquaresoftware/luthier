"""Unit tests for buses_properties_body — createBusesProperties() C++ generation."""

import pytest

from core.plugin_settings import buses_properties_body

_EMPTY = "    return {};"
_STEREO_OUT = 'withOutput("Output", juce::AudioChannelSet::stereo(), true)'
_MONO_OUT = 'withOutput("Output", juce::AudioChannelSet::mono(), true)'
_STEREO_IN = 'withInput("Input", juce::AudioChannelSet::stereo(), true)'
_MONO_IN = 'withInput("Input", juce::AudioChannelSet::mono(), true)'


@pytest.mark.parametrize(
    "is_synth,is_midi_effect,preset,expect_in,expect_out,expect_empty",
    [
        (False, False, "stereo", _STEREO_IN, _STEREO_OUT, False),
        (True, False, "stereo", None, _STEREO_OUT, False),
        (False, False, "mono", _MONO_IN, _MONO_OUT, False),
        (True, False, "mono", None, _MONO_OUT, False),
        (True, False, "synth-no-input", None, _STEREO_OUT, False),
        (False, True, "stereo", None, None, True),
        (False, False, "midi-effect", None, None, True),
    ],
)
def test_buses_properties_body_presets(
    is_synth, is_midi_effect, preset, expect_in, expect_out, expect_empty
):
    body = buses_properties_body(is_synth, is_midi_effect, preset)
    if expect_empty:
        assert body == _EMPTY
        return
    assert expect_out in body
    if expect_in:
        assert expect_in in body
    else:
        assert "withInput" not in body


def test_buses_properties_body_midi_effect_overrides_stereo_preset():
    body = buses_properties_body(True, True, "stereo")
    assert body == _EMPTY


def test_buses_properties_body_normalizes_legacy_preset():
    body = buses_properties_body(False, False, "synth_no_input")
    assert _STEREO_OUT in body
    assert "withInput" not in body
