"""Build the str.format context that fills the project templates."""

import json

from core import plugin_settings
from core.paths import normalize_portable_path
from core.project_spec import ProjectSpec

_VALUE_KEYS = (
    "projectName",
    "projectDisplayName",
    "projectVersion",
    "manufacturerName",
    "manufacturerCode",
    "pluginCode",
    "pluginFormats",
)


def _cmake_quoted(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    return f'"{escaped}"'


def characteristics_cmake_context(spec: ProjectSpec) -> dict:
    to_cmake = plugin_settings._bool_to_cmake
    return {
        "isSynth": to_cmake(spec.is_synth),
        "isMidiEffect": to_cmake(spec.is_midi_effect),
        "needsMidiInput": to_cmake(spec.needs_midi_input),
        "needsMidiOutput": to_cmake(spec.needs_midi_output),
        "editorWantsKeyboardFocus": to_cmake(spec.editor_wants_keyboard_focus),
        "pluginDescription": _cmake_quoted(spec.plugin_description or ""),
        "vstNumMidiIns": str(spec.vst_num_midi_ins),
        "vstNumMidiOuts": str(spec.vst_num_midi_outs),
    }


def build_context(spec: ProjectSpec) -> dict:
    d = spec.to_dict()
    flags = characteristics_cmake_context(spec)
    context = {key: d[key] for key in _VALUE_KEYS}
    context.update(flags)
    context.update(_categories(flags))
    context.update(_copy_config(d))
    context.update(_artefact_entries(d))
    context.update(_juce_workspace_paths(d))
    context["bundleId"] = plugin_settings.bundle_id(d["manufacturerName"], d["projectName"])
    context.update(_extra_fields(d))
    return context


def _juce_workspace_paths(config: dict) -> dict:
    return {
        "juceDirWindows": _cmake_path_value(config.get("juceDirWindows", "")),
        "juceDirMacos": _cmake_path_value(config.get("juceDirMacos", "")),
        "juceDirLinux": _cmake_path_value(config.get("juceDirLinux", "")),
    }


def _categories(flags: dict) -> dict:
    au_main_type, vst3_categories = plugin_settings.au_and_vst3_categories(
        flags["isSynth"], flags["isMidiEffect"]
    )
    return {"auMainType": au_main_type, "vst3Categories": vst3_categories}


def _copy_config(config: dict) -> dict:
    return {
        "copyToSystemFolders": _on_off(config["copyToSystemFolders"]),
        "copyToArtefactsDir": _on_off(config["copyToArtefactsDir"]),
        "artefactsDirWindows": _cmake_path_value(config["artefactsDirWindows"]),
        "artefactsDirMacos": _cmake_path_value(config["artefactsDirMacos"]),
        "artefactsDirLinux": _cmake_path_value(config["artefactsDirLinux"]),
    }


def _cmake_path_value(path: str) -> str:
    normalized = normalize_portable_path(path or "")
    if not normalized:
        return '""'
    return _cmake_quoted(normalized)


def _on_off(enabled: bool) -> str:
    return "ON" if enabled else "OFF"


def _artefact_entries(d: dict) -> dict:
    enabled = d["copyToArtefactsDir"]
    return {
        "macosArtefactEntry": _artefact_entry(enabled, "ARTEFACTS_DIR_MACOS", d.get("artefactsDirMacos", "")),
        "windowsArtefactEntry": _artefact_entry(enabled, "ARTEFACTS_DIR_WINDOWS", d.get("artefactsDirWindows", "")),
        "linuxArtefactEntry": _artefact_entry(enabled, "ARTEFACTS_DIR_LINUX", d.get("artefactsDirLinux", "")),
    }


def _artefact_entry(enabled: bool, key: str, path: str) -> str:
    if not enabled or not path or not str(path).strip():
        return ""
    normalized = normalize_portable_path(path)
    if not normalized.strip():
        return ""
    fragment = json.dumps({key: normalized}, ensure_ascii=False)
    inner = fragment[1:-1]
    return f",\n        {inner}"


def build_tokens(spec: ProjectSpec) -> dict:
    """@KEY@ substitutions available to the (user-editable) source templates."""
    return {
        "PROJECT_NAME": spec.project_name,
        "PROJECT_DISPLAY_NAME": spec.project_display_name,
        "CREATE_BUSES_PROPERTIES_BODY": plugin_settings.buses_properties_body(
            spec.is_synth, spec.is_midi_effect, spec.audio_io_preset
        ),
    }


def _extra_fields(values: dict) -> dict:
    return {
        "cxxStandard": (values.get("cxxStandard") or "C++17").replace("C++", ""),
        "companyCopyright": values.get("companyCopyright", ""),
        "companyWebsite": values.get("companyWebsite", ""),
        "companyEmail": values.get("companyEmail", ""),
        "headerSearchPathsBlock": _include_block(values),
        "extraDefinitionsBlock": _definitions_block(values),
    }


def _include_block(values: dict) -> str:
    paths = _non_empty_lines(values.get("headerSearchPaths", ""))
    opening = f"target_include_directories({values['projectName']}\n    PRIVATE"
    return _cmake_block(opening, paths)


def _definitions_block(values: dict) -> str:
    defs = _non_empty_lines(values.get("preprocessorDefinitions", ""))
    opening = f"target_compile_definitions({values['projectName']}\n    PUBLIC"
    return _cmake_block(opening, defs)


def _cmake_block(opening: str, items: list) -> str:
    if not items:
        return ""
    body = "\n".join(f"        {item}" for item in items)
    return f"\n\n{opening}\n{body}\n)"


def _non_empty_lines(text: str) -> list:
    return [line.strip() for line in text.splitlines() if line.strip()]
