"""Read and override the editable C++ source templates.

Defaults ship in templates/Source/. User overrides live in the app config
directory so a packaged (read-only) install can still be customized.
"""

from pathlib import Path

from PySide6.QtCore import QStandardPaths

from core.project_generator import templates_dir

SOURCE_FILES = (
    "PluginProcessor.h",
    "PluginProcessor.cpp",
    "PluginEditor.h",
    "PluginEditor.cpp",
)

GITIGNORE_FILE = ".gitignore"

EDITABLE_FILES = SOURCE_FILES + (GITIGNORE_FILE,)


def templates_root() -> Path:
    location = QStandardPaths.StandardLocation.AppConfigLocation
    base = QStandardPaths.writableLocation(location)
    return Path(base) / "templates"


def overrides_dir() -> Path:
    return templates_root() / "Source"


def _bundled_path(name: str) -> Path:
    if name == GITIGNORE_FILE:
        return templates_dir() / GITIGNORE_FILE
    return templates_dir() / "Source" / name


def _override_path(name: str) -> Path:
    if name == GITIGNORE_FILE:
        return templates_root() / GITIGNORE_FILE
    return overrides_dir() / name


def has_override(name: str) -> bool:
    return _override_path(name).exists()


def read_default(name: str) -> str:
    return _bundled_path(name).read_text(encoding="utf-8")


def read_effective(name: str) -> str:
    path = _override_path(name)
    return path.read_text(encoding="utf-8") if path.exists() else read_default(name)


def save_override(name: str, content: str) -> None:
    target = _override_path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def reset(name: str) -> None:
    _override_path(name).unlink(missing_ok=True)
