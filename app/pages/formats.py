"""Formats page: which plugin formats to build (at least one required)."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget

from app.qss import repolish

_FORMATS = ["AU", "VST3", "Standalone"]


class FormatsPage(QWidget):
    """Checkbox set producing the space-joined pluginFormats string."""

    validityChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self._checks: dict[str, QCheckBox] = {}
        self._build_ui()

    def value(self) -> str:
        return " ".join(name for name, box in self._checks.items() if box.isChecked())

    def is_valid(self) -> bool:
        return any(box.isChecked() for box in self._checks.values())

    def set_formats(self, formats: str) -> None:
        wanted = set(formats.split())
        for name, box in self._checks.items():
            box.setChecked(name in wanted)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)
        title = QLabel("Formats")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        for name in _FORMATS:
            layout.addWidget(self._make_checkbox(name))
        self._hint = QLabel("Select at least one format.")
        self._hint.setObjectName("FieldHint")
        layout.addWidget(self._hint)
        layout.addStretch(1)

    def _make_checkbox(self, name: str) -> QCheckBox:
        box = QCheckBox(name)
        box.setChecked(True)
        box.toggled.connect(self._on_toggled)
        self._checks[name] = box
        return box

    def _on_toggled(self, _checked: bool) -> None:
        ok = self.is_valid()
        self._hint.setObjectName("FieldHint" if ok else "FieldError")
        repolish(self._hint)
        self.validityChanged.emit(ok)
