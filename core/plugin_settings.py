"""Plugin type flags, AU/VST3 categories and bundle identifier.

Pure functions shared by the form, the project reader and the generator.
"""

import re

TYPE_INSTRUMENT = "instrument"
TYPE_AUDIO_EFFECT = "audio-effect"
TYPE_MIDI_EFFECT = "midi-effect"

PLUGIN_TYPES = [
    (TYPE_INSTRUMENT, "Instrument"),
    (TYPE_AUDIO_EFFECT, "Audio Effect"),
    (TYPE_MIDI_EFFECT, "MIDI Effect"),
]

# type_key -> (isSynth, isMidiEffect, needsMidiInput, needsMidiOutput)
_FLAGS = {
    TYPE_INSTRUMENT: ("TRUE", "FALSE", "TRUE", "FALSE"),
    TYPE_AUDIO_EFFECT: ("FALSE", "FALSE", "FALSE", "FALSE"),
    TYPE_MIDI_EFFECT: ("FALSE", "TRUE", "TRUE", "TRUE"),
}


def flags_for_type(type_key: str) -> dict:
    if type_key not in _FLAGS:
        valid = ", ".join(key for key, _ in PLUGIN_TYPES)
        raise ValueError(
            f"Unknown plugin type {type_key!r}. Expected one of: {valid}."
        )
    is_synth, is_midi, midi_in, midi_out = _FLAGS[type_key]
    return {
        "isSynth": is_synth,
        "isMidiEffect": is_midi,
        "needsMidiInput": midi_in,
        "needsMidiOutput": midi_out,
    }


def type_for_flags(is_synth: str, is_midi_effect: str) -> str:
    if is_synth == "TRUE":
        return TYPE_INSTRUMENT
    if is_midi_effect == "TRUE":
        return TYPE_MIDI_EFFECT
    return TYPE_AUDIO_EFFECT


def bundle_id(manufacturer_name: str, project_name: str) -> str:
    manufacturer = re.sub(r"[^a-zA-Z0-9]", "", manufacturer_name)
    if manufacturer and not manufacturer[0].isalpha():
        manufacturer = "Company" + manufacturer
    project = re.sub(r"[^a-zA-Z0-9_-]", "", project_name)
    return f"com.{manufacturer}.{project}"


def au_and_vst3_categories(is_synth: str, is_midi_effect: str) -> tuple[str, str]:
    if is_synth == "TRUE":
        return "kAudioUnitType_MusicDevice", "Instrument|Synth"
    if is_midi_effect == "TRUE":
        return "kAudioUnitType_MIDIProcessor", "Fx|MIDI"
    return "kAudioUnitType_Effect", "Fx"
