"""Plugin Type page: exclusive choice driving the ProjectData plugin flags."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from core.plugin_settings import PLUGIN_TYPES

_DESCRIPTIONS = {
    "synth": "Instrument. Receives MIDI, produces audio.",
    "effect": "Processes incoming audio.",
    "midi": "Processes MIDI. No audio input or output.",
}
_DEFAULT_TYPE = PLUGIN_TYPES[0][0]


class PluginTypePage(QWidget):
    """Single mutually exclusive plugin type selection."""

    changed = Signal()

    def __init__(self):
        super().__init__()
        self._group = QButtonGroup(self)
        self._group.buttonClicked.connect(lambda _btn: self.changed.emit())
        self._build_ui()

    def selected_type(self) -> str:
        checked = self._group.checkedButton()
        return checked.property("typeKey") if checked else _DEFAULT_TYPE

    def set_type(self, type_key: str) -> None:
        for button in self._group.buttons():
            if button.property("typeKey") == type_key:
                button.setChecked(True)
                return

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for key, label in PLUGIN_TYPES:
            layout.addWidget(self._make_option(key, label))

    def _make_option(self, key: str, label: str) -> QWidget:
        container = QWidget()
        box = QVBoxLayout(container)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(2)
        box.addWidget(self._make_radio(key, label))
        box.addWidget(self._make_description(key))
        return container

    def _make_radio(self, key: str, label: str) -> QRadioButton:
        radio = QRadioButton(label)
        radio.setProperty("typeKey", key)
        radio.setChecked(key == _DEFAULT_TYPE)
        self._group.addButton(radio)
        return radio

    def _make_description(self, key: str) -> QLabel:
        desc = QLabel(_DESCRIPTIONS[key])
        desc.setObjectName("FieldHint")
        desc.setContentsMargins(22, 0, 0, 6)
        return desc
