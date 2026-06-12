"""Project Info page: technical/display names, version, manufacturer, codes."""

from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.widgets.validated_field import FieldSpec, make_field_label
from app.widgets.validated_form import ValidatedForm
from core import validation


def _field_specs(defaults: dict) -> list[FieldSpec]:
    return [
        FieldSpec("projectName", "Project name",
                  validation.validate_project_name, placeholder="NewPlugin"),
        FieldSpec("projectDisplayName", "Display name",
                  validation.validate_display_name, placeholder="optional"),
        FieldSpec("projectVersion", "Version",
                  validation.validate_version, default="1.0.0"),
        FieldSpec("manufacturerName", "Manufacturer",
                  validation.validate_manufacturer_name,
                  default=defaults.get("manufacturer", "")),
        FieldSpec("manufacturerCode", "Manufacturer code",
                  validation.validate_manufacturer_code,
                  default=defaults.get("manufacturerCode", "")),
        FieldSpec("pluginCode", "Plugin code",
                  validation.validate_plugin_code,
                  default=defaults.get("pluginCode", "")),
        FieldSpec("destinationDir", "Destination",
                  validation.validate_destination,
                  default=defaults.get("destination", "")),
    ]


class ProjectInfoPage(QWidget):
    """Form for the core ProjectData fields with live validation."""

    validityChanged = Signal(bool)

    def __init__(self, defaults: dict, bundle_id_fn: Callable[[str, str], str]):
        super().__init__()
        self._bundle_id_fn = bundle_id_fn
        self._form = ValidatedForm(_field_specs(defaults))
        self._build_ui()
        self._connect_signals()
        self._update_bundle_id()

    def values(self) -> dict:
        result = self._form.values()
        if not result["projectDisplayName"].strip():
            result["projectDisplayName"] = result["projectName"]
        return result

    def is_valid(self) -> bool:
        return self._form.is_valid()

    def load(self, values: dict) -> None:
        self._form.set_values(values)
        self._update_bundle_id()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(2)
        title = QLabel("Project Info")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        layout.addWidget(self._form)
        layout.addLayout(self._build_bundle_row())
        layout.addStretch(1)

    def _build_bundle_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        self._bundle = QLineEdit()
        self._bundle.setReadOnly(True)
        row.addWidget(make_field_label("Bundle ID"))
        row.addWidget(self._bundle)
        row.addSpacing(24)
        return row

    def _connect_signals(self) -> None:
        self._form.validityChanged.connect(self.validityChanged)
        self._form.field("projectName").valueChanged.connect(self._update_bundle_id)
        self._form.field("manufacturerName").valueChanged.connect(self._update_bundle_id)

    def _update_bundle_id(self, _text: str = "") -> None:
        manufacturer = self._form.field("manufacturerName").value()
        project = self._form.field("projectName").value()
        self._bundle.setText(self._bundle_id_fn(manufacturer, project))
