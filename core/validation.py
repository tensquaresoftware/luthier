"""Pure field validators for the Luthier form.

Self-contained mirror of the generator's input rules (InputCollector,
pathValidation, uiConstants). Kept dependency-free so the form stays
testable without importing the generator. Source of truth for the specs:
Juce-Project-Generator/Generator.
"""

import re

ValidationResult = tuple[bool, str]

_PROJECT_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
_DISPLAY_NAME_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_"
)
_CODE_LENGTH = 4


def _ok() -> ValidationResult:
    return True, ""


def validate_project_name(value: str) -> ValidationResult:
    if _PROJECT_NAME_RE.match(value):
        return _ok()
    return False, "Start with a letter; letters, digits, '-' and '_' only."


def validate_display_name(value: str) -> ValidationResult:
    invalid = sorted({c for c in value if c not in _DISPLAY_NAME_CHARS})
    if not invalid:
        return _ok()
    chars = ", ".join(f"'{c}'" for c in invalid)
    return False, f"Invalid characters: {chars}"


def validate_version(value: str) -> ValidationResult:
    if value.strip():
        return _ok()
    return False, "Version is required."


def validate_manufacturer_name(value: str) -> ValidationResult:
    if value.strip():
        return _ok()
    return False, "Manufacturer name is required."


def validate_manufacturer_code(value: str) -> ValidationResult:
    if len(value) == _CODE_LENGTH and value.isalpha():
        return _ok()
    return False, f"Exactly {_CODE_LENGTH} alphabetic characters."


def validate_plugin_code(value: str) -> ValidationResult:
    if len(value) == _CODE_LENGTH and value.isalnum():
        return _ok()
    return False, f"Exactly {_CODE_LENGTH} alphanumeric characters."


def _no_accents(value: str) -> ValidationResult:
    accented = sorted({c for c in value if ord(c) > 127})
    if not accented:
        return _ok()
    chars = ", ".join(f"'{c}'" for c in accented)
    return False, f"No accented characters in paths: {chars}"


def validate_destination(value: str) -> ValidationResult:
    if not value.strip():
        return False, "Destination is required."
    return _no_accents(value)


def validate_optional_path(value: str) -> ValidationResult:
    return _no_accents(value)
