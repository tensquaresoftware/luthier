"""Portable path string normalization (NFR3 / JSON sidecar safety)."""

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


def normalize_path_dict_values(data: dict) -> dict:
    """Return a copy with known path keys normalized."""
    out = dict(data)
    for key in _PATH_DICT_KEYS:
        if key in out and out[key]:
            out[key] = normalize_portable_path(str(out[key]))
    return out
