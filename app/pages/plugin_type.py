"""Plugin Type page: exclusive choice driving the ProjectData plugin flags."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
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
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        radio = QRadioButton(label)
        radio.setProperty("typeKey", key)
        radio.setChecked(key == _DEFAULT_TYPE)
        self._group.addButton(radio)
        desc = QLabel(f"— {_DESCRIPTIONS[key]}")
        desc.setObjectName("FieldHint")
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(radio)
        layout.addWidget(desc, 1)
        return row
