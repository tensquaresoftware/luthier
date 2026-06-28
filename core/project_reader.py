"""Reads a generated project back into form values.

When `.luthier.json` exists at the project root, it is the authoritative
source (sidecar-first per AD-3). Otherwise CMakeLists.txt is parsed via regex
as a fallback for legacy projects without a sidecar.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from core import plugin_settings
from core.paths import normalize_portable_path
from core.project_spec import ProjectSpec, _coerce_bool

_SIDECAR = ".luthier.json"

_VALID_PLUGIN_TYPES = frozenset({
    plugin_settings.TYPE_INSTRUMENT,
    plugin_settings.TYPE_AUDIO_EFFECT,
    plugin_settings.TYPE_MIDI_EFFECT,
})

_PROJECT_RE = re.compile(r"project\(\s*(\S+)\s+VERSION\s+([^\s)]+)")
_FORMATS_RE = re.compile(r"set\(\s*PLUGIN_FORMATS_LIST\s+([^)]*)\)")
_SET_RE = re.compile(r'set\s*\(\s*(\w+)\s+("(?:[^"\\]|\\.)*"|[^\s)]+)')
_CXX_RE = re.compile(r"set\(\s*CMAKE_CXX_STANDARD\s+(\w+)\s*\)")
_INCLUDE_RE = re.compile(r"target_include_directories\(\s*\S+\s+PRIVATE\s*(.*?)\)", re.DOTALL)
_DEFS_RE = re.compile(r"target_compile_definitions\(\s*\S+\s+PUBLIC\s*(.*?)\)", re.DOTALL)
_IS_SYNTH_RE = re.compile(r"\bIS_SYNTH\s+(TRUE|FALSE)\b")

_QUOTED_FIELDS = {
    "manufacturerName": "COMPANY_NAME",
    "manufacturerCode": "PLUGIN_MANUFACTURER_CODE",
    "pluginCode": "PLUGIN_CODE",
    "projectDisplayName": "PLUGIN_NAME",
    "companyCopyright": "COMPANY_COPYRIGHT",
    "companyWebsite": "COMPANY_WEBSITE",
    "companyEmail": "COMPANY_EMAIL",
}

_REQUIRED_CMAKE_KEYS = (
    "projectName",
    "projectVersion",
    "pluginFormats",
    "manufacturerName",
    "manufacturerCode",
    "pluginCode",
    "projectDisplayName",
    "companyCopyright",
    "companyWebsite",
    "companyEmail",
    "cxxStandard",
)

_FIELD_LABELS = {
    "projectName": "Project Name",
    "projectVersion": "Project Version",
    "pluginFormats": "Plugin Formats",
    "manufacturerName": "Company Name",
    "manufacturerCode": "Manufacturer Code",
    "pluginCode": "Plugin Code",
    "projectDisplayName": "Project Display Name",
    "companyCopyright": "Company Copyright",
    "companyWebsite": "Company Website",
    "companyEmail": "Company Email",
    "cxxStandard": "C++ Standard",
}


@dataclass(frozen=True)
class ProjectReadResult:
    spec: Optional[ProjectSpec]
    missing_fields: tuple[str, ...] = ()
    error: str | None = None


def read_project_result(project_dir: Path) -> ProjectReadResult:
    sidecar = project_dir / _SIDECAR
    if sidecar.exists():
        return _read_sidecar_result(sidecar, project_dir)
    return _read_from_cmake_result(project_dir)


def read_project(project_dir: Path) -> Optional[ProjectSpec]:
    return read_project_result(project_dir).spec


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
    data["destinationDir"] = normalize_portable_path(str(project_dir.parent))
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


def _read_from_cmake(project_dir: Path) -> Optional[ProjectSpec]:
    return _read_from_cmake_result(project_dir).spec


def _read_from_cmake_result(project_dir: Path) -> ProjectReadResult:
    cmake = project_dir / "CMakeLists.txt"
    if not cmake.exists():
        return ProjectReadResult(spec=None)
    try:
        text = cmake.read_text(encoding="utf-8")
    except OSError:
        return ProjectReadResult(spec=None)
    values, missing_labels = _parse_cmakelists(text)
    if values is None or missing_labels:
        return ProjectReadResult(spec=None, missing_fields=tuple(missing_labels))
    values["destinationDir"] = normalize_portable_path(str(project_dir.parent))
    values.update(_parse_build_settings(project_dir))
    return ProjectReadResult(spec=ProjectSpec.from_dict(values))


def _parse_cmakelists(text: str) -> tuple[Optional[dict], list[str]]:
    project = _PROJECT_RE.search(text)
    if not project:
        return None, []
    values = _collect_cmake_values(text, project)
    missing = _missing_required_fields(values)
    if not _IS_SYNTH_RE.search(text):
        missing.append("Plugin Type")
    return values, missing


def _collect_cmake_values(text: str, project: re.Match) -> dict:
    values = {
        "projectName": project.group(1),
        "projectVersion": project.group(2),
        "pluginFormats": _read_formats(text),
        "pluginType": _read_type(text),
        "cxxStandard": _read_cxx(text),
        "headerSearchPaths": _read_header_paths(text),
        "preprocessorDefinitions": _read_preproc(text),
    }
    values.update(_quoted_fields(text))
    return values


def _missing_required_fields(values: dict) -> list[str]:
    missing = []
    for key in _REQUIRED_CMAKE_KEYS:
        value = values.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(_FIELD_LABELS[key])
    return missing


def _read_cxx(text: str) -> Optional[str]:
    match = _CXX_RE.search(text)
    return f"C++{match.group(1)}" if match else None


def _read_header_paths(text: str) -> str:
    match = _INCLUDE_RE.search(text)
    return _block_lines(match.group(1)) if match else ""


def _read_preproc(text: str) -> str:
    for body in _DEFS_RE.findall(text):
        if "JUCE_WEB_BROWSER" not in body:
            return _block_lines(body)
    return ""


def _block_lines(body: str) -> str:
    return "\n".join(line.strip() for line in body.splitlines() if line.strip())


def _quoted_fields(text: str) -> dict:
    vars_map = _parse_set_vars(text)
    found = {}
    for key, name in _QUOTED_FIELDS.items():
        if name in vars_map and vars_map[name]:
            found[key] = vars_map[name]
            continue
        value = _parse_quoted_field(text, name)
        if value is not None:
            found[key] = value
    return found


def _parse_quoted_field(text: str, name: str) -> Optional[str]:
    match = re.search(rf'\b{re.escape(name)}\s+("(?:[^"\\]|\\.)*")', text)
    if not match:
        return None
    value = match.group(1)
    return value[1:-1].replace('\\"', '"')


def _read_formats(text: str) -> str:
    match = _FORMATS_RE.search(text)
    return match.group(1).strip() if match else ""


def _read_type(text: str) -> str:
    return plugin_settings.type_for_flags(
        _flag(text, "IS_SYNTH"), _flag(text, "IS_MIDI_EFFECT")
    )


def _flag(text: str, name: str) -> str:
    match = re.search(rf"\b{name}\s+(TRUE|FALSE)\b", text)
    return match.group(1) if match else "FALSE"


def _parse_build_settings(project_dir: Path) -> dict:
    config = project_dir / "project-configuration.cmake"
    source = config if config.exists() else project_dir / "CMakeLists.txt"
    if not source.exists():
        return {}
    cfg = _parse_set_vars(source.read_text(encoding="utf-8"))
    return {
        "copyToSystemFolders": _bool(cfg, "USER_COPY_TO_SYSTEM_FOLDERS", "COPY_TO_SYSTEM_FOLDERS"),
        "copyToArtefactsDir": _bool(cfg, "USER_COPY_TO_ARTEFACTS_DIR", "COPY_TO_ARTEFACTS_DIR"),
        "artefactsDirWindows": cfg.get("ARTEFACTS_DIR_WINDOWS", ""),
        "artefactsDirMacos": cfg.get("ARTEFACTS_DIR_MACOS", ""),
        "artefactsDirLinux": cfg.get("ARTEFACTS_DIR_LINUX", ""),
    }


def _parse_set_vars(text: str) -> dict:
    result = {}
    for match in _SET_RE.finditer(text):
        name, value = match.group(1), match.group(2)
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')
        result[name] = value
    return result


def _bool(cfg: dict, user_key: str, cache_key: str) -> bool:
    value = cfg.get(user_key, cfg.get(cache_key, "OFF"))
    return _coerce_bool(value, False)
