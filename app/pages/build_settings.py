"""Build Settings page: artefact copy flags and central artefact directories."""

from PySide6.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget

from app.widgets.save_bar import SaveBar
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
        FieldSpec("artefactsDirWindows", "Artefacts (Windows)",
                  validation.validate_optional_path,
                  default=prefs.get("artefactsDirWindows")),
        FieldSpec("artefactsDirMacos", "Artefacts (macOS)",
                  validation.validate_optional_path,
                  default=prefs.get("artefactsDirMacos")),
        FieldSpec("artefactsDirLinux", "Artefacts (Linux)",
                  validation.validate_optional_path,
                  default=prefs.get("artefactsDirLinux")),
    ]


class BuildSettingsPage(QWidget):
    """Edits the persisted artefact copy flags and directories."""

    def __init__(self, prefs: Preferences):
        super().__init__()
        self._prefs = prefs
        self._form = ValidatedForm(_artefact_specs(prefs))
        self._checks: dict[str, QCheckBox] = {}
        self._bar = SaveBar("Save build settings")
        self._bar.saveRequested.connect(self._on_save)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)
        title = QLabel("Build Settings")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        for key, label in _COPY_FLAGS:
            layout.addWidget(self._make_check(key, label))
        layout.addWidget(self._form)
        layout.addWidget(self._bar)
        layout.addStretch(1)

    def load(self, values: dict) -> None:
        for key, box in self._checks.items():
            if key in values:
                box.setChecked(bool(values[key]))
        self._form.set_values(values)

    def _make_check(self, key: str, label: str) -> QCheckBox:
        box = QCheckBox(label)
        box.setChecked(bool(self._prefs.get(key)))
        self._checks[key] = box
        return box

    def _on_save(self) -> None:
        if not self._form.is_valid():
            self._bar.set_status("Fix the invalid fields before saving.", ok=False)
            return
        self._prefs.update(self._form.values())
        self._prefs.update({k: b.isChecked() for k, b in self._checks.items()})
        self._prefs.save()
        self._bar.set_status("Build settings saved.", ok=True)
