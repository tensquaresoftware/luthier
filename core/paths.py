"""Portable path string normalization (NFR3 / JSON sidecar safety)."""

from pathlib import Path

from core import validation

_PATH_VALIDATORS = frozenset({
    validation.validate_destination,
    validation.validate_optional_path,
})

_PATH_DICT_KEYS = frozenset({
    "destination",
    "destinationDir",
    "juceDir",
    "artefactsDirWindows",
    "artefactsDirMacos",
    "artefactsDirLinux",
})


def is_path_validator(validator) -> bool:
    return validator in _PATH_VALIDATORS


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


def normalize_path_dict_values(data: dict) -> dict:
    """Return a copy with known path keys normalized."""
    out = dict(data)
    for key in _PATH_DICT_KEYS:
        if key in out:
            if out[key] is None:
                out[key] = ""
            elif out[key]:
                out[key] = normalize_portable_path(str(out[key]))
    return out
