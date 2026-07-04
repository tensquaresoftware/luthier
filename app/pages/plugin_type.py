"""Plugin Type page: preset choice and independent characteristic toggles."""

from collections.abc import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from app.confirm import confirm_discard_unsaved
from app.pages.plugin_characteristics import PluginCharacteristicsWidget
from core.plugin_settings import PLUGIN_TYPES

_DESCRIPTIONS = {
    "instrument": "Receives MIDI, produces audio.",
    "audio-effect": "Processes incoming audio.",
    "midi-effect": "Processes MIDI. No audio input or output.",
}
_DEFAULT_TYPE = PLUGIN_TYPES[0][0]
_PRESETS_MIN_WIDTH = 248
_PRESET_CONFIRM_MESSAGE = (
    "Changing the plugin type preset will reset characteristic toggles. "
    "Discard your unsaved changes and apply the new preset?"
)


class PluginTypePage(QWidget):
    """Plugin type preset with decoupled characteristic configuration."""

    changed = Signal()
    validityChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self._group = QButtonGroup(self)
        self._loading = False
        self._active_type = _DEFAULT_TYPE
        self._dirty_callback: Callable[[], bool] | None = None
        self._characteristics = PluginCharacteristicsWidget()
        self._group.idClicked.connect(self._on_preset_clicked)
        self._build_ui()
        self._characteristics.apply_preset(_DEFAULT_TYPE)
        self._connect_characteristics()

    def selected_type(self) -> str:
        checked = self._group.checkedButton()
        return checked.property("typeKey") if checked else _DEFAULT_TYPE

    def characteristics_values(self) -> dict:
        return self._characteristics.values()

    def is_valid(self) -> bool:
        return self._characteristics.is_valid()

    def set_dirty_callback(self, callback: Callable[[], bool] | None) -> None:
        self._dirty_callback = callback

    def load(self, data: dict) -> None:
        self._loading = True
        self._group.blockSignals(True)
        try:
            type_key = str(data.get("pluginType", _DEFAULT_TYPE))
            if not self.set_type(type_key):
                type_key = _DEFAULT_TYPE
                self.set_type(type_key)
            self._active_type = self.selected_type()
            self._characteristics.load(data, type_key=self.selected_type())
        finally:
            self._group.blockSignals(False)
            self._loading = False

    def set_type(self, type_key: str) -> bool:
        for button in self._group.buttons():
            if button.property("typeKey") == type_key:
                button.setChecked(True)
                return True
        return False

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        columns = QHBoxLayout()
        columns.setSpacing(16)
        columns.addWidget(self._presets_column(), 4)
        columns.addWidget(self._characteristics.checkbox_column(), 4)
        columns.addWidget(self._characteristics.hint_column(), 0)
        layout.addLayout(columns)
        layout.addWidget(self._columns_divider())
        layout.addSpacing(8)
        layout.addWidget(self._characteristics)

    def _columns_divider(self) -> QFrame:
        line = QFrame()
        line.setObjectName("SectionDivider")
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        return line

    def _presets_column(self) -> QWidget:
        column = QWidget()
        column.setMinimumWidth(_PRESETS_MIN_WIDTH)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        for key, label in PLUGIN_TYPES:
            layout.addWidget(self._make_preset_block(key, label))
        layout.addStretch(1)
        return column

    def _make_preset_block(self, key: str, label: str) -> QWidget:
        block = QWidget()
        block_layout = QVBoxLayout(block)
        block_layout.setContentsMargins(0, 0, 0, 0)
        block_layout.setSpacing(2)
        radio = QRadioButton(label)
        radio.setProperty("typeKey", key)
        radio.setChecked(key == _DEFAULT_TYPE)
        self._group.addButton(radio)
        desc = QLabel(_DESCRIPTIONS[key])
        desc.setObjectName("FieldHint")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        block_layout.addWidget(radio)
        block_layout.addWidget(desc)
        return block

    def _connect_characteristics(self) -> None:
        self._characteristics.changed.connect(self.changed.emit)
        self._characteristics.validityChanged.connect(self._emit_validity)

    def _on_preset_clicked(self, _button_id: int) -> None:
        if self._loading:
            return
        new_type = self.selected_type()
        if new_type == self._active_type:
            return
        if self._dirty_callback and self._dirty_callback():
            if not confirm_discard_unsaved(
                self,
                "Plugin Type",
                _PRESET_CONFIRM_MESSAGE,
            ):
                self._revert_preset(self._active_type)
                return
        self._active_type = new_type
        self._characteristics.apply_preset(new_type)
        self.changed.emit()

    def _revert_preset(self, type_key: str) -> None:
        self._group.blockSignals(True)
        self.set_type(type_key)
        self._group.blockSignals(False)

    def _emit_validity(self, _ok: bool = False) -> None:
        self.validityChanged.emit(self.is_valid())
