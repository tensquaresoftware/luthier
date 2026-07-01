"""Portable path string normalization (NFR3 / JSON sidecar safety)."""

import sys
from pathlib import Path
from typing import Literal

from core import validation

_PATH_VALIDATORS = frozenset({
    validation.validate_destination,
    validation.validate_optional_path,
})

_PATH_DICT_KEYS = frozenset({
    "destination",
    "destinationDir",
    "juceDir",
    "destinationDirWindows",
    "destinationDirMacos",
    "destinationDirLinux",
    "juceDirWindows",
    "juceDirMacos",
    "juceDirLinux",
    "artefactsDirWindows",
    "artefactsDirMacos",
    "artefactsDirLinux",
})

WORKSPACE_DESTINATION_KEYS = (
    "destinationDirWindows",
    "destinationDirMacos",
    "destinationDirLinux",
)
WORKSPACE_JUCE_KEYS = (
    "juceDirWindows",
    "juceDirMacos",
    "juceDirLinux",
)
WORKSPACE_KEYS = WORKSPACE_DESTINATION_KEYS + WORKSPACE_JUCE_KEYS

_LEGACY_WORKSPACE_KEYS = ("destination", "destinationDir", "juceDir")


def is_path_validator(validator) -> bool:
    return validator in _PATH_VALIDATORS


def host_workspace_field_key(kind: Literal["destination", "juce"]) -> str:
    """JSON key for the workspace path of the OS Luthier is running on."""
    suffix = _host_os_suffix()
    if kind == "destination":
        return f"destinationDir{suffix}"
    return f"juceDir{suffix}"


def _host_os_suffix() -> str:
    if sys.platform == "win32":
        return "Windows"
    if sys.platform == "darwin":
        return "Macos"
    return "Linux"


def normalize_portable_path(path: str) -> str:
    """Store and display paths with forward slashes on all platforms."""
    if not path:
        return path
    return path.strip().replace("\\", "/")


def resolve_dir(path: str) -> Path | None:
    """Return a resolved Path when *path* names an existing directory, else None."""
    stripped = path.strip()
    if not stripped:
        return None
    candidate = Path(stripped).expanduser()
    try:
        candidate = candidate.resolve(strict=False)
    except OSError:
        pass
    return candidate if candidate.is_dir() else None


def migrate_workspace_keys(data: dict) -> dict:
    """Copy legacy single-path keys to host OS workspace keys; strip legacy keys."""
    out = dict(data)
    dest_host = host_workspace_field_key("destination")
    juce_host = host_workspace_field_key("juce")
    legacy_dest = str(out.get("destination") or "").strip()
    if not legacy_dest:
        legacy_dest = str(out.get("destinationDir") or "").strip()
    legacy_juce = str(out.get("juceDir") or "").strip()
    if legacy_dest and not str(out.get(dest_host) or "").strip():
        out[dest_host] = legacy_dest
    if legacy_juce and not str(out.get(juce_host) or "").strip():
        out[juce_host] = legacy_juce
    for key in _LEGACY_WORKSPACE_KEYS:
        out.pop(key, None)
    return out


def normalize_path_dict_values(data: dict) -> dict:
    """Return a copy with known path keys normalized."""
    out = migrate_workspace_keys(dict(data))
    for key in _PATH_DICT_KEYS:
        if key in out:
            if out[key] is None:
                out[key] = ""
            elif out[key]:
                out[key] = normalize_portable_path(str(out[key]))
    return out
