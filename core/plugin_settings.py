"""Plugin type flags, AU/VST3 categories and bundle identifier.

Pure functions shared by the form and the generator.
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

AUDIO_IO_PRESETS = ("stereo", "mono", "synth-no-input", "midi-effect")

_AUDIO_IO_LEGACY = {
    "synth_no_input": "synth-no-input",
    "midi_effect": "midi-effect",
}

LOCKED_ON = "locked_on"
LOCKED_OFF = "locked_off"
OPTIONAL = "optional"

# type_key -> (is_synth, is_midi_effect, needs_midi_input, needs_midi_output)
_PRESET_BOOLS = {
    TYPE_INSTRUMENT: (True, False, True, False),
    TYPE_AUDIO_EFFECT: (False, False, False, False),
    TYPE_MIDI_EFFECT: (False, True, True, True),
}

_PRESET_AUDIO_IO = {
    TYPE_INSTRUMENT: "stereo",
    TYPE_AUDIO_EFFECT: "stereo",
    TYPE_MIDI_EFFECT: "midi-effect",
}

_PRESET_CHECKBOX_RULES = {
    TYPE_INSTRUMENT: {
        "is_synth": LOCKED_ON,
        "needs_midi_input": LOCKED_ON,
        "needs_midi_output": OPTIONAL,
        "is_midi_effect": LOCKED_OFF,
        "editor_wants_keyboard_focus": OPTIONAL,
    },
    TYPE_AUDIO_EFFECT: {
        "is_synth": LOCKED_OFF,
        "needs_midi_input": OPTIONAL,
        "needs_midi_output": OPTIONAL,
        "is_midi_effect": LOCKED_OFF,
        "editor_wants_keyboard_focus": OPTIONAL,
    },
    TYPE_MIDI_EFFECT: {
        "is_synth": LOCKED_OFF,
        "needs_midi_input": LOCKED_ON,
        "needs_midi_output": LOCKED_ON,
        "is_midi_effect": LOCKED_ON,
        "editor_wants_keyboard_focus": OPTIONAL,
    },
}


def _require_type_key(type_key: str) -> None:
    if type_key not in _PRESET_BOOLS:
        valid = ", ".join(key for key, _ in PLUGIN_TYPES)
        raise ValueError(
            f"Unknown plugin type {type_key!r}. Expected one of: {valid}."
        )


def preset_characteristics(type_key: str) -> dict[str, bool]:
    _require_type_key(type_key)
    is_synth, is_midi, midi_in, midi_out = _PRESET_BOOLS[type_key]
    return {
        "is_synth": is_synth,
        "is_midi_effect": is_midi,
        "needs_midi_input": midi_in,
        "needs_midi_output": midi_out,
    }


def preset_audio_io(type_key: str) -> str:
    _require_type_key(type_key)
    return _PRESET_AUDIO_IO[type_key]


def preset_checkbox_rules(type_key: str) -> dict[str, str]:
    _require_type_key(type_key)
    return dict(_PRESET_CHECKBOX_RULES[type_key])


def normalize_audio_io_preset(value: str) -> str:
    text = str(value or "").strip()
    text = _AUDIO_IO_LEGACY.get(text, text)
    if text not in AUDIO_IO_PRESETS:
        return "stereo"
    return text


def audio_io_combo_options(type_key: str) -> list[tuple[str, str]]:
    _require_type_key(type_key)
    if type_key == TYPE_MIDI_EFFECT:
        return [("MIDI Effect", "midi-effect")]
    return [
        ("Stereo", "stereo"),
        ("Mono", "mono"),
        ("Synth No Input", "synth-no-input"),
    ]


def characteristics_conflict(is_synth: bool, is_midi_effect: bool) -> tuple[bool, str]:
    if is_synth and is_midi_effect:
        return False, "Synth and MIDI Effect cannot both be enabled."
    return True, ""


def clamp_midi_count(value, default: int = 16) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    if number < 1 or number > 16:
        return default
    return number


def _bool_to_cmake(value: bool) -> str:
    return "TRUE" if value else "FALSE"


_EMPTY_BUSES_BODY = "    return {};"

_OUT_STEREO_ONLY_BODY = """\
    juce::AudioProcessor::BusesProperties properties;
    return properties.withOutput("Output", juce::AudioChannelSet::stereo(), true);"""

_STEREO_EFFECT_BODY = """\
    juce::AudioProcessor::BusesProperties properties;
    properties = properties.withInput("Input", juce::AudioChannelSet::stereo(), true);
    return properties.withOutput("Output", juce::AudioChannelSet::stereo(), true);"""

_MONO_EFFECT_BODY = """\
    juce::AudioProcessor::BusesProperties properties;
    properties = properties.withInput("Input", juce::AudioChannelSet::mono(), true);
    return properties.withOutput("Output", juce::AudioChannelSet::mono(), true);"""

_MONO_OUT_ONLY_BODY = """\
    juce::AudioProcessor::BusesProperties properties;
    return properties.withOutput("Output", juce::AudioChannelSet::mono(), true);"""


def buses_properties_body(is_synth: bool, is_midi_effect: bool, audio_io_preset: str) -> str:
    preset = normalize_audio_io_preset(audio_io_preset)
    if is_midi_effect or preset == "midi-effect":
        return _EMPTY_BUSES_BODY
    if preset == "synth-no-input":
        return _OUT_STEREO_ONLY_BODY
    if preset == "mono":
        return _MONO_OUT_ONLY_BODY if is_synth else _MONO_EFFECT_BODY
    return _OUT_STEREO_ONLY_BODY if is_synth else _STEREO_EFFECT_BODY


def flags_for_type(type_key: str) -> dict:
    chars = preset_characteristics(type_key)
    return {
        "isSynth": _bool_to_cmake(chars["is_synth"]),
        "isMidiEffect": _bool_to_cmake(chars["is_midi_effect"]),
        "needsMidiInput": _bool_to_cmake(chars["needs_midi_input"]),
        "needsMidiOutput": _bool_to_cmake(chars["needs_midi_output"]),
    }


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
