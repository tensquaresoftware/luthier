"""Pure field validators for the Luthier form.

Self-contained and dependency-free so the form stays testable. Plugin identity
codes follow the GarageBand 10.3 / JUCE AU convention (4-char codes, ASCII-only
paths).
"""

import random
import re
import string

ValidationResult = tuple[bool, str]

_PROJECT_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
_DISPLAY_NAME_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_"
)
_MANUFACTURER_CODE_RE = re.compile(r"^[A-Z][a-z]{3}$")
_PLUGIN_CODE_RE = re.compile(r"^[A-Z][a-z0-9]{3}$")
_RESERVED_PLUGIN_CODE = "DEMO"


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
    if _MANUFACTURER_CODE_RE.match(value):
        return _ok()
    return False, "First uppercase letter, then 3 lowercase letters."


def validate_plugin_code(value: str) -> ValidationResult:
    if value.upper() == _RESERVED_PLUGIN_CODE:
        return False, f"'{_RESERVED_PLUGIN_CODE}' is reserved by Apple."
    if _PLUGIN_CODE_RE.match(value):
        return _ok()
    return False, "First uppercase letter, then 3 lowercase letters or digits."


def generate_manufacturer_code() -> str:
    """Return a random GarageBand-compatible manufacturer code."""
    first = random.choice(string.ascii_uppercase)
    rest = "".join(random.choices(string.ascii_lowercase, k=3))
    return first + rest


def generate_plugin_code() -> str:
    """Return a random GarageBand-compatible plugin code."""
    alphabet = string.ascii_lowercase + string.digits
    while True:
        first = random.choice(string.ascii_uppercase)
        rest = "".join(random.choices(alphabet, k=3))
        code = first + rest
        if code.upper() != _RESERVED_PLUGIN_CODE:
            return code


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


def validate_optional(value: str) -> ValidationResult:
    return _ok()
