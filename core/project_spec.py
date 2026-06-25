from dataclasses import dataclass


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
    destination_dir: str = ""
    juce_dir: str = ""
    plugin_type: str = "Instrument"
    plugin_formats: str = ""
    cxx_standard: str = "C++17"
    preprocessor_definitions: str = ""
    header_search_paths: str = ""
    copy_to_system_folders: bool = False
    copy_to_artefacts_dir: bool = True
    artefacts_dir_windows: str = ""
    artefacts_dir_macos: str = ""
    artefacts_dir_linux: str = ""

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
            "destinationDir": self.destination_dir,
            "juceDir": self.juce_dir,
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
        }

    @classmethod
    def from_dict(cls, d):
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
            destination_dir=d.get("destinationDir", ""),
            juce_dir=d.get("juceDir", ""),
            plugin_type=d.get("pluginType", "Instrument"),
            plugin_formats=d.get("pluginFormats", ""),
            cxx_standard=d.get("cxxStandard", "C++17"),
            preprocessor_definitions=d.get("preprocessorDefinitions", ""),
            header_search_paths=d.get("headerSearchPaths", ""),
            copy_to_system_folders=d.get("copyToSystemFolders", False),
            copy_to_artefacts_dir=d.get("copyToArtefactsDir", True),
            artefacts_dir_windows=d.get("artefactsDirWindows", ""),
            artefacts_dir_macos=d.get("artefactsDirMacos", ""),
            artefacts_dir_linux=d.get("artefactsDirLinux", ""),
        )
