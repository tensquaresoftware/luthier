"""Project Info page: technical/display names, version, manufacturer, codes."""

from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.pages.path_specs import destination_field_spec, juce_field_spec
from app.widgets.elided_line_edit import ElidedLineEdit
from app.widgets.folder_field import FolderField
from app.widgets.validated_field import FieldSpec, make_field_label
from app.widgets.validated_form import ValidatedForm
from core import validation


def _field_specs(defaults: dict) -> list[FieldSpec]:
    manufacturer = defaults.get("manufacturerName", defaults.get("manufacturer", ""))
    return [
        FieldSpec("projectName", "Project name *",
                  validation.validate_project_name, placeholder="NewPlugin"),
        FieldSpec("projectDisplayName", "Display name",
                  validation.validate_display_name, placeholder="optional"),
        FieldSpec("projectVersion", "Version *",
                  validation.validate_version, default="1.0.0"),
        FieldSpec("manufacturerName", "Manufacturer *",
                  validation.validate_manufacturer_name,
                  default=manufacturer),
        FieldSpec("companyCopyright", "Copyright",
                  validation.validate_optional, placeholder="optional",
                  default=defaults.get("companyCopyright", "")),
        FieldSpec("companyWebsite", "Website",
                  validation.validate_optional, placeholder="optional",
                  default=defaults.get("companyWebsite", "")),
        FieldSpec("companyEmail", "E-mail",
                  validation.validate_optional, placeholder="optional",
                  default=defaults.get("companyEmail", "")),
        FieldSpec("manufacturerCode", "Manufacturer code *",
                  validation.validate_manufacturer_code,
                  default=defaults.get("manufacturerCode", "")),
        FieldSpec("pluginCode", "Plugin code *",
                  validation.validate_plugin_code,
                  default=defaults.get("pluginCode", "")),
    ]


def _default_path(defaults: dict, primary: str, legacy: str = "") -> str:
    value = defaults.get(primary, "")
    if not value and legacy:
        value = defaults.get(legacy, "")
    return value or ""


class ProjectInfoPage(QWidget):
    """Form for the core ProjectData fields with live validation."""

    validityChanged = Signal(bool)

    def __init__(
        self,
        defaults: dict,
        bundle_id_fn: Callable[[str, str], str],
        folder_start_resolver: Callable[[str], str] | None = None,
    ):
        super().__init__()
        self._bundle_id_fn = bundle_id_fn
        self._form = ValidatedForm(_field_specs(defaults))
        self._destination = FolderField(
            destination_field_spec(_default_path(defaults, "destinationDir", "destination")),
            "Choose destination folder",
            start_dir_resolver=folder_start_resolver,
        )
        self._juce_dir = FolderField(
            juce_field_spec(_default_path(defaults, "juceDir")),
            "Choose JUCE directory",
            start_dir_resolver=folder_start_resolver,
        )
        self._build_ui()
        self._connect_signals()
        self._update_bundle_id()

    def values(self) -> dict:
        result = self._form.values()
        if not result["projectDisplayName"].strip():
            result["projectDisplayName"] = result["projectName"]
        result["destinationDir"] = self._destination.value()
        result["juceDir"] = self._juce_dir.value()
        return result

    def is_valid(self) -> bool:
        return (
            self._form.is_valid()
            and self._destination.is_valid()
            and self._juce_dir.is_valid()
        )

    def load(self, values: dict) -> None:
        self._form.set_values(values)
        self._destination.set_value(_default_path(values, "destinationDir", "destination"))
        self._juce_dir.set_value(values.get("juceDir") or "")
        self._update_bundle_id()

    def set_destination(self, value: str) -> None:
        self._destination.set_value(value)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self._form)
        layout.addWidget(self._build_bundle_row())
        layout.addWidget(self._destination)
        layout.addWidget(self._juce_dir)

    def _build_bundle_row(self) -> QWidget:
        widget = QWidget()
        outer = QVBoxLayout(widget)
        outer.setContentsMargins(0, 4, 0, 4)
        outer.setSpacing(0)
        row = QHBoxLayout()
        row.setSpacing(8)
        self._bundle = ElidedLineEdit()
        self._bundle.setReadOnly(True)
        mark = QLabel("")
        mark.setObjectName("FieldMark")
        mark.setFixedWidth(16)
        row.addWidget(make_field_label("Bundle ID"))
        row.addWidget(self._bundle, 1)
        row.addWidget(mark)
        outer.addLayout(row)
        return widget

    def _connect_signals(self) -> None:
        self._form.validityChanged.connect(self._emit_validity)
        self._destination.validityChanged.connect(self._emit_validity)
        self._juce_dir.validityChanged.connect(self._emit_validity)
        self._form.field("projectName").valueChanged.connect(self._update_bundle_id)
        self._form.field("manufacturerName").valueChanged.connect(self._update_bundle_id)

    def _emit_validity(self, _ok: bool = False) -> None:
        self.validityChanged.emit(self.is_valid())

    def _update_bundle_id(self, _text: str = "") -> None:
        manufacturer = self._form.field("manufacturerName").value()
        project = self._form.field("projectName").value()
        self._bundle.setText(self._bundle_id_fn(manufacturer, project))
