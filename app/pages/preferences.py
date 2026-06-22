"""Preferences page: edit and persist the global default values."""

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.pages.artefacts import ArtefactsSection
from app.widgets.save_bar import SaveBar
from app.widgets.section import Section
from app.widgets.validated_field import FieldSpec
from app.widgets.validated_form import ValidatedForm
from core import validation
from core.preferences import Preferences


def _pref_specs(prefs: Preferences) -> list[FieldSpec]:
    return [
        FieldSpec("manufacturer", "Manufacturer",
                  validation.validate_manufacturer_name,
                  default=prefs.get("manufacturer")),
        FieldSpec("manufacturerCode", "Manufacturer code",
                  validation.validate_manufacturer_code,
                  default=prefs.get("manufacturerCode")),
        FieldSpec("pluginCode", "Plugin code",
                  validation.validate_plugin_code,
                  default=prefs.get("pluginCode")),
        FieldSpec("companyCopyright", "Copyright",
                  validation.validate_optional,
                  default=prefs.get("companyCopyright")),
        FieldSpec("companyWebsite", "Website",
                  validation.validate_optional,
                  default=prefs.get("companyWebsite")),
        FieldSpec("companyEmail", "E-mail",
                  validation.validate_optional,
                  default=prefs.get("companyEmail")),
        FieldSpec("destination", "Default destination",
                  validation.validate_destination,
                  default=prefs.get("destination")),
        FieldSpec("juceDir", "JUCE directory",
                  validation.validate_optional_path,
                  default=prefs.get("juceDir")),
    ]


class PreferencesPage(QWidget):
    """Edits the persisted defaults (identity + default artefact settings)."""

    def __init__(self, prefs: Preferences):
        super().__init__()
        self._prefs = prefs
        self._form = ValidatedForm(_pref_specs(prefs))
        self._artefacts = ArtefactsSection(prefs)
        self._bar = SaveBar("Save Preferences")
        self._bar.saveRequested.connect(self._on_save)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        title = QLabel("Preferences")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        layout.addWidget(self._intro())
        layout.addWidget(self._form)
        layout.addWidget(Section("Default artefacts", self._artefacts))
        layout.addWidget(self._bar)
        layout.addStretch(1)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _intro(self) -> QLabel:
        label = QLabel(
            "These are reusable defaults: they pre-fill the matching fields when you "
            "create a new project, so you don't retype them each time. They are saved "
            "on this machine only and are never imposed on the projects you generate."
        )
        label.setObjectName("FieldHint")
        label.setWordWrap(True)
        return label

    def _on_save(self) -> None:
        if not (self._form.is_valid() and self._artefacts.is_valid()):
            self._bar.set_status("Fix the invalid fields before saving.", ok=False)
            return
        self._prefs.update(self._form.values())
        self._prefs.update(self._artefacts.values())
        self._prefs.save()
        self._bar.set_status("Preferences saved.", ok=True)
