"""Artefacts section: where built plugins are copied after each build.

Live per-project fields, seeded from preferences. The three directory fields
are disabled while "Copy to central artefacts folder" is off.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget

from app.widgets.validated_field import FieldSpec
from app.widgets.validated_form import ValidatedForm
from core import validation
from core.preferences import Preferences

_COPY_FLAGS = [
    ("copyToSystemFolders", "Copy to system plugin folders"),
    ("copyToArtefactsDir", "Copy to central artefacts folder"),
]


def _artefact_specs(prefs: Preferences) -> list[FieldSpec]:
    return [
        FieldSpec("artefactsDirWindows", "Windows",
                  validation.validate_optional_path, default=prefs.get("artefactsDirWindows")),
        FieldSpec("artefactsDirMacos", "macOS",
                  validation.validate_optional_path, default=prefs.get("artefactsDirMacos")),
        FieldSpec("artefactsDirLinux", "Linux",
                  validation.validate_optional_path, default=prefs.get("artefactsDirLinux")),
    ]


class ArtefactsSection(QWidget):
    """Copy flags + per-OS artefact directories, seeded from preferences."""

    validityChanged = Signal(bool)

    def __init__(self, prefs: Preferences):
        super().__init__()
        self._prefs = prefs
        self._form = ValidatedForm(_artefact_specs(prefs))
        self._checks: dict[str, QCheckBox] = {}
        self._build_ui()
        self._form.validityChanged.connect(self.validityChanged)
        self._sync_paths_enabled()

    def values(self) -> dict:
        values = self._form.values()
        values.update({key: box.isChecked() for key, box in self._checks.items()})
        return values

    def is_valid(self) -> bool:
        if not self._checks["copyToArtefactsDir"].isChecked():
            return True
        return self._form.is_valid()

    def load(self, values: dict) -> None:
        for key, box in self._checks.items():
            if key in values:
                box.setChecked(bool(values[key]))
        self._form.set_values(values)

    def flash_saved(self, sender) -> None:
        for field in self._form._fields.values():
            if field.is_saved_sender(sender):
                field.flash_saved()
                return
        if sender in self._checks.values() and self._checks["copyToArtefactsDir"].isChecked():
            next(iter(self._form._fields.values())).flash_saved()

    def is_saved_sender(self, sender) -> bool:
        if sender in self._checks.values():
            return True
        return any(field.is_saved_sender(sender) for field in self._form._fields.values())

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        for key, label in _COPY_FLAGS:
            layout.addWidget(self._make_check(key, label))
        layout.addWidget(self._form)

    def _make_check(self, key: str, label: str) -> QCheckBox:
        box = QCheckBox(label)
        box.setChecked(bool(self._prefs.get(key)))
        self._checks[key] = box
        if key == "copyToArtefactsDir":
            box.toggled.connect(self._sync_paths_enabled)
        return box

    def _sync_paths_enabled(self, _checked: bool = False) -> None:
        self._form.setEnabled(self._checks["copyToArtefactsDir"].isChecked())
