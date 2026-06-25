"""Lightweight app state persisted separately from preferences.json."""

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from core.preferences import Preferences


def _is_valid_dir(path: str) -> bool:
    stripped = str(path).strip()
    return bool(stripped) and Path(stripped).is_dir()


def _desktop_path() -> str:
    desktop = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DesktopLocation
    )
    if not str(desktop).strip():
        return str(Path.home())
    return str(desktop)


class AppState:
    """Last-used parent directory and other non-profile app state."""

    def __init__(self, path: Path):
        self._path = path
        self._data: dict = {"lastUsedParentDir": ""}

    @staticmethod
    def default_path() -> Path:
        return Preferences.default_path().parent / "app_state.json"

    def load(self) -> None:
        if not self._path.exists():
            return
        try:
            loaded = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if isinstance(loaded, dict):
            parent = loaded.get("lastUsedParentDir", "")
            if isinstance(parent, str):
                self._data["lastUsedParentDir"] = parent

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def remember_parent(self, dir_path: str) -> None:
        stripped = str(dir_path).strip()
        if not stripped:
            return
        self._data["lastUsedParentDir"] = str(Path(stripped).resolve())

    def dialog_start_dir(self, field_value: str = "") -> str:
        if _is_valid_dir(field_value):
            return str(Path(field_value.strip()).resolve())
        last = self._data.get("lastUsedParentDir", "")
        if isinstance(last, str) and _is_valid_dir(last):
            return last
        return _desktop_path()
