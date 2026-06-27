"""Plugin type flags, AU/VST3 categories and bundle identifier.

Pure functions shared by the form, the project reader and the generator.
"""

import re

PLUGIN_TYPES = [
    ("synth", "Instrument"),
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
