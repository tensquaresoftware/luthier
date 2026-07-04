"""Unit tests for workspace path normalization and host resolution."""

import json
import sys

import pytest

from core.paths import host_workspace_field_key, normalize_path_dict_values
from core.preferences import Preferences, factory_defaults, validate_profile
from core.project_spec import ProjectSpec
from tests.conftest import make_spec


def _host_dest_key() -> str:
    return host_workspace_field_key("destination")


def _host_juce_key() -> str:
    return host_workspace_field_key("juce")


def test_host_resolution_matches_platform(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    spec = ProjectSpec(
        destination_dir_windows="C:/win",
        destination_dir_macos="/mac",
        destination_dir_linux="/linux",
        juce_dir_windows="C:/juce",
        juce_dir_macos="/juce/mac",
        juce_dir_linux="/juce/linux",
    )
    assert spec.host_destination_dir() == "/mac"
    assert spec.host_juce_dir() == "/juce/mac"

    monkeypatch.setattr(sys, "platform", "win32")
    assert spec.host_destination_dir() == "C:/win"
    assert spec.host_juce_dir() == "C:/juce"


def test_preferences_load_ignores_legacy_workspace_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "core.preferences.QStandardPaths.writableLocation",
        lambda *_args, **_kwargs: "/mock/Desktop",
    )
    path = tmp_path / "preferences.json"
    path.write_text(
        '{"destination": "/legacy/dest", "juceDir": "/Applications/JUCE", '
        '"manufacturer": "Acme Corp", "manufacturerCode": "Acme", "pluginCode": "Plug", '
        '"pluginType": "instrument", "pluginFormats": "VST3", "cxxStandard": "C++17"}',
        encoding="utf-8",
    )
    prefs = Preferences(path)
    prefs.load()
    assert prefs.get("manufacturer") == "Acme Corp"
    assert prefs.get(_host_dest_key()) == "/mock/Desktop"
    assert prefs.get(_host_juce_key()) == ""


def test_apply_profile_rejects_legacy_workspace_keys_only(tmp_path):
    path = tmp_path / "preferences.json"
    legacy = {
        "manufacturer": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destination": "/legacy/dest",
        "juceDir": "/Applications/JUCE",
        "pluginType": "instrument",
        "pluginFormats": "VST3",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "",
        "headerSearchPaths": "",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": False,
        "artefactsDirWindows": "",
        "artefactsDirMacos": "",
        "artefactsDirLinux": "",
    }
    prefs = Preferences(path)
    with pytest.raises(ValueError):
        prefs.apply_profile(legacy)


def test_validate_profile_allows_empty_non_host_destination():
    host_dest = _host_dest_key()
    host_juce = _host_juce_key()
    profile = {
        "manufacturer": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destinationDirWindows": "",
        "destinationDirMacos": "",
        "destinationDirLinux": "",
        "juceDirWindows": "",
        "juceDirMacos": "",
        "juceDirLinux": "",
        host_dest: "/tmp/projects",
        host_juce: "",
        "pluginType": "instrument",
        "pluginFormats": "VST3",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "",
        "headerSearchPaths": "",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": False,
        "artefactsDirWindows": "",
        "artefactsDirMacos": "",
        "artefactsDirLinux": "",
    }
    ok, message = validate_profile(profile)
    assert ok, message


def test_validate_profile_import_allows_empty_host_destination(monkeypatch):
    """Linux export imported on macOS may leave host destination empty."""
    monkeypatch.setattr("core.paths.sys.platform", "darwin")
    profile = {
        "manufacturer": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destinationDirWindows": "",
        "destinationDirMacos": "",
        "destinationDirLinux": "/home/user/projects",
        "juceDirWindows": "",
        "juceDirMacos": "",
        "juceDirLinux": "/home/user/Dev/SDKs/JUCE",
        "pluginType": "instrument",
        "pluginFormats": "VST3",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "",
        "headerSearchPaths": "",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": False,
        "artefactsDirWindows": "",
        "artefactsDirMacos": "",
        "artefactsDirLinux": "",
    }
    ok, message = validate_profile(profile, require_host_destination=False)
    assert ok, message


def test_validate_profile_import_still_requires_host_destination_for_auto_save(monkeypatch):
    monkeypatch.setattr("core.paths.sys.platform", "darwin")
    profile = {
        "manufacturer": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destinationDirWindows": "",
        "destinationDirMacos": "",
        "destinationDirLinux": "/home/user/projects",
        "juceDirWindows": "",
        "juceDirMacos": "",
        "juceDirLinux": "",
        "pluginType": "instrument",
        "pluginFormats": "VST3",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "",
        "headerSearchPaths": "",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": False,
        "artefactsDirWindows": "",
        "artefactsDirMacos": "",
        "artefactsDirLinux": "",
    }
    ok, message = validate_profile(profile, require_host_destination=True)
    assert not ok
    assert message == "Destination is required."


def test_apply_profile_import_accepts_cross_platform_export(tmp_path, monkeypatch):
    monkeypatch.setattr("core.paths.sys.platform", "darwin")
    prefs = Preferences(tmp_path / "preferences.json")
    profile = {
        "manufacturer": "Studio Linux",
        "manufacturerCode": "Linu",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destinationDirWindows": "",
        "destinationDirMacos": "",
        "destinationDirLinux": "/home/user/projects",
        "juceDirWindows": "",
        "juceDirMacos": "",
        "juceDirLinux": "/home/user/Dev/SDKs/JUCE",
        "pluginType": "instrument",
        "pluginFormats": "VST3 Standalone",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "",
        "headerSearchPaths": "",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": False,
        "artefactsDirWindows": "",
        "artefactsDirMacos": "",
        "artefactsDirLinux": "",
    }
    prefs.apply_profile(profile, require_host_destination=False)
    assert prefs.get("destinationDirLinux") == "/home/user/projects"
    assert prefs.get("destinationDirMacos") == ""


def test_round_trip_six_workspace_keys_in_sidecar(tmp_path):
    from tests.conftest import generate_project

    spec = make_spec(
        tmp_path,
        destination_dir_windows=str(tmp_path / "dest" / "win"),
        destination_dir_macos=str(tmp_path / "dest" / "mac"),
        destination_dir_linux=str(tmp_path / "dest" / "linux"),
        juce_dir_windows=str(tmp_path / "juce" / "win"),
        juce_dir_macos=str(tmp_path / "juce" / "mac"),
        juce_dir_linux=str(tmp_path / "juce" / "linux"),
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    for key in (
        "destinationDirWindows", "destinationDirMacos", "destinationDirLinux",
        "juceDirWindows", "juceDirMacos", "juceDirLinux",
    ):
        assert data[key] == spec.to_dict()[key]


def test_factory_defaults_sets_host_destination_only(monkeypatch):
    monkeypatch.setattr(
        "core.preferences.QStandardPaths.writableLocation",
        lambda *_args, **_kwargs: "/mock/Desktop",
    )
    defaults = factory_defaults()
    host_dest = _host_dest_key()
    assert defaults[host_dest] == "/mock/Desktop"
    for key in (
        "destinationDirWindows", "destinationDirMacos", "destinationDirLinux",
        "juceDirWindows", "juceDirMacos", "juceDirLinux",
    ):
        if key != host_dest:
            assert defaults[key] == ""


def test_normalize_path_dict_values_normalizes_slashes():
    out = normalize_path_dict_values({
        "artefactsDirWindows": r"C:\team\out",
        _host_dest_key(): r"C:\projects",
    })
    assert out["artefactsDirWindows"] == "C:/team/out"
    assert out[_host_dest_key()] == "C:/projects"
