"""Artefacts section: where built plugins are copied after each build.

Live per-project fields, seeded from preferences. The three directory fields
are disabled while "Copy to central artefacts folder" is off. A native Choose…
button is shown only for the artefact path matching the host OS.
"""

from collections.abc import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget

from app.pages.path_specs import host_artefact_field_key
from app.widgets.folder_field import FolderField
from app.widgets.os_path_tree_group import OsPathTreeGroup
from app.widgets.validated_field import FieldSpec, ValidatedField
from core import validation
from core.display import display_str
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

    def __init__(
        self,
        prefs: Preferences,
        folder_start_resolver: Callable[[str], str] | None = None,
    ):
        super().__init__()
        self._prefs = prefs
        self._path_fields: dict[str, ValidatedField | FolderField] = {}
        self._checks: dict[str, QCheckBox] = {}
        self._paths_tree: OsPathTreeGroup | None = None
        self._build_ui(folder_start_resolver)
        self._sync_paths_enabled()

    def path_fields(self) -> dict[str, ValidatedField | FolderField]:
        return dict(self._path_fields)

    def values(self) -> dict:
        values = {key: field.value() for key, field in self._path_fields.items()}
        values.update({key: box.isChecked() for key, box in self._checks.items()})
        return values

    def is_valid(self) -> bool:
        if not self._checks["copyToArtefactsDir"].isChecked():
            return True
        return all(field.is_valid() for field in self._path_fields.values())

    def load(self, values: dict) -> None:
        for key, box in self._checks.items():
            if key in values:
                box.setChecked(bool(values[key]))
        for key, field in self._path_fields.items():
            if key in values:
                field.set_value(display_str(values[key]))

    def flash_saved(self, sender) -> None:
        for field in self._path_fields.values():
            if field.is_saved_sender(sender):
                field.flash_saved()
                return
        if sender in self._checks.values() and self._checks["copyToArtefactsDir"].isChecked():
            next(iter(self._path_fields.values())).flash_saved()

    def is_saved_sender(self, sender) -> bool:
        if sender in self._checks.values():
            return True
        return any(field.is_saved_sender(sender) for field in self._path_fields.values())

    def _build_ui(self, folder_start_resolver: Callable[[str], str] | None) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._make_check("copyToSystemFolders", _COPY_FLAGS[0][1]))
        layout.addWidget(self._build_paths_tree(folder_start_resolver))

    def _build_paths_tree(self, folder_start_resolver: Callable[[str], str] | None) -> OsPathTreeGroup:
        anchor = self._make_check("copyToArtefactsDir", _COPY_FLAGS[1][1])
        host_key = host_artefact_field_key()
        fields = []
        for spec in _artefact_specs(self._prefs):
            if spec.key == host_key:
                field = FolderField(
                    spec,
                    f"Choose {spec.label} artefacts folder",
                    start_dir_resolver=folder_start_resolver,
                )
            else:
                field = ValidatedField(spec)
            field.validityChanged.connect(self.validityChanged)
            self._path_fields[spec.key] = field
            fields.append(field)
        self._paths_tree = OsPathTreeGroup(anchor, fields)
        return self._paths_tree

    def _make_check(self, key: str, label: str) -> QCheckBox:
        box = QCheckBox(label)
        box.setChecked(bool(self._prefs.get(key)))
        self._checks[key] = box
        if key == "copyToArtefactsDir":
            box.toggled.connect(self._sync_paths_enabled)
        return box

    def _sync_paths_enabled(self, _checked: bool = False) -> None:
        enabled = self._checks["copyToArtefactsDir"].isChecked()
        for field in self._path_fields.values():
            field.setEnabled(enabled)
        if self._paths_tree is not None:
            self._paths_tree.update()
