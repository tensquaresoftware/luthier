"""Lightweight app state persisted separately from preferences.json."""

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from core.json_files import atomic_write_text
from core.preferences import Preferences


def _is_valid_dir(path: str) -> bool:
    stripped = str(path).strip()
    return bool(stripped) and Path(stripped).is_dir()


LOAD_WARNING_MESSAGE = (
    "App state file was corrupt and has been reset to defaults."
)


def _default_data() -> dict:
    return {
        "lastUsedParentDir": "",
        "lastPrefsProfileDir": "",
        "windowGeometry": "",
        "windowRect": None,
        "windowMaximized": False,
    }


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
        self._data: dict = _default_data()
        self._load_warning: str | None = None

    @staticmethod
    def default_path() -> Path:
        return Preferences.default_path().parent / "app_state.json"

    @property
    def load_warning(self) -> str | None:
        return self._load_warning

    def load(self) -> None:
        self._load_warning = None
        if not self._path.exists():
            return
        try:
            loaded = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._reset_corrupt_file()
            return
        if not isinstance(loaded, dict):
            self._reset_corrupt_file()
            return
        parent = loaded.get("lastUsedParentDir", "")
        if isinstance(parent, str):
            self._data["lastUsedParentDir"] = parent
        prefs_dir = loaded.get("lastPrefsProfileDir", "")
        if isinstance(prefs_dir, str):
            self._data["lastPrefsProfileDir"] = prefs_dir
        geometry = loaded.get("windowGeometry", "")
        if isinstance(geometry, str):
            self._data["windowGeometry"] = geometry
        rect = loaded.get("windowRect")
        if isinstance(rect, dict):
            self._data["windowRect"] = rect
        maximized = loaded.get("windowMaximized", False)
        if isinstance(maximized, bool):
            self._data["windowMaximized"] = maximized

    def save(self) -> None:
        atomic_write_text(self._path, json.dumps(self._data, indent=2))

    def _reset_corrupt_file(self) -> None:
        self._load_warning = LOAD_WARNING_MESSAGE
        self._data = _default_data()
        try:
            self.save()
        except OSError:
            pass

    def remember_parent(self, dir_path: str) -> None:
        stripped = str(dir_path).strip()
        if not stripped:
            return
        self._data["lastUsedParentDir"] = str(Path(stripped).resolve())

    def remember_prefs_profile_dir(self, file_path: str) -> None:
        stripped = str(file_path).strip()
        if not stripped:
            return
        parent = Path(stripped).resolve().parent
        if parent.is_dir():
            self._data["lastPrefsProfileDir"] = str(parent)

    def prefs_profile_dir(self) -> str:
        last = self._data.get("lastPrefsProfileDir", "")
        if isinstance(last, str) and _is_valid_dir(last):
            return last
        return _desktop_path()

    def set_window_geometry_b64(self, value: str) -> None:
        self._data["windowGeometry"] = value

    def window_geometry_b64(self) -> str:
        stored = self._data.get("windowGeometry", "")
        return stored if isinstance(stored, str) else ""

    def set_window_rect(self, x: int, y: int, width: int, height: int) -> None:
        self._data["windowRect"] = {
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
        }

    def window_rect(self) -> dict | None:
        rect = self._data.get("windowRect")
        if not isinstance(rect, dict):
            return None
        try:
            return {
                "x": int(rect["x"]),
                "y": int(rect["y"]),
                "width": int(rect["width"]),
                "height": int(rect["height"]),
            }
        except (KeyError, TypeError, ValueError):
            return None

    def set_window_maximized(self, value: bool) -> None:
        self._data["windowMaximized"] = bool(value)

    def window_maximized(self) -> bool:
        return bool(self._data.get("windowMaximized", False))

    def dialog_start_dir(self, field_value: str = "") -> str:
        if _is_valid_dir(field_value):
            return str(Path(field_value.strip()).resolve())
        last = self._data.get("lastUsedParentDir", "")
        if isinstance(last, str) and _is_valid_dir(last):
            return last
        return _desktop_path()
