"""Preferences page: edit and persist the global default values."""

import json
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.pages.artefacts import ArtefactsSection
from app.pages.compilation import CompilationSection
from app.pages.formats import FormatsPage
from app.pages.plugin_type import PluginTypePage
from app.pages.workspace import WorkspaceSection
from app.widgets.accent_color_picker import AccentColorSection
from app.widgets.section import Section
from app.widgets.validated_field import FieldSpec
from app.widgets.validated_form import ValidatedForm
from core import validation
from core.preferences import Preferences, validate_profile


def _identity_specs(prefs: Preferences) -> list[FieldSpec]:
    return [
        FieldSpec("manufacturer", "Manufacturer",
                  validation.validate_manufacturer_name,
                  default=prefs.get("manufacturer")),
        FieldSpec("manufacturerCode", "Manufacturer code",
                  validation.validate_manufacturer_code,
                  default=prefs.get("manufacturerCode"),
                  generator=validation.generate_manufacturer_code),
        FieldSpec("pluginCode", "Plugin code",
                  validation.validate_plugin_code,
                  default=prefs.get("pluginCode"),
                  generator=validation.generate_plugin_code),
        FieldSpec("companyCopyright", "Copyright",
                  validation.validate_optional,
                  default=prefs.get("companyCopyright")),
        FieldSpec("companyWebsite", "Website",
                  validation.validate_optional,
                  default=prefs.get("companyWebsite")),
        FieldSpec("companyEmail", "E-mail",
                  validation.validate_optional,
                  default=prefs.get("companyEmail")),
    ]


def _pref_text(prefs: Preferences, key: str) -> str:
    value = prefs.get(key)
    return "" if value is None else str(value)


