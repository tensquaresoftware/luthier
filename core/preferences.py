"""User preferences persisted as JSON, replacing generator-configuration.py edits."""

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from core import validation

_DEFAULTS = {
    "manufacturer": "My Company",
    "manufacturerCode": "Myco",
    "pluginCode": "Mypl",
    "companyCopyright": "",
    "companyWebsite": "",
    "companyEmail": "",
    "destination": "",
    "juceDir": "",
    "pluginType": "synth",
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

_VALID_PLUGIN_TYPES = frozenset({"synth", "effect", "midi"})
_VALID_PLUGIN_FORMATS = frozenset({"AU", "VST3", "Standalone"})
_VALID_CXX = frozenset({"C++17", "C++20", "C++23"})


def factory_defaults(desktop: str | None = None) -> dict:
    """Return a fresh profile dict with factory values (Desktop destination)."""
    data = dict(_DEFAULTS)
    if desktop is None:
        desktop = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DesktopLocation
        )
    if not str(desktop).strip():
        desktop = str(Path.home())
    data["destination"] = desktop
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
        return False, "Plugin type must be synth, effect, or midi."
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
    return True, ""


class Preferences:
    """Loads, holds and saves the persisted default values."""

    def __init__(self, path: Path):
        self._path = path
        self._data = dict(_DEFAULTS)

    @staticmethod
    def default_path() -> Path:
        location = QStandardPaths.StandardLocation.AppConfigLocation
        base = QStandardPaths.writableLocation(location)
        return Path(base) / "preferences.json"

    def ensure_initialized(self) -> None:
        if self._path.exists():
            self.load()
        else:
            self._data = factory_defaults()
            try:
                self.save()
            except OSError as error:
                raise OSError(
                    f"Could not create preferences at {self._path}: {error}"
                ) from error

    def load(self) -> None:
        if self._path.exists():
            self._data.update(self._read())
        ok, _message = validate_profile(self.to_dict())
        if not ok:
            self._data = factory_defaults()
            self.save()

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get(self, key: str):
        return self._data.get(key, _DEFAULTS.get(key))

    @property
    def juce_dir(self) -> str:
        return str(self.get("juceDir") or "").strip()

    def to_dict(self) -> dict:
        return {key: self.get(key) for key in _PROFILE_KEYS}

    def apply_profile(self, data: dict) -> None:
        profile = _complete_profile(data)
        ok, message = validate_profile(profile)
        if not ok:
            raise ValueError(message)
        for key in _PROFILE_KEYS:
            self._data[key] = profile[key]

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

    def _read(self) -> dict:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
