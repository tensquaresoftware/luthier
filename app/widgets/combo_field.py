"""Label + drop-down field, aligned with the ValidatedField row layout."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QListView, QWidget

from app.widgets.saved_badge import BadgedInputHost
from app.widgets.validated_field import make_field_label


def _make_combo_view() -> QListView:
    view = QListView()
    view.setFrameShape(QListView.Shape.NoFrame)
    return view


class ComboField(QWidget):
    """A labelled drop-down with plain or display/value choices."""

    valueChanged = Signal()

    def __init__(self, label: str, choices, default: str):
        super().__init__()
        combo = QComboBox()
        combo.setView(_make_combo_view())
        self._combo_host = BadgedInputHost(combo)
        self._combo = combo
        self._combo.currentIndexChanged.connect(self._on_index_changed)
        self.set_choices(choices, default)
        self._build_ui(label)

    def value(self) -> str:
        data = self._combo.currentData()
        if data is not None:
            return str(data)
        text = self._combo.currentText()
        return text if text else str(self._combo.itemData(0) or "")

    def set_value(self, value: str) -> None:
        for index in range(self._combo.count()):
            if self._combo.itemData(index) == value:
                self._combo.setCurrentIndex(index)
                return
        index = self._combo.findText(value)
        if index >= 0:
            self._combo.setCurrentIndex(index)

    def set_choices(self, choices, default: str) -> None:
        self._combo.blockSignals(True)
        self._combo.clear()
        if choices:
            if isinstance(choices[0], tuple):
                for display, stored in choices:
                    self._combo.addItem(display, stored)
            else:
                self._combo.addItems(choices)
        else:
            self._combo.addItem(default, default)
        self.set_value(default)
        self._combo.blockSignals(False)

    def flash_saved(self) -> None:
        self._combo_host.flash_saved()

    def is_saved_sender(self, sender) -> bool:
        return sender in (self, self._combo)

    def _on_index_changed(self, _index: int) -> None:
        if not self._combo.signalsBlocked():
            self.valueChanged.emit()

    def _build_ui(self, label: str) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(8)
        row.addWidget(make_field_label(label))
        row.addWidget(self._combo_host, 1)
        row.addSpacing(24)
