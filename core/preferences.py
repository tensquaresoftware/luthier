"""User preferences persisted as JSON, replacing generator-configuration.py edits."""

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

_DEFAULTS = {
    "generatorRoot": "",
    "manufacturer": "",
    "manufacturerCode": "",
    "pluginCode": "",
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

    def file_exists(self) -> bool:
        return self._path.exists()

    def load(self) -> None:
        if self._path.exists():
            self._data.update(self._read())

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get(self, key: str):
        return self._data.get(key, _DEFAULTS.get(key))

    def update(self, values: dict) -> None:
        self._data.update({k: v for k, v in values.items() if k in _DEFAULTS})

    def generation_config(self) -> dict:
        return {key: self._data[key] for key in _RENDER_KEYS}

    def _read(self) -> dict:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
