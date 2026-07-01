"""Reads a generated project back into form values via `.luthier.json` sidecar."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from core import plugin_settings
from core.paths import host_workspace_field_key, normalize_portable_path
from core.project_spec import ProjectSpec

_SIDECAR = ".luthier.json"

_VALID_PLUGIN_TYPES = frozenset({
    plugin_settings.TYPE_INSTRUMENT,
    plugin_settings.TYPE_AUDIO_EFFECT,
    plugin_settings.TYPE_MIDI_EFFECT,
})


@dataclass(frozen=True)
class ProjectReadResult:
    spec: Optional[ProjectSpec]
    error: str | None = None


def read_project_result(project_dir: Path) -> ProjectReadResult:
    sidecar = project_dir / _SIDECAR
    if not sidecar.exists():
        return ProjectReadResult(
            spec=None,
            error="Not a Luthier project or companion file .luthier.json is missing.",
        )
    return _read_sidecar_result(sidecar, project_dir)


def _read_sidecar_result(sidecar: Path, project_dir: Path) -> ProjectReadResult:
    try:
        raw = sidecar.read_text(encoding="utf-8")
    except OSError:
        return ProjectReadResult(
            spec=None,
            error="Could not read sidecar file.",
        )
    except UnicodeDecodeError:
        return ProjectReadResult(
            spec=None,
            error="Sidecar file is not valid UTF-8 text.",
        )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return ProjectReadResult(
            spec=None,
            error="Sidecar file is not valid JSON.",
        )
    if not isinstance(data, dict):
        return ProjectReadResult(
            spec=None,
            error="Sidecar file must contain a JSON object.",
        )
    if not data:
        return ProjectReadResult(
            spec=None,
            error="Sidecar file is empty — no project configuration found.",
        )
    validation_error = _validate_sidecar(data)
    if validation_error:
        return ProjectReadResult(spec=None, error=validation_error)
    host_dest = host_workspace_field_key("destination")
    data[host_dest] = normalize_portable_path(str(project_dir.parent))
    return ProjectReadResult(spec=ProjectSpec.from_dict(data))


def _validate_sidecar(data: dict) -> str | None:
    problems = []

    def check_required_str(key: str) -> None:
        if key not in data:
            problems.append(f"{key} is required")
            return
        value = data[key]
        if value is None:
            problems.append(f"{key} must not be null")
            return
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{key} must be a non-empty string")

    check_required_str("projectName")
    check_required_str("pluginFormats")

    if "pluginType" not in data:
        problems.append("pluginType is required")
    elif data["pluginType"] is None:
        problems.append("pluginType must not be null")
    elif not isinstance(data["pluginType"], str):
        problems.append("pluginType must be a string")
    elif data["pluginType"] not in _VALID_PLUGIN_TYPES:
        valid = ", ".join(sorted(_VALID_PLUGIN_TYPES))
        problems.append(f"pluginType must be one of: {valid}")

    if not problems:
        return None
    return "Sidecar is invalid: " + "; ".join(problems)
