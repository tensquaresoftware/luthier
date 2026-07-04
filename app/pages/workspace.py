"""Workspace section: per-OS destination and JUCE paths.

Live per-project fields on the Project tab, seeded from preferences.
A native Choose… button is shown only for the path row matching the host OS.
"""

from collections.abc import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.pages.path_specs import (
    host_workspace_field_key,
    workspace_destination_specs,
    workspace_juce_specs,
)
from app.widgets.folder_field import FolderField
from app.widgets.os_path_tree_group import OsPathTreeGroup
from app.widgets.validated_field import ValidatedField, make_field_label
from core.display import display_str
from core.preferences import Preferences


class WorkspaceSection(QWidget):
    """Per-OS destination and JUCE directories."""

    validityChanged = Signal(bool)

    def __init__(
        self,
        prefs: Preferences,
        folder_start_resolver: Callable[[str], str] | None = None,
    ):
        super().__init__()
        self._prefs = prefs
        self._path_fields: dict[str, ValidatedField | FolderField] = {}
        self._build_ui(folder_start_resolver)

    def path_fields(self) -> dict[str, ValidatedField | FolderField]:
        return dict(self._path_fields)

    def values(self) -> dict:
        return {key: field.value() for key, field in self._path_fields.items()}

    def is_valid(self) -> bool:
        host_dest = host_workspace_field_key("destination")
        if not self._path_fields[host_dest].is_valid():
            return False
        return all(field.is_valid() for field in self._path_fields.values())

    def load(self, values: dict) -> None:
        for key, field in self._path_fields.items():
            if key in values:
                field.set_value(display_str(values[key]))

    def set_host_destination(self, value: str) -> None:
        host_dest = host_workspace_field_key("destination")
        self._path_fields[host_dest].set_value(value)

    def flash_saved(self, sender) -> None:
        for field in self._path_fields.values():
            if field.is_saved_sender(sender):
                field.flash_saved()
                return

    def is_saved_sender(self, sender) -> bool:
        return any(field.is_saved_sender(sender) for field in self._path_fields.values())

    def _build_ui(self, folder_start_resolver: Callable[[str], str] | None) -> None:
        defaults = self._prefs.to_dict()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._build_path_tree(
            make_field_label("Destination folder *"),
            workspace_destination_specs(defaults),
            folder_start_resolver,
            "Choose destination folder",
        ))
        layout.addWidget(self._build_path_tree(
            make_field_label("JUCE directory"),
            workspace_juce_specs(defaults),
            folder_start_resolver,
            "Choose JUCE directory",
        ))

    def _build_path_tree(
        self,
        anchor,
        specs,
        folder_start_resolver: Callable[[str], str] | None,
        choose_title: str,
    ) -> OsPathTreeGroup:
        host_dest = host_workspace_field_key("destination")
        host_juce = host_workspace_field_key("juce")
        fields = []
        for spec in specs:
            if spec.key in (host_dest, host_juce):
                field = FolderField(
                    spec,
                    choose_title,
                    start_dir_resolver=folder_start_resolver,
                )
            else:
                field = ValidatedField(spec)
            field.validityChanged.connect(self.validityChanged)
            self._path_fields[spec.key] = field
            fields.append(field)
        return OsPathTreeGroup(anchor, fields)
