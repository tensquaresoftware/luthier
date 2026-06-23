"""User preferences persisted as JSON, replacing generator-configuration.py edits."""

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from core.project_spec import ProjectSpec

_DEFAULTS = {
    "manufacturer": "My Company",
    "manufacturerCode": "Myco",
    "pluginCode": "Mypl",
    "companyCopyright": "",
    "companyWebsite": "",
    "companyEmail": "",
    "destination": "",
    "juceDir": "",
    "artefactsDirWindows": "",
    "artefactsDirMacos": "",
    "artefactsDirLinux": "",
    "copyToSystemFolders": False,
    "copyToArtefactsDir": True,
}

_RENDER_KEYS = (
    "copyToSystemFolders",
    "copyToArtefactsDir",
    "artefactsDirWindows",
    "artefactsDirMacos",
    "artefactsDirLinux",
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

    def load(self) -> None:
        if self._path.exists():
            self._data.update(self._read())

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get(self, key: str):
        return self._data.get(key, _DEFAULTS.get(key))

    @property
    def juce_dir(self) -> str:
        return str(self.get("juceDir") or "").strip()

    def apply_form(self, identity: dict, artefacts: dict) -> None:
        for key in _IDENTITY_KEYS:
            if key in identity:
                self._data[key] = identity[key]
        for key in _ARTEFACT_KEYS:
            if key in artefacts:
                self._data[key] = artefacts[key]

    def update(self, spec: ProjectSpec) -> None:
        candidates = {
            "manufacturer": spec.manufacturer_name,
            "manufacturerCode": spec.manufacturer_code,
            "pluginCode": spec.plugin_code,
            "destination": spec.destination_dir,
            "companyCopyright": spec.company_copyright,
            "companyWebsite": spec.company_website,
            "companyEmail": spec.company_email,
            "artefactsDirWindows": spec.artefacts_dir_windows,
            "artefactsDirMacos": spec.artefacts_dir_macos,
            "artefactsDirLinux": spec.artefacts_dir_linux,
            "copyToSystemFolders": spec.copy_to_system_folders,
            "copyToArtefactsDir": spec.copy_to_artefacts_dir,
        }
        self._data.update({k: v for k, v in candidates.items() if isinstance(v, bool) or v})

    def generation_config(self) -> dict:
        return {key: self._data[key] for key in _RENDER_KEYS}

    def _read(self) -> dict:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
