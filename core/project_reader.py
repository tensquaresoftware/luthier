"""Reads a generated project back into form values.

Project identity lives in CMakeLists.txt (the juce_add_plugin block); build
settings live in project-configuration.cmake. The set() parsing mirrors the
generator's projectConfigParser; the juce_add_plugin fields need their own
regexes since no existing parser covers them.
"""

import re
from pathlib import Path
from typing import Optional

from core import plugin_settings

_PROJECT_RE = re.compile(r"project\(\s*(\S+)\s+VERSION\s+([^\s)]+)")
_FORMATS_RE = re.compile(r"set\(\s*PLUGIN_FORMATS_LIST\s+([^)]*)\)")
_SET_RE = re.compile(r'set\s*\(\s*(\w+)\s+("(?:[^"\\]|\\.)*"|[^\s)]+)')

_QUOTED_FIELDS = {
    "manufacturerName": "COMPANY_NAME",
    "manufacturerCode": "PLUGIN_MANUFACTURER_CODE",
    "pluginCode": "PLUGIN_CODE",
    "projectDisplayName": "PLUGIN_NAME",
}


def read_project(project_dir: Path) -> Optional[dict]:
    cmake = project_dir / "CMakeLists.txt"
    if not cmake.exists():
        return None
    values = _parse_cmakelists(cmake.read_text(encoding="utf-8"))
    if values is None:
        return None
    values["destinationDir"] = str(project_dir.parent)
    values.update(_parse_build_settings(project_dir))
    return values


def _parse_cmakelists(text: str) -> Optional[dict]:
    project = _PROJECT_RE.search(text)
    if not project:
        return None
    values = {
        "projectName": project.group(1),
        "projectVersion": project.group(2),
        "pluginFormats": _read_formats(text),
        "pluginType": _read_type(text),
    }
    values.update(_quoted_fields(text))
    return values


def _quoted_fields(text: str) -> dict:
    found = {}
    for key, name in _QUOTED_FIELDS.items():
        match = re.search(rf'\b{name}\s+"([^"]*)"', text)
        if match:
            found[key] = match.group(1)
    return found


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
    if not config.exists():
        return {}
    cfg = _parse_set_vars(config.read_text(encoding="utf-8"))
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
    return value.upper() in ("ON", "TRUE", "1", "YES")
