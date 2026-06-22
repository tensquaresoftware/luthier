"""Label + drop-down field, aligned with the ValidatedField row layout."""

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QListView, QWidget

from app.widgets.validated_field import make_field_label


def _make_combo_view() -> QListView:
    view = QListView()
    view.setFrameShape(QListView.Shape.NoFrame)
    return view


class ComboField(QWidget):
    """A labelled drop-down with a fixed set of string choices."""

    def __init__(self, label: str, choices: list[str], default: str):
        super().__init__()
        self._combo = QComboBox()
        self._combo.setView(_make_combo_view())
        self._combo.addItems(choices)
        self.set_value(default)
        self._build_ui(label)

    def value(self) -> str:
        return self._combo.currentText()

    def set_value(self, value: str) -> None:
        index = self._combo.findText(value)
        if index >= 0:
            self._combo.setCurrentIndex(index)

    def _build_ui(self, label: str) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(8)
        row.addWidget(make_field_label(label))
        row.addWidget(self._combo, 1)
        row.addSpacing(24)
