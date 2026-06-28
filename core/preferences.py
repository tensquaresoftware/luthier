"""User preferences persisted as JSON, replacing generator-configuration.py edits."""

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from core import validation
from core.accent_colors import (
    ACCENT_COLOR_CORRECTED_MESSAGE,
    DEFAULT_ACCENT_COLOR,
    accent_color_file_value_differs,
    normalize_accent_color,
    validate_accent_color,
)
from core.json_files import atomic_write_text
from core.paths import normalize_path_dict_values, normalize_portable_path
from core.plugin_settings import PLUGIN_TYPES, TYPE_INSTRUMENT

_DEFAULTS = {
    "manufacturer": "My Company",
    "manufacturerCode": "Myco",
    "pluginCode": "Mypl",
    "companyCopyright": "",
    "companyWebsite": "",
    "companyEmail": "",
    "destination": "",
    "juceDir": "",
    "pluginType": TYPE_INSTRUMENT,
    "pluginFormats": "AU VST3 Standalone",
    "cxxStandard": "C++17",
    "preprocessorDefinitions": "",
    "headerSearchPaths": "",
    "artefactsDirWindows": "",
    "artefactsDirMacos": "",
    "artefactsDirLinux": "",
    "copyToSystemFolders": False,
    "copyToArtefactsDir": False,
}

_PROFILE_KEYS = (
    "manufacturer", "manufacturerCode", "pluginCode",
    "companyCopyright", "companyWebsite", "companyEmail",
    "destination", "juceDir",
    "pluginType", "pluginFormats", "cxxStandard",
    "preprocessorDefinitions", "headerSearchPaths",
    "copyToSystemFolders", "copyToArtefactsDir",
    "artefactsDirWindows", "artefactsDirMacos", "artefactsDirLinux",
)

_IDENTITY_KEYS = (
    "manufacturer", "manufacturerCode", "pluginCode",
    "companyCopyright", "companyWebsite", "companyEmail",
    "destination", "juceDir",
)

_ARTEFACT_KEYS = (
    "copyToSystemFolders", "copyToArtefactsDir",
    "artefactsDirWindows", "artefactsDirMacos", "artefactsDirLinux",
)

_COMPILATION_KEYS = ("cxxStandard", "preprocessorDefinitions", "headerSearchPaths")

_PLUGIN_KEYS = ("pluginType", "pluginFormats")

_VALID_PLUGIN_TYPES = frozenset(key for key, _ in PLUGIN_TYPES)
_VALID_PLUGIN_FORMATS = frozenset({"AU", "VST3", "Standalone"})
_VALID_CXX = frozenset({"C++17", "C++20", "C++23"})

LOAD_WARNING_MESSAGE = (
    "Preferences file was corrupt and has been reset to defaults."
)


def factory_defaults(desktop: str | None = None) -> dict:
    """Return a fresh profile dict with factory values (Desktop destination)."""
    data = dict(_DEFAULTS)
    if desktop is None:
        desktop = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DesktopLocation
        )
    if not str(desktop).strip():
        desktop = str(Path.home())
    data["destination"] = normalize_portable_path(desktop)
    return data


def _complete_profile(data: dict) -> dict:
    """Fill missing profile keys from code defaults (import full-replace semantics)."""
    return {key: data.get(key, _DEFAULTS.get(key)) for key in _PROFILE_KEYS}


def validate_profile(data: dict) -> tuple[bool, str]:
    """Validate an imported or in-memory profile dict; return (ok, first error)."""
    checks = [
        ("manufacturer", validation.validate_manufacturer_name),
        ("manufacturerCode", validation.validate_manufacturer_code),
        ("pluginCode", validation.validate_plugin_code),
        ("companyCopyright", validation.validate_optional),
        ("companyWebsite", validation.validate_optional),
        ("companyEmail", validation.validate_optional),
        ("destination", validation.validate_destination),
        ("juceDir", validation.validate_optional_path),
        ("preprocessorDefinitions", validation.validate_optional),
        ("headerSearchPaths", validation.validate_optional),
        ("artefactsDirWindows", validation.validate_optional_path),
        ("artefactsDirMacos", validation.validate_optional_path),
        ("artefactsDirLinux", validation.validate_optional_path),
    ]
    for key, validator in checks:
        ok, message = validator(str(data.get(key, "")))
        if not ok:
            return False, message
    plugin_type = str(data.get("pluginType", ""))
    if plugin_type not in _VALID_PLUGIN_TYPES:
        return False, (
            "Plugin type must be instrument, audio-effect, or midi-effect."
        )
    formats = str(data.get("pluginFormats", "")).split()
    if not formats:
        return False, "Select at least one plugin format."
    if not all(fmt in _VALID_PLUGIN_FORMATS for fmt in formats):
        return False, "Plugin formats must be AU, VST3, and/or Standalone."
    cxx = str(data.get("cxxStandard", ""))
    if cxx not in _VALID_CXX:
        return False, "C++ standard must be C++17, C++20, or C++23."
    for flag in ("copyToSystemFolders", "copyToArtefactsDir"):
        if flag in data and not isinstance(data[flag], bool):
            return False, f"{flag} must be a boolean."
    if "accentColor" in data:
        ok, message = validate_accent_color(data["accentColor"])
        if not ok:
            return False, message
    return True, ""


