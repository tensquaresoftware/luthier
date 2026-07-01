"""Unit tests for workspace path migration and host resolution."""

import json
import sys

import pytest

from core.paths import host_workspace_field_key, migrate_workspace_keys, normalize_path_dict_values
from core.preferences import Preferences, factory_defaults, validate_profile
from core.project_reader import read_project_result
from core.project_spec import ProjectSpec
from tests.conftest import make_spec


def _host_dest_key() -> str:
    return host_workspace_field_key("destination")


def _host_juce_key() -> str:
    return host_workspace_field_key("juce")


def test_migrate_legacy_destination_to_host(tmp_path):
    legacy = {"destination": "/legacy/dest", "destinationDir": "/ignored"}
    migrated = migrate_workspace_keys(legacy)
    assert migrated[_host_dest_key()] == "/legacy/dest"
    assert "destination" not in migrated
    assert "destinationDir" not in migrated


def test_migrate_whitespace_destination_falls_back_to_destination_dir():
    migrated = migrate_workspace_keys({
        "destination": "   ",
        "destinationDir": "/real/path",
    })
    assert migrated[_host_dest_key()] == "/real/path"


def test_migrate_legacy_juce_to_host():
    migrated = migrate_workspace_keys({"juceDir": "/Applications/JUCE"})
    assert migrated[_host_juce_key()] == "/Applications/JUCE"
    assert "juceDir" not in migrated


def test_migrate_does_not_overwrite_existing_host_values():
    host_dest = _host_dest_key()
    migrated = migrate_workspace_keys({
        "destination": "/legacy",
        host_dest: "/current",
    })
    assert migrated[host_dest] == "/current"


def test_project_spec_from_dict_migrates_legacy_keys():
    spec = ProjectSpec.from_dict({
        "destinationDir": "/projects/out",
        "juceDir": "/Applications/JUCE",
    })
    assert spec.host_destination_dir() == "/projects/out"
    assert spec.host_juce_dir() == "/Applications/JUCE"
    assert "destinationDir" not in spec.to_dict()
    assert "juceDir" not in spec.to_dict()


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


def test_preferences_load_migrates_legacy_file(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text(
        '{"destination": "/legacy/dest", "juceDir": "/Applications/JUCE", '
        '"manufacturer": "Acme Corp", "manufacturerCode": "Acme", "pluginCode": "Plug", '
        '"pluginType": "instrument", "pluginFormats": "VST3", "cxxStandard": "C++17"}',
        encoding="utf-8",
    )
    prefs = Preferences(path)
    prefs.load()
    assert prefs.get(_host_dest_key()) == "/legacy/dest"
    assert prefs.get(_host_juce_key()) == "/Applications/JUCE"
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert "destination" not in saved
    assert "juceDir" not in saved
    assert saved[_host_dest_key()] == "/legacy/dest"


def test_apply_profile_migrates_legacy_export_json(tmp_path):
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
    prefs.apply_profile(legacy)
    assert prefs.get(_host_dest_key()) == "/legacy/dest"
    assert prefs.get(_host_juce_key()) == "/Applications/JUCE"
    assert "destination" not in prefs.to_dict()
    assert "juceDir" not in prefs.to_dict()


def test_open_project_updates_host_destination_only(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    project_dir = tmp_path / "parent" / "MyPlugin"
    project_dir.mkdir(parents=True)
    sidecar = {
        "projectName": "MyPlugin",
        "pluginFormats": "VST3",
        "pluginType": "instrument",
        "destinationDirWindows": "C:/win",
        "destinationDirMacos": "/old/mac",
        "destinationDirLinux": "/linux",
        "juceDirWindows": "C:/juce",
        "juceDirMacos": "/juce/mac",
        "juceDirLinux": "/juce/linux",
    }
    import json
    (project_dir / ".luthier.json").write_text(json.dumps(sidecar), encoding="utf-8")
    result = read_project_result(project_dir)
    assert result.spec is not None
    assert result.spec.destination_dir_macos == str(project_dir.parent)
    assert result.spec.destination_dir_windows == "C:/win"
    assert result.spec.juce_dir_macos == "/juce/mac"


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


def test_normalize_path_dict_values_migrates_and_normalizes():
    out = normalize_path_dict_values({
        "destination": r"C:\legacy",
        "artefactsDirWindows": r"C:\team\out",
    })
    assert out[_host_dest_key()] == "C:/legacy"
    assert out["artefactsDirWindows"] == "C:/team/out"
    assert "destination" not in out
