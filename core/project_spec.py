from dataclasses import dataclass

from core.paths import host_workspace_field_key, normalize_path_dict_values
from core.plugin_settings import TYPE_INSTRUMENT, clamp_midi_count, normalize_audio_io_preset


def _coerce_bool(value, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        upper = value.strip().upper()
        if upper in ("ON", "TRUE", "1", "YES"):
            return True
        if upper in ("OFF", "FALSE", "0", "NO"):
            return False
        return default
    return default


@dataclass
class ProjectSpec:
    project_name: str = ""
    project_display_name: str = ""
    project_version: str = "1.0.0"
    manufacturer_name: str = ""
    manufacturer_code: str = ""
    plugin_code: str = ""
    company_copyright: str = ""
    company_website: str = ""
    company_email: str = ""
    destination_dir_windows: str = ""
    destination_dir_macos: str = ""
    destination_dir_linux: str = ""
    juce_dir_windows: str = ""
    juce_dir_macos: str = ""
    juce_dir_linux: str = ""
    plugin_type: str = TYPE_INSTRUMENT
    plugin_formats: str = ""
    cxx_standard: str = "C++17"
    preprocessor_definitions: str = ""
    header_search_paths: str = ""
    copy_to_system_folders: bool = False
    copy_to_artefacts_dir: bool = True
    artefacts_dir_windows: str = ""
    artefacts_dir_macos: str = ""
    artefacts_dir_linux: str = ""
    needs_midi_input: bool = True
    needs_midi_output: bool = False
    is_synth: bool = True
    is_midi_effect: bool = False
    editor_wants_keyboard_focus: bool = False
    plugin_description: str = ""
    audio_io_preset: str = "stereo"
    vst_num_midi_ins: int = 16
    vst_num_midi_outs: int = 16

    def host_destination_dir(self) -> str:
        key = host_workspace_field_key("destination")
        return self._workspace_value(key)

    def host_juce_dir(self) -> str:
        key = host_workspace_field_key("juce")
        return self._workspace_value(key)

    def _workspace_value(self, key: str) -> str:
        mapping = {
            "destinationDirWindows": self.destination_dir_windows,
            "destinationDirMacos": self.destination_dir_macos,
            "destinationDirLinux": self.destination_dir_linux,
            "juceDirWindows": self.juce_dir_windows,
            "juceDirMacos": self.juce_dir_macos,
            "juceDirLinux": self.juce_dir_linux,
        }
        return str(mapping.get(key, "") or "").strip()

    def to_dict(self):
        return {
            "projectName": self.project_name,
            "projectDisplayName": self.project_display_name,
            "projectVersion": self.project_version,
            "manufacturerName": self.manufacturer_name,
            "manufacturerCode": self.manufacturer_code,
            "pluginCode": self.plugin_code,
            "companyCopyright": self.company_copyright,
            "companyWebsite": self.company_website,
            "companyEmail": self.company_email,
            "destinationDirWindows": self.destination_dir_windows,
            "destinationDirMacos": self.destination_dir_macos,
            "destinationDirLinux": self.destination_dir_linux,
            "juceDirWindows": self.juce_dir_windows,
            "juceDirMacos": self.juce_dir_macos,
            "juceDirLinux": self.juce_dir_linux,
            "pluginType": self.plugin_type,
            "pluginFormats": self.plugin_formats,
            "cxxStandard": self.cxx_standard,
            "preprocessorDefinitions": self.preprocessor_definitions,
            "headerSearchPaths": self.header_search_paths,
            "copyToSystemFolders": self.copy_to_system_folders,
            "copyToArtefactsDir": self.copy_to_artefacts_dir,
            "artefactsDirWindows": self.artefacts_dir_windows,
            "artefactsDirMacos": self.artefacts_dir_macos,
            "artefactsDirLinux": self.artefacts_dir_linux,
            "needsMidiInput": self.needs_midi_input,
            "needsMidiOutput": self.needs_midi_output,
            "isSynth": self.is_synth,
            "isMidiEffect": self.is_midi_effect,
            "editorWantsKeyboardFocus": self.editor_wants_keyboard_focus,
            "pluginDescription": self.plugin_description,
            "audioIoPreset": self.audio_io_preset,
            "vstNumMidiIns": self.vst_num_midi_ins,
            "vstNumMidiOuts": self.vst_num_midi_outs,
        }

    @classmethod
    def from_dict(cls, d):
        d = normalize_path_dict_values(d)
        return cls(
            project_name=d.get("projectName", ""),
            project_display_name=d.get("projectDisplayName", ""),
            project_version=d.get("projectVersion", "1.0.0"),
            manufacturer_name=d.get("manufacturerName", ""),
            manufacturer_code=d.get("manufacturerCode", ""),
            plugin_code=d.get("pluginCode", ""),
            company_copyright=d.get("companyCopyright", ""),
            company_website=d.get("companyWebsite", ""),
            company_email=d.get("companyEmail", ""),
            destination_dir_windows=d.get("destinationDirWindows", ""),
            destination_dir_macos=d.get("destinationDirMacos", ""),
            destination_dir_linux=d.get("destinationDirLinux", ""),
            juce_dir_windows=d.get("juceDirWindows", ""),
            juce_dir_macos=d.get("juceDirMacos", ""),
            juce_dir_linux=d.get("juceDirLinux", ""),
            plugin_type=d.get("pluginType", TYPE_INSTRUMENT),
            plugin_formats=d.get("pluginFormats", ""),
            cxx_standard=d.get("cxxStandard", "C++17"),
            preprocessor_definitions=d.get("preprocessorDefinitions", ""),
            header_search_paths=d.get("headerSearchPaths", ""),
            copy_to_system_folders=_coerce_bool(d.get("copyToSystemFolders"), False),
            copy_to_artefacts_dir=_coerce_bool(d.get("copyToArtefactsDir"), True),
            artefacts_dir_windows=d.get("artefactsDirWindows", ""),
            artefacts_dir_macos=d.get("artefactsDirMacos", ""),
            artefacts_dir_linux=d.get("artefactsDirLinux", ""),
            needs_midi_input=_coerce_bool(d.get("needsMidiInput"), True),
            needs_midi_output=_coerce_bool(d.get("needsMidiOutput"), False),
            is_synth=_coerce_bool(d.get("isSynth"), True),
            is_midi_effect=_coerce_bool(d.get("isMidiEffect"), False),
            editor_wants_keyboard_focus=_coerce_bool(
                d.get("editorWantsKeyboardFocus"), False
            ),
            plugin_description=d.get("pluginDescription", ""),
            audio_io_preset=normalize_audio_io_preset(d.get("audioIoPreset", "stereo")),
            vst_num_midi_ins=clamp_midi_count(d.get("vstNumMidiIns"), 16),
            vst_num_midi_outs=clamp_midi_count(d.get("vstNumMidiOuts"), 16),
        )