class PreferencesPage(QWidget):
    """Edits the persisted profile with auto-save and import/export."""

    saved = Signal()

    def __init__(
        self,
        prefs: Preferences,
        folder_start_resolver: Callable[[str], str] | None = None,
    ):
        super().__init__()
        self._prefs = prefs
        self._identity = ValidatedForm(_identity_specs(prefs))
        self._workspace = WorkspaceSection(
            prefs, folder_start_resolver=folder_start_resolver
        )
        self._plugin_type = PluginTypePage()
        self._formats = FormatsPage()
        self._compilation = CompilationSection()
        self._artefacts = ArtefactsSection(
            prefs, folder_start_resolver=folder_start_resolver
        )
        self._accent = AccentColorSection(prefs.accent_color)
        self._reload_guard = False
        self._build_ui()
        self.reload_from_prefs()
        self._connect_auto_save()
        self._accent.colorChanged.connect(self._on_accent_save)

    def accent_section(self) -> AccentColorSection:
        return self._accent

    def reload_from_prefs(self) -> None:
        self._reload_guard = True
        try:
            self._identity.set_values(self._prefs.to_dict())
            self._workspace.load(self._prefs.to_dict())
            self._plugin_type.set_type(_pref_text(self._prefs, "pluginType"))
            self._formats.set_formats(_pref_text(self._prefs, "pluginFormats"))
            self._compilation.load(self._prefs.to_dict())
            self._artefacts.load(self._prefs.to_dict())
            self._accent.set_color(self._prefs.accent_color)
        finally:
            self._reload_guard = False

    def import_from_file(self, path: str) -> tuple[bool, str]:
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            return False, f"Could not read file: {error}"
        if not isinstance(data, dict):
            return False, "Preferences file must contain a JSON object."
        ok, message = validate_profile(data, require_host_destination=False)
        if not ok:
            return False, message
        before_accent = self._prefs.accent_color
        before = self._prefs.to_dict()
        try:
            self._prefs.apply_profile(data, require_host_destination=False)
            self._prefs.save()
            self.reload_from_prefs()
            self.saved.emit()
            return True, ""
        except (ValueError, OSError) as error:
            self._prefs.apply_profile(before)
            self._prefs.set_accent_color(before_accent)
            self.reload_from_prefs()
            return False, str(error)

    def export_to_file(self, path: str) -> tuple[bool, str]:
        if not self._is_aggregate_valid():
            return False, "Fix the invalid fields before exporting preferences."
        profile = self._collect_profile()
        try:
            Path(path).write_text(
                json.dumps(profile, indent=2), encoding="utf-8"
            )
        except OSError as error:
            return False, f"Could not write file: {error}"
        return True, ""

    def _collect_profile(self) -> dict:
        profile = dict(self._identity.values())
        profile.update(self._workspace.values())
        profile["pluginType"] = self._plugin_type.selected_type()
        profile["pluginFormats"] = self._formats.value()
        profile.update(self._compilation.values())
        profile.update(self._artefacts.values())
        profile["accentColor"] = self._prefs.accent_color
        return profile

    def _is_aggregate_valid(self) -> bool:
        return (
            self._identity.is_valid()
            and self._workspace.is_valid()
            and self._formats.is_valid()
            and self._artefacts.is_valid()
        )

    def _on_accent_save(self, color: str) -> None:
        if self._reload_guard:
            return
        self._prefs.set_accent_color(color)
        try:
            self._prefs.save()
        except OSError:
            return

    def _try_auto_save(self, *_args) -> None:
        if self._reload_guard:
            return
        if not self._is_aggregate_valid():
            return
        profile = self._collect_profile()
        try:
            self._prefs.apply_profile(profile)
            self._prefs.save()
            self._flash_saved_for_sender(self.sender())
            self.saved.emit()
        except (ValueError, OSError):
            return

    def _flash_saved_for_sender(self, sender) -> None:
        if sender is None:
            return
        targets = [
            *self._identity._fields.values(),
            self._workspace,
            self._compilation,
            self._artefacts,
        ]
        for target in targets:
            if hasattr(target, "is_saved_sender") and target.is_saved_sender(sender):
                if hasattr(target, "flash_saved"):
                    if target is self._compilation or target is self._workspace or target is self._artefacts:
                        target.flash_saved(sender)
                    else:
                        target.flash_saved()
                return

    def _connect_auto_save(self) -> None:
        self._identity.validityChanged.connect(self._try_auto_save)
        self._identity.field("manufacturer").valueChanged.connect(self._try_auto_save)
        self._identity.field("manufacturerCode").valueChanged.connect(self._try_auto_save)
        self._identity.field("pluginCode").valueChanged.connect(self._try_auto_save)
        self._identity.field("companyCopyright").valueChanged.connect(self._try_auto_save)
        self._identity.field("companyWebsite").valueChanged.connect(self._try_auto_save)
        self._identity.field("companyEmail").valueChanged.connect(self._try_auto_save)
        self._workspace.validityChanged.connect(self._try_auto_save)
        for field in self._workspace.path_fields().values():
            field.valueChanged.connect(self._try_auto_save)
        self._plugin_type.changed.connect(self._try_auto_save)
        self._formats.validityChanged.connect(self._try_auto_save)
        self._compilation.changed.connect(self._try_auto_save)
        self._artefacts.validityChanged.connect(self._try_auto_save)
        for box in self._artefacts._checks.values():
            box.toggled.connect(self._try_auto_save)
        for field in self._artefacts.path_fields().values():
            field.valueChanged.connect(self._try_auto_save)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._build_content())
        outer.addWidget(scroll)

    def _build_content(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(36)
        layout.addWidget(self._intro())
        layout.addWidget(self._accent)
        layout.addWidget(Section("Identity", self._identity))
        layout.addWidget(Section("Plugin Type", self._plugin_type))
        layout.addWidget(Section("Formats", self._formats))
        layout.addWidget(Section("Compilation", self._compilation))
        layout.addWidget(Section("Workspace", self._workspace))
        layout.addWidget(Section("Artefacts", self._artefacts))
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
