"""Preferences page: edit and persist the global default values."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.widgets.save_bar import SaveBar
from app.widgets.validated_field import FieldSpec
from app.widgets.validated_form import ValidatedForm
from core import validation
from core.preferences import Preferences


def _pref_specs(prefs: Preferences) -> list[FieldSpec]:
    return [
        FieldSpec("generatorRoot", "Generator path",
                  validation.validate_optional_path,
                  default=prefs.get("generatorRoot"),
                  placeholder="empty in packaged builds; set when running from source"),
        FieldSpec("manufacturer", "Manufacturer",
                  validation.validate_manufacturer_name,
                  default=prefs.get("manufacturer")),
        FieldSpec("manufacturerCode", "Manufacturer code",
                  validation.validate_manufacturer_code,
                  default=prefs.get("manufacturerCode")),
        FieldSpec("pluginCode", "Plugin code",
                  validation.validate_plugin_code,
                  default=prefs.get("pluginCode")),
        FieldSpec("destination", "Default destination",
                  validation.validate_destination,
                  default=prefs.get("destination")),
        FieldSpec("juceDir", "JUCE directory",
                  validation.validate_optional_path,
                  default=prefs.get("juceDir")),
    ]


class PreferencesPage(QWidget):
    """Edits the persisted defaults and writes them to the JSON file."""

    def __init__(self, prefs: Preferences):
        super().__init__()
        self._prefs = prefs
        self._form = ValidatedForm(_pref_specs(prefs))
        self._bar = SaveBar("Save preferences")
        self._bar.saveRequested.connect(self._on_save)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(2)
        title = QLabel("Preferences")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        layout.addWidget(self._form)
        hint = QLabel("The generator path applies after restarting Luthier.")
        hint.setObjectName("FieldHint")
        layout.addWidget(hint)
        layout.addWidget(self._bar)
        layout.addStretch(1)

    def _on_save(self) -> None:
        if not self._form.is_valid():
            self._bar.set_status("Fix the invalid fields before saving.", ok=False)
            return
        self._prefs.update(self._form.values())
        self._prefs.save()
        self._bar.set_status("Preferences saved.", ok=True)
