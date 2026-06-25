"""Shared path field specs for Preferences and Project pages."""

import sys

from app.widgets.validated_field import FieldSpec
from core import validation


def juce_dir_placeholder() -> str:
    if sys.platform == "win32":
        return "C:/Program Files/JUCE"
    if sys.platform == "darwin":
        return "/Applications/JUCE"
    return "/usr/local/JUCE"


def destination_field_spec(
    default: str,
    *,
    key: str = "destinationDir",
    label: str = "Destination folder *",
) -> FieldSpec:
    return FieldSpec(key, label, validation.validate_destination, default=default)


def juce_field_spec(default: str) -> FieldSpec:
    return FieldSpec(
        "juceDir",
        "JUCE directory",
        validation.validate_optional_path,
        default=default,
        placeholder=juce_dir_placeholder(),
    )
