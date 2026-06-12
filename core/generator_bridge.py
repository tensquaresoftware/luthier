"""Bridge to the JUCE Project Generator.

Adds the generator repository to sys.path and reuses its pipeline
(ConfigLoader, TemplateLoader, TemplateRenderer, FileGenerator) instead of
duplicating it. The generator stays the single source of truth; Luthier only
replaces its interactive InputCollector with the GUI form.
"""

import sys
from pathlib import Path
from typing import Optional

from core import plugin_settings

_DEV_GENERATOR_ROOT = Path(
    "/Volumes/Guillaume/Dev/SDKs/JUCE/Tools/Juce-Project-Generator"
)


def default_generator_root() -> Path:
    """Bundled copy when frozen (PyInstaller), the dev checkout otherwise."""
    bundle = getattr(sys, "_MEIPASS", None)
    return Path(bundle) / "generator" if bundle else _DEV_GENERATOR_ROOT


_FORM_FIELDS = (
    "projectName",
    "projectDisplayName",
    "projectVersion",
    "manufacturerName",
    "manufacturerCode",
    "pluginCode",
    "destinationDir",
)


class GeneratorBridge:
    """Loads the generator on demand and runs its generation pipeline."""

    def __init__(self, generator_root: Optional[Path] = None):
        self._root = Path(generator_root) if generator_root else default_generator_root()
        self._api: Optional[dict] = None
        self.load_error: Optional[str] = None

    @property
    def root(self) -> Path:
        return self._root

    @property
    def is_loaded(self) -> bool:
        return self._api is not None

    def ensure_loaded(self) -> bool:
        if self._api is not None:
            return True
        try:
            self._api = self._import_generator()
            self.load_error = None
        except Exception as error:
            self.load_error = str(error)
        return self._api is not None

    def load_defaults(self) -> dict:
        loader = self._api["ConfigLoader"](self._root)
        return loader.loadAll()

    def make_bundle_id(self, manufacturer_name: str, project_name: str) -> str:
        if not self.is_loaded:
            return ""
        return self._api["generateBundleId"](manufacturer_name, project_name)

    def project_exists(self, destination: str, project_name: str) -> bool:
        return (Path(destination) / project_name).exists()

    def generate(self, values: dict, config: dict) -> Path:
        data = self._build_project_data(values)
        self._run_pipeline(data, config)
        return data.projectDir

    def _import_generator(self) -> dict:
        if not (self._root / "Generator").is_dir():
            raise FileNotFoundError(f"Generator not found at {self._root}")
        if str(self._root) not in sys.path:
            sys.path.insert(0, str(self._root))
        import Generator  # registers hyphenated modules in sys.modules
        import pluginCategories

        return {
            "ConfigLoader": Generator.ConfigLoader,
            "FileGenerator": Generator.FileGenerator,
            "TemplateLoader": Generator.TemplateLoader,
            "TemplateRenderer": Generator.TemplateRenderer,
            "ProjectData": Generator.ProjectData,
            "generateBundleId": pluginCategories.generateBundleId,
            "updateAuAndVst3Categories": pluginCategories.updateAuAndVst3Categories,
        }

    def _build_project_data(self, values: dict):
        data = self._api["ProjectData"]()
        for field in _FORM_FIELDS:
            setattr(data, field, values[field])
        data.projectDir = Path(values["destinationDir"]) / data.projectName
        data.bundleId = self.make_bundle_id(data.manufacturerName, data.projectName)
        self._apply_plugin_settings(data, values)
        return data

    def _apply_plugin_settings(self, data, values: dict) -> None:
        for key, flag in plugin_settings.flags_for_type(values["pluginType"]).items():
            setattr(data, key, flag)
        update = self._api["updateAuAndVst3Categories"]
        data.auMainType, data.vst3Categories = update(data.isSynth, data.isMidiEffect)
        data.pluginFormats = values["pluginFormats"]

    def _run_pipeline(self, data, config: dict) -> None:
        templates_dir = self._root / "Templates"
        loader = self._api["TemplateLoader"](templates_dir)
        renderer = self._api["TemplateRenderer"](data, config)
        generator = self._api["FileGenerator"](
            loader, data.projectDir, data, renderer, self._root
        )
        generator.generateAll()
