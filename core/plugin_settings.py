"""Plugin type -> ProjectData flags.

Mirror of InputCollector._configurePluginSettings / _midiDefaultsForPluginType
(those are private to the generator's CLI collector). AU/VST3 categories stay
derived by the generator's own updateAuAndVst3Categories.
"""

PLUGIN_TYPES = [
    ("synth", "Synthesizer"),
    ("effect", "Audio Effect"),
    ("midi", "MIDI Effect"),
]

# type_key -> (isSynth, isMidiEffect, needsMidiInput, needsMidiOutput)
_FLAGS = {
    "synth": ("TRUE", "FALSE", "TRUE", "FALSE"),
    "effect": ("FALSE", "FALSE", "FALSE", "FALSE"),
    "midi": ("FALSE", "TRUE", "TRUE", "TRUE"),
}


def flags_for_type(type_key: str) -> dict:
    is_synth, is_midi, midi_in, midi_out = _FLAGS[type_key]
    return {
        "isSynth": is_synth,
        "isMidiEffect": is_midi,
        "needsMidiInput": midi_in,
        "needsMidiOutput": midi_out,
    }


def type_for_flags(is_synth: str, is_midi_effect: str) -> str:
    if is_synth == "TRUE":
        return "synth"
    if is_midi_effect == "TRUE":
        return "midi"
    return "effect"
