"""Plugin characteristic toggles, audio I/O preset, and MIDI channel counts."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from app.qss import repolish
from app.widgets.combo_field import ComboField
from app.widgets.validated_field import make_field_label
from core.plugin_settings import (
    LOCKED_OFF,
    LOCKED_ON,
    PLUGIN_TYPES,
    TYPE_MIDI_EFFECT,
    audio_io_combo_options,
    characteristics_conflict,
    normalize_audio_io_preset,
    preset_audio_io,
    preset_characteristics,
    preset_checkbox_rules,
)

_CHARACTERISTIC_LABELS = (
    ("is_synth", "Plugin is a Synth"),
    ("needs_midi_input", "Plugin MIDI Input"),
    ("needs_midi_output", "Plugin MIDI Output"),
    ("is_midi_effect", "MIDI Effect Plugin"),
    ("editor_wants_keyboard_focus", "Editor Requires Keyboard Focus"),
)

_MIDI_COUNT_CHOICES = [str(value) for value in range(1, 17)]

HINT_MAX_WIDTH = 268

_PRESET_HINT_BODIES = {
    "instrument": "you can enable MIDI Output for controller-style instruments.",
    "audio-effect": "you can enable MIDI Input or Output for MIDI-driven effects.",
    "midi-effect": "characteristics are fixed by the preset.",
}


class PluginCharacteristicsWidget(QWidget):
    """Preset-constrained plugin flags and related options."""

    changed = Signal()
    validityChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self._checks: dict[str, QCheckBox] = {}
        self._loading = False
        self._preset_type = "instrument"
        self._checkbox_column = self._build_checkbox_column()
        self._audio_io = ComboField("Audio I/O", audio_io_combo_options("instrument"), "stereo")
        self._midi_ins = ComboField("VST MIDI Inputs", _MIDI_COUNT_CHOICES, "16")
        self._midi_outs = ComboField("VST MIDI Outputs", _MIDI_COUNT_CHOICES, "16")
        self._description = QLineEdit()
        self._hint_title = QLabel("Info")
        self._hint_title.setObjectName("PluginTypeHintTitle")
        self._hint = QLabel()
        self._hint.setObjectName("FieldHint")
        self._hint.setWordWrap(True)
        self._build_options_ui()
        self._connect_signals()

    def checkbox_column(self) -> QWidget:
        return self._checkbox_column

    def hint_column(self) -> QWidget:
        column = QWidget()
        column.setMaximumWidth(HINT_MAX_WIDTH)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        panel = QFrame()
        panel.setObjectName("PluginTypeHintPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 10, 12, 10)
        panel_layout.setSpacing(6)
        panel_layout.addWidget(self._hint_title)
        panel_layout.addWidget(self._hint)
        layout.addWidget(panel, 0, Qt.AlignmentFlag.AlignTop)
        layout.addStretch(1)
        return column

    def values(self) -> dict:
        return {
            "needsMidiInput": self._checked("needs_midi_input"),
            "needsMidiOutput": self._checked("needs_midi_output"),
            "isSynth": self._checked("is_synth"),
            "isMidiEffect": self._checked("is_midi_effect"),
            "editorWantsKeyboardFocus": self._checked("editor_wants_keyboard_focus"),
            "pluginDescription": self._description.text(),
            "audioIoPreset": self._audio_io.value(),
            "vstNumMidiIns": int(self._midi_ins.value()),
            "vstNumMidiOuts": int(self._midi_outs.value()),
        }

    def load(self, data: dict, *, type_key: str) -> None:
        self._loading = True
        try:
            self._preset_type = type_key
            defaults = preset_characteristics(type_key)
            for key, _label in _CHARACTERISTIC_LABELS:
                box = self._checks[key]
                json_key = _json_key(key)
                if json_key in data:
                    box.setChecked(bool(data[json_key]))
                elif key in defaults:
                    box.setChecked(defaults[key])
                else:
                    box.setChecked(False)
            self._description.setText(str(data.get("pluginDescription", "")))
            audio_io = normalize_audio_io_preset(str(data.get("audioIoPreset", "stereo")))
            self._midi_ins.set_value(str(data.get("vstNumMidiIns", 16)))
            self._midi_outs.set_value(str(data.get("vstNumMidiOuts", 16)))
            self._apply_preset_constraints(type_key)
            self._audio_io.set_value(audio_io)
            self._sync_midi_count_state()
            self._sync_midi_effect_audio_io()
            self._update_hint()
            self._update_validity()
        finally:
            self._loading = False

    def is_valid(self) -> bool:
        ok, _ = characteristics_conflict(
            self._checked("is_synth"),
            self._checked("is_midi_effect"),
        )
        return ok

    def apply_preset(self, type_key: str) -> None:
        self._loading = True
        try:
            self._preset_type = type_key
            defaults = preset_characteristics(type_key)
            for key, value in defaults.items():
                self._checks[key].setChecked(value)
            self._checks["editor_wants_keyboard_focus"].setChecked(False)
            self._description.clear()
            self._midi_ins.set_value("16")
            self._midi_outs.set_value("16")
            self._apply_preset_constraints(type_key)
            self._audio_io.set_value(preset_audio_io(type_key))
            self._sync_midi_count_state()
            self._update_hint()
            self._update_validity()
        finally:
            self._loading = False

    def _checked(self, key: str) -> bool:
        return self._checks[key].isChecked()

    def _build_checkbox_column(self) -> QWidget:
        column = QWidget()
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for key, label in _CHARACTERISTIC_LABELS:
            layout.addWidget(self._make_checkbox(key, label))
        self._conflict_error = QLabel()
        self._conflict_error.setObjectName("FieldHint")
        self._conflict_error.setWordWrap(True)
        self._conflict_error.hide()
        layout.addWidget(self._conflict_error)
        layout.addStretch(1)
        return column

    def _build_options_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._audio_io)
        layout.addWidget(self._midi_ins)
        layout.addWidget(self._midi_outs)
        layout.addWidget(self._description_row())

    def _make_checkbox(self, key: str, label: str) -> QCheckBox:
        box = QCheckBox(label)
        self._checks[key] = box
        return box

    def _description_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)
        layout.addWidget(make_field_label("Plugin Description"))
        layout.addWidget(self._description, 1)
        layout.addSpacing(24)
        return row

    def _connect_signals(self) -> None:
        for box in self._checks.values():
            box.toggled.connect(self._on_characteristic_toggled)
        self._description.textChanged.connect(self._on_changed)
        self._audio_io.valueChanged.connect(self._on_changed)
        self._midi_ins.valueChanged.connect(self._on_changed)
        self._midi_outs.valueChanged.connect(self._on_changed)

    def _on_characteristic_toggled(self, _checked: bool) -> None:
        if self._loading:
            return
        self._sync_midi_count_state()
        self._sync_midi_effect_audio_io()
        self._on_changed()

    def _on_changed(self, *_args) -> None:
        if self._loading:
            return
        self.changed.emit()
        self._update_validity()

    def _update_validity(self) -> None:
        ok, message = characteristics_conflict(
            self._checked("is_synth"),
            self._checked("is_midi_effect"),
        )
        if ok:
            self._conflict_error.hide()
            self._conflict_error.setText("")
            self._conflict_error.setObjectName("FieldHint")
        else:
            self._conflict_error.setText(message)
            self._conflict_error.setObjectName("FieldError")
            self._conflict_error.show()
        repolish(self._conflict_error)
        self.validityChanged.emit(ok)

    def _apply_preset_constraints(self, type_key: str) -> None:
        rules = preset_checkbox_rules(type_key)
        for key, rule in rules.items():
            box = self._checks[key]
            if rule == LOCKED_ON:
                box.setChecked(True)
                box.setEnabled(False)
            elif rule == LOCKED_OFF:
                box.setChecked(False)
                box.setEnabled(False)
            else:
                box.setEnabled(True)
        midi_effect_preset = type_key == TYPE_MIDI_EFFECT
        self._audio_io.set_choices(
            audio_io_combo_options(type_key),
            preset_audio_io(type_key),
        )
        self._audio_io.setEnabled(not midi_effect_preset)

    def _sync_midi_count_state(self) -> None:
        self._midi_ins.setEnabled(self._checked("needs_midi_input"))
        self._midi_outs.setEnabled(self._checked("needs_midi_output"))

    def _sync_midi_effect_audio_io(self) -> None:
        if self._checked("is_midi_effect"):
            self._audio_io.set_value("midi-effect")
            self._audio_io.setEnabled(False)
        elif self._preset_type != TYPE_MIDI_EFFECT:
            self._audio_io.setEnabled(True)
            if normalize_audio_io_preset(self._audio_io.value()) == "midi-effect":
                self._audio_io.set_value("stereo")

    def _update_hint(self) -> None:
        self._hint.setText(_format_preset_hint(self._preset_type))


def _format_preset_hint(type_key: str) -> str:
    labels = {key: label for key, label in PLUGIN_TYPES}
    display = labels.get(type_key, type_key)
    body = _PRESET_HINT_BODIES.get(type_key, "")
    if not body:
        return ""
    return f"For {display} type plugin, {body}"


def _json_key(python_key: str) -> str:
    mapping = {
        "is_synth": "isSynth",
        "needs_midi_input": "needsMidiInput",
        "needs_midi_output": "needsMidiOutput",
        "is_midi_effect": "isMidiEffect",
        "editor_wants_keyboard_focus": "editorWantsKeyboardFocus",
    }
    return mapping[python_key]
