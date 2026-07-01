"""Unit tests for project form seeding and dirty-state comparison (Story 5.5)."""

from core.paths import host_workspace_field_key
from core.plugin_settings import TYPE_AUDIO_EFFECT, TYPE_INSTRUMENT
from core.preferences import Preferences
from core.project_form_state import form_snapshots_equal, new_project_seed
from core.project_spec import ProjectSpec


def _profile_seed(**overrides) -> dict:
    host_dest = host_workspace_field_key("destination")
    host_juce = host_workspace_field_key("juce")
    data = {
        "manufacturerName": "Acme Corp",
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
        host_juce: "/Applications/JUCE",
        "pluginType": TYPE_INSTRUMENT,
        "pluginFormats": "AU VST3 Standalone",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "FOO=1",
        "headerSearchPaths": "/include",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": True,
        "artefactsDirWindows": "C:\\artefacts",
        "artefactsDirMacos": "/artefacts",
        "artefactsDirLinux": "/artefacts",
        "manufacturer": "Acme Corp",
    }
    data.update(overrides)
    return data


def test_new_project_seed_clears_identity_preserves_profile_fields():
    host_juce = host_workspace_field_key("juce")
    seed = new_project_seed(_profile_seed())
    assert seed["projectName"] == ""
    assert seed["projectDisplayName"] == ""
    assert seed["projectVersion"] == "1.0.0"
    assert seed["pluginType"] == TYPE_INSTRUMENT
    assert seed["pluginFormats"] == "AU VST3 Standalone"
    assert seed[host_juce] == "/Applications/JUCE"
    assert seed["cxxStandard"] == "C++17"
    assert seed["preprocessorDefinitions"] == "FOO=1"


def test_form_snapshots_equal_detects_field_change():
    baseline = ProjectSpec(plugin_type=TYPE_INSTRUMENT).to_dict()
    current = dict(baseline)
    current["pluginType"] = TYPE_AUDIO_EFFECT
    assert not form_snapshots_equal(baseline, current)


def test_form_snapshots_equal_ignores_display_name_fallback():
    """Empty display name matches project name after ProjectInfoPage normalization."""
    baseline = ProjectSpec(
        project_name="MyPlugin",
        project_display_name="MyPlugin",
    ).to_dict()
    current = ProjectSpec(
        project_name="MyPlugin",
        project_display_name="",
    ).to_dict()
    assert form_snapshots_equal(baseline, current)


def test_load_project_clears_dirty_state():
    """After load (e.g. post-generate), the form should not appear unsaved."""
    baseline = ProjectSpec(project_name="MyPlugin", project_version="1.0.0").to_dict()
    edited = dict(baseline)
    edited["projectVersion"] = "1.0.1"
    assert not form_snapshots_equal(baseline, edited)
    assert form_snapshots_equal(edited, edited)


def test_create_new_project_seed_does_not_mutate_preferences_file(tmp_path):
    host_dest = host_workspace_field_key("destination")
    host_juce = host_workspace_field_key("juce")
    prefs_path = tmp_path / "preferences.json"
    prefs = Preferences(prefs_path)
    prefs.apply_profile({
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
        host_juce: "/Applications/JUCE",
        "pluginType": TYPE_INSTRUMENT,
        "pluginFormats": "AU VST3 Standalone",
        "cxxStandard": "C++17",
        "preprocessorDefinitions": "",
        "headerSearchPaths": "",
        "copyToSystemFolders": False,
        "copyToArtefactsDir": True,
        "artefactsDirWindows": "",
        "artefactsDirMacos": "",
        "artefactsDirLinux": "",
    })
    prefs.save()
    snapshot = prefs_path.read_bytes()
    snapshot_mtime = prefs_path.stat().st_mtime

    seed = new_project_seed(prefs.seed_dict())
    ProjectSpec.from_dict(seed)

    assert prefs_path.read_bytes() == snapshot
    assert prefs_path.stat().st_mtime == snapshot_mtime
