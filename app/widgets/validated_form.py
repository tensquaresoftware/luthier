"""A vertical stack of ValidatedField rows with aggregate validity."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.widgets.validated_field import FieldSpec, ValidatedField
from core.display import display_str


class ValidatedForm(QWidget):
    """Builds fields from specs and reports combined validity."""

    validityChanged = Signal(bool)

    def __init__(self, specs: list[FieldSpec]):
        super().__init__()
        self._fields: dict[str, ValidatedField] = {}
        self._build(specs)

    def field(self, key: str) -> ValidatedField:
        return self._fields[key]

    def values(self) -> dict:
        return {key: field.value() for key, field in self._fields.items()}

    def set_values(self, values: dict) -> None:
        for key, field in self._fields.items():
            if key in values:
                field.set_value(display_str(values[key]))

    def is_valid(self) -> bool:
        return all(field.is_valid() for field in self._fields.values())

    def _build(self, specs: list[FieldSpec]) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        for spec in specs:
            field = ValidatedField(spec)
            field.validityChanged.connect(self._emit)
            self._fields[spec.key] = field
            layout.addWidget(field)

    def _emit(self, _ok: bool = False) -> None:
        self.validityChanged.emit(self.is_valid())
