"""Unit tests for AppState last-used parent persistence."""

import json
from pathlib import Path
from unittest.mock import patch

from core.app_state import AppState
from core.preferences import Preferences


def test_remember_parent_persists_to_file(tmp_path):
    state_path = tmp_path / "app_state.json"
    state = AppState(state_path)
    dest = tmp_path / "projects"
    dest.mkdir()
    state.remember_parent(str(dest))
    state.save()
    data = json.loads(state_path.read_text(encoding="utf-8"))
    assert data["lastUsedParentDir"] == str(dest.resolve())


def test_dialog_start_dir_prefers_field_value_when_valid(tmp_path):
    field_dir = tmp_path / "field"
    field_dir.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    state = AppState(tmp_path / "app_state.json")
    state.remember_parent(str(other))
    assert state.dialog_start_dir(str(field_dir)) == str(field_dir.resolve())


def test_dialog_start_dir_uses_last_parent_when_field_empty(tmp_path):
    parent = tmp_path / "last-parent"
    parent.mkdir()
    state = AppState(tmp_path / "app_state.json")
    state.remember_parent(str(parent))
    assert state.dialog_start_dir("") == str(parent.resolve())


def test_dialog_start_dir_falls_back_to_desktop_when_parent_invalid(tmp_path):
    state = AppState(tmp_path / "app_state.json")
    state._data["lastUsedParentDir"] = "/nonexistent/path"
    with patch(
        "core.app_state.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        assert state.dialog_start_dir("") == "/mock/Desktop"


def test_dialog_start_dir_falls_back_to_home_when_desktop_empty(tmp_path):
    state = AppState(tmp_path / "app_state.json")
    with patch(
        "core.app_state.QStandardPaths.writableLocation",
        return_value="",
    ):
        assert state.dialog_start_dir("") == str(Path.home())


def test_app_state_save_does_not_touch_preferences_json(tmp_path):
    prefs_path = tmp_path / "preferences.json"
    state_path = tmp_path / "app_state.json"
    prefs = Preferences(prefs_path)
    prefs.apply_profile({
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
    })
    prefs.save()
    before = prefs_path.read_bytes()
    before_mtime = prefs_path.stat().st_mtime

    dest = tmp_path / "generated"
    dest.mkdir()
    state = AppState(state_path)
    state.remember_parent(str(dest))
    state.save()

    assert state_path.exists()
    assert prefs_path.read_bytes() == before
    assert prefs_path.stat().st_mtime == before_mtime


def test_app_state_default_path_is_sibling_of_preferences(tmp_path):
    with patch.object(Preferences, "default_path", return_value=tmp_path / "preferences.json"):
        assert AppState.default_path() == tmp_path / "app_state.json"
