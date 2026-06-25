"""Unit tests for Preferences profile API."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from core.preferences import Preferences, factory_defaults, validate_profile


def _valid_profile(**overrides) -> dict:
    data = {
        "manufacturer": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destination": "/tmp/projects",
        "juceDir": "",
        "pluginType": "synth",
        "pluginFormats": "AU VST3 Standalone",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "",
        "headerSearchPaths": "",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": False,
        "artefactsDirWindows": "",
        "artefactsDirMacos": "",
        "artefactsDirLinux": "",
    }
    data.update(overrides)
    return data


def test_factory_defaults_include_extended_schema():
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        defaults = factory_defaults()
    assert defaults["destination"] == "/mock/Desktop"
    assert defaults["pluginType"] == "synth"
    assert defaults["pluginFormats"] == "AU VST3 Standalone"
    assert defaults["cxxStandard"] == "C++17"
    assert defaults["preprocessorDefinitions"] == ""
    assert defaults["headerSearchPaths"] == ""
    assert defaults["copyToArtefactsDir"] is False


def test_factory_defaults_falls_back_when_desktop_empty():
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="",
    ):
        defaults = factory_defaults()
    assert defaults["destination"] == str(Path.home())


def test_ensure_initialized_creates_file_with_desktop_destination(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        prefs.ensure_initialized()
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["destination"] == "/mock/Desktop"
    assert data["pluginType"] == "synth"


def test_to_dict_apply_profile_round_trip(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    profile = _valid_profile(destination="/projects/out", pluginType="effect")
    prefs.apply_profile(profile)
    prefs.save()
    reloaded = Preferences(path)
    reloaded.load()
    assert reloaded.to_dict() == prefs.to_dict()
    assert reloaded.get("pluginType") == "effect"
    assert reloaded.get("destination") == "/projects/out"


def test_apply_profile_rejects_invalid_plugin_formats(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    profile = _valid_profile(pluginFormats="")
    with pytest.raises(ValueError, match="at least one"):
        prefs.apply_profile(profile)


def test_apply_profile_rejects_unknown_format_token(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    profile = _valid_profile(pluginFormats="VST2")
    with pytest.raises(ValueError, match="AU, VST3"):
        prefs.apply_profile(profile)


def test_apply_profile_fills_missing_keys_from_defaults(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile(copyToArtefactsDir=True))
    partial = _valid_profile(copyToArtefactsDir=False)
    del partial["copyToArtefactsDir"]
    prefs.apply_profile(partial)
    assert prefs.get("copyToArtefactsDir") is False


def test_import_validation_preserves_existing_on_failure(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.apply_profile(_valid_profile(manufacturer="Keep Me"))
    prefs.save()
    before = prefs.to_dict()
    ok, _ = validate_profile(_valid_profile(pluginFormats=""))
    assert not ok
    prefs.apply_profile(before)
    assert prefs.to_dict() == before


def test_seed_dict_maps_project_form_keys(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile(
        manufacturer="Seed Co",
        destination="/seed/dest",
        pluginFormats="VST3",
    ))
    seed = prefs.seed_dict()
    assert seed["manufacturerName"] == "Seed Co"
    assert seed["destinationDir"] == "/seed/dest"
    assert seed["pluginFormats"] == "VST3"
    assert seed["manufacturer"] == "Seed Co"
    assert seed["destination"] == "/seed/dest"


def test_seed_dict_round_trips_through_project_spec(tmp_path):
    from core.project_spec import ProjectSpec

    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile(
        destination="/seed/dest",
        juceDir="/Applications/JUCE",
        pluginType="effect",
        pluginFormats="AU VST3",
        cxxStandard="C++20",
    ))
    seed = {
        **prefs.seed_dict(),
        "projectName": "",
        "projectDisplayName": "",
        "projectVersion": "1.0.0",
    }
    spec = ProjectSpec.from_dict(seed)
    assert spec.destination_dir == "/seed/dest"
    assert spec.juce_dir == "/Applications/JUCE"
    assert spec.plugin_type == "effect"
    assert spec.plugin_formats == "AU VST3"
    assert spec.cxx_standard == "C++20"
