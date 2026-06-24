"""Preferences page: edit and persist the global default values."""

import json
import sys
from pathlib import Path

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.pages.artefacts import ArtefactsSection
from app.widgets.section import Section
from app.widgets.validated_field import FieldSpec
from app.widgets.validated_form import ValidatedForm
from core import validation
from core.preferences import Preferences


def _juce_dir_placeholder() -> str:
    if sys.platform == "win32":
        return "C:/Program Files/JUCE"
    if sys.platform == "darwin":
        return "/Applications/JUCE"
    return "/usr/local/JUCE"


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
                  default=prefs.get("juceDir"),
                  placeholder=_juce_dir_placeholder()),
    ]


class PreferencesPage(QWidget):
    """Edits the persisted defaults (identity + default artefact settings)."""

    def __init__(self, prefs: Preferences):
        super().__init__()
        self._prefs = prefs
        self._form = ValidatedForm(_pref_specs(prefs))
        self._artefacts = ArtefactsSection(prefs)
        self._build_ui()

    def save(self) -> bool:
        if not (self._form.is_valid() and self._artefacts.is_valid()):
            return False
        self._prefs.apply_form(self._form.values(), self._artefacts.values())
        self._prefs.save()
        return True

    def load_from_file(self, path: str) -> None:
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        self._form.set_values(data)
        self._artefacts.load(data)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._build_content())
        outer.addWidget(scroll)

    def _build_content(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(36)
        layout.addWidget(self._intro())
        layout.addWidget(Section("Default infos", self._form))
        layout.addWidget(Section("Default artefacts", self._artefacts))
        layout.addStretch(1)
        return content

    def _intro(self) -> QLabel:
        label = QLabel(
            "These are reusable defaults: they pre-fill the matching fields when you "
            "create a new project, so you don't retype them each time. They are saved "
            "on this machine only and are never imposed on the projects you generate."
        )
        label.setObjectName("FieldHint")
        label.setWordWrap(True)
        return label

