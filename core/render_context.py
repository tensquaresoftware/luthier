"""Build the str.format context that fills the project templates."""

from core import plugin_settings

_VALUE_KEYS = (
    "projectName",
    "projectDisplayName",
    "projectVersion",
    "manufacturerName",
    "manufacturerCode",
    "pluginCode",
    "pluginFormats",
)


def build_context(values: dict, config: dict) -> dict:
    flags = plugin_settings.flags_for_type(values["pluginType"])
    context = {key: values[key] for key in _VALUE_KEYS}
    context.update(flags)
    context.update(_categories(flags))
    context.update(_copy_config(config))
    context["bundleId"] = plugin_settings.bundle_id(
        values["manufacturerName"], values["projectName"]
    )
    context.update(_extra_fields(values))
    return context


def _categories(flags: dict) -> dict:
    au_main_type, vst3_categories = plugin_settings.au_and_vst3_categories(
        flags["isSynth"], flags["isMidiEffect"]
    )
    return {"auMainType": au_main_type, "vst3Categories": vst3_categories}


def _copy_config(config: dict) -> dict:
    return {
        "copyToSystemFolders": _on_off(config["copyToSystemFolders"]),
        "copyToArtefactsDir": _on_off(config["copyToArtefactsDir"]),
        "artefactsDirWindows": config["artefactsDirWindows"],
        "artefactsDirMacos": config["artefactsDirMacos"],
        "artefactsDirLinux": config["artefactsDirLinux"],
    }


def _on_off(enabled: bool) -> str:
    return "ON" if enabled else "OFF"


def build_tokens(values: dict) -> dict:
    """@KEY@ substitutions available to the (user-editable) source templates."""
    return {
        "PROJECT_NAME": values["projectName"],
        "PROJECT_DISPLAY_NAME": values["projectDisplayName"],
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
