"""Shared path field specs for Preferences and Project pages."""

import sys

from app.widgets.validated_field import FieldSpec
from core import validation
from core.paths import WORKSPACE_DESTINATION_KEYS, WORKSPACE_JUCE_KEYS, host_workspace_field_key

# Left margin for per-OS rows nested under section headings (Workspace, Artefacts).
# Checkbox label inset (theme.py): padding-left 2 + indicator 16 + spacing 8 = 26;
# +2 px so FieldLabel text lines up with QCheckBox label text.
OS_FIELD_LEFT_MARGIN = 28
OS_TREE_TRUNK_X = 14
OS_TREE_LABEL_GAP = 7
OS_TREE_BRANCH_END = OS_FIELD_LEFT_MARGIN - OS_TREE_LABEL_GAP
OS_TREE_LINE_WIDTH = 1.0

_WORKSPACE_DEST_LABELS = {
    "destinationDirWindows": "Windows",
    "destinationDirMacos": "macOS",
    "destinationDirLinux": "Linux",
}

_WORKSPACE_JUCE_LABELS = {
    "juceDirWindows": "Windows",
    "juceDirMacos": "macOS",
    "juceDirLinux": "Linux",
}


def host_artefact_field_key() -> str:
    """Preference/spec key for the artefact path of the OS Luthier is running on."""
    if sys.platform == "win32":
        return "artefactsDirWindows"
    if sys.platform == "darwin":
        return "artefactsDirMacos"
    return "artefactsDirLinux"


def workspace_destination_specs(defaults: dict) -> list[FieldSpec]:
    host_key = host_workspace_field_key("destination")
    specs = []
    for key in WORKSPACE_DESTINATION_KEYS:
        validator = (
            validation.validate_destination
            if key == host_key
            else validation.validate_optional_path
        )
        specs.append(
            FieldSpec(
                key,
                _WORKSPACE_DEST_LABELS[key],
                validator,
                default=str(defaults.get(key, "") or ""),
            )
        )
    return specs


def workspace_juce_specs(defaults: dict) -> list[FieldSpec]:
    return [
        FieldSpec(
            key,
            _WORKSPACE_JUCE_LABELS[key],
            validation.validate_optional_path,
            default=str(defaults.get(key, "") or ""),
        )
        for key in WORKSPACE_JUCE_KEYS
    ]
