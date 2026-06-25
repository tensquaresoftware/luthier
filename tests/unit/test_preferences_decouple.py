"""Tests that Open/Generate workflows do not modify preferences.json."""

import json

from core.app_state import AppState
from core.preferences import Preferences
from core.project_spec import ProjectSpec


def _valid_profile(**overrides) -> dict:
    data = {
        "manufacturer": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destination": "/tmp/prefs-dest",
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


def test_preferences_file_unchanged_after_simulated_open_generate_workflow(tmp_path):
    """Simulate post-5.4 MainWindow: load project + remember parent without prefs writes."""
    prefs_path = tmp_path / "preferences.json"
    state_path = tmp_path / "app_state.json"
    prefs = Preferences(prefs_path)
    prefs.apply_profile(_valid_profile())
    prefs.save()
    snapshot = prefs_path.read_bytes()
    snapshot_mtime = prefs_path.stat().st_mtime

    project_dest = tmp_path / "project-dest"
    project_dest.mkdir()
    spec = ProjectSpec.from_dict({
        **prefs.seed_dict(),
        "projectName": "TestPlugin",
        "projectDisplayName": "Test Plugin",
        "projectVersion": "1.0.0",
        "destinationDir": str(project_dest),
    })

    loaded = Preferences(prefs_path)
    loaded.load()
    assert loaded.to_dict() == prefs.to_dict()
    assert spec.project_name == "TestPlugin"

    state = AppState(state_path)
    state.remember_parent(spec.destination_dir)
    state.save()

    assert prefs_path.read_bytes() == snapshot
    assert prefs_path.stat().st_mtime == snapshot_mtime
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_data["lastUsedParentDir"] == str(project_dest.resolve())


def test_preferences_has_no_update_method():
    assert "update" not in Preferences.__dict__