class Preferences:
    """Loads, holds and saves the persisted default values."""

    def __init__(self, path: Path):
        self._path = path
        self._data = dict(_DEFAULTS)
        self._accent_color_warning: str | None = None
        self._load_warning: str | None = None
        self._initialized = False

    @staticmethod
    def default_path() -> Path:
        location = QStandardPaths.StandardLocation.AppConfigLocation
        base = QStandardPaths.writableLocation(location)
        return Path(base) / "preferences.json"

    def ensure_initialized(self) -> None:
        if self._initialized:
            return
        if self._path.exists():
            self.load()
        else:
            self._data = factory_defaults()
            self._data["accentColor"] = DEFAULT_ACCENT_COLOR
            try:
                self.save()
            except OSError as error:
                raise OSError(
                    f"Could not create preferences at {self._path}: {error}"
                ) from error
        self._initialized = True

    @property
    def accent_color_warning(self) -> str | None:
        return self._accent_color_warning

    @property
    def load_warning(self) -> str | None:
        return self._load_warning

    def load(self) -> None:
        self._accent_color_warning = None
        self._load_warning = None
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._reset_corrupt_file()
            return
        if not isinstance(raw, dict):
            self._reset_corrupt_file()
            return
        raw_accent = raw.get("accentColor")
        accent = normalize_accent_color(raw_accent)
        self._data.update(raw)
        ok, _message = validate_profile(self.to_dict())
        if not ok:
            self._data = factory_defaults()
        self._data["accentColor"] = accent
        if (
            raw_accent is not None
            and str(raw_accent).strip()
            and not validate_accent_color(raw_accent)[0]
        ):
            self._accent_color_warning = ACCENT_COLOR_CORRECTED_MESSAGE
        if not ok or accent_color_file_value_differs(raw_accent):
            self.save()

    def save(self) -> None:
        atomic_write_text(self._path, json.dumps(self._data, indent=2))

    def _reset_corrupt_file(self) -> None:
        self._load_warning = LOAD_WARNING_MESSAGE
        self._data = factory_defaults()
        self._data["accentColor"] = DEFAULT_ACCENT_COLOR
        try:
            self.save()
        except OSError:
            pass

    def get(self, key: str):
        return self._data.get(key, _DEFAULTS.get(key))

    @property
    def accent_color(self) -> str:
        return normalize_accent_color(self._data.get("accentColor"))

    def set_accent_color(self, value: str) -> None:
        self._data["accentColor"] = normalize_accent_color(value)

    @property
    def juce_dir(self) -> str:
        return str(self.get("juceDir") or "").strip()

    def to_dict(self) -> dict:
        return {key: self.get(key) for key in _PROFILE_KEYS}

    def apply_profile(self, data: dict) -> None:
        profile = _complete_profile(normalize_path_dict_values(data))
        ok, message = validate_profile(profile)
        if not ok:
            raise ValueError(message)
        for key in _PROFILE_KEYS:
            self._data[key] = profile[key]
        if "accentColor" in data:
            ok, message = validate_accent_color(data["accentColor"])
            if not ok:
                raise ValueError(message)
            self.set_accent_color(data["accentColor"])

    def seed_dict(self) -> dict:
        """Project-form seed snapshot (camelCase keys for ProjectPage.load/reset)."""
        seed = {
            "manufacturerName": self.get("manufacturer"),
            "manufacturerCode": self.get("manufacturerCode"),
            "pluginCode": self.get("pluginCode"),
            "companyCopyright": self.get("companyCopyright"),
            "companyWebsite": self.get("companyWebsite"),
            "companyEmail": self.get("companyEmail"),
            "destinationDir": self.get("destination"),
            "juceDir": self.get("juceDir"),
            "pluginType": self.get("pluginType"),
            "pluginFormats": self.get("pluginFormats"),
            "cxxStandard": self.get("cxxStandard"),
            "preprocessorDefinitions": self.get("preprocessorDefinitions"),
            "headerSearchPaths": self.get("headerSearchPaths"),
            "copyToSystemFolders": self.get("copyToSystemFolders"),
            "copyToArtefactsDir": self.get("copyToArtefactsDir"),
            "artefactsDirWindows": self.get("artefactsDirWindows"),
            "artefactsDirMacos": self.get("artefactsDirMacos"),
            "artefactsDirLinux": self.get("artefactsDirLinux"),
        }
        # Legacy keys for ProjectInfoPage init until Story 5.2 wires full seed.
        seed["manufacturer"] = seed["manufacturerName"]
        seed["destination"] = seed["destinationDir"]
        return seed

    def apply_form(self, identity: dict, artefacts: dict) -> None:
        profile = dict(self.to_dict())
        for key in _IDENTITY_KEYS:
            if key in identity:
                profile[key] = identity[key]
        for key in _ARTEFACT_KEYS:
            if key in artefacts:
                profile[key] = artefacts[key]
        for key in _PLUGIN_KEYS + _COMPILATION_KEYS:
            if key in identity:
                profile[key] = identity[key]
        self.apply_profile(profile)

