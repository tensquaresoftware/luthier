"""Unit tests for project form seeding and dirty-state comparison (Story 5.5)."""

from core.plugin_settings import TYPE_AUDIO_EFFECT, TYPE_INSTRUMENT
from core.preferences import Preferences
from core.project_form_state import form_snapshots_equal, new_project_seed
from core.project_spec import ProjectSpec


def _profile_seed(**overrides) -> dict:
    data = {
        "manufacturerName": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destinationDir": "/tmp/projects",
        "juceDir": "/Applications/JUCE",
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
        "destination": "/tmp/projects",
    }
    data.update(overrides)
    return data


def test_new_project_seed_clears_identity_preserves_profile_fields():
    seed = new_project_seed(_profile_seed())
    assert seed["projectName"] == ""
    assert seed["projectDisplayName"] == ""
    assert seed["projectVersion"] == "1.0.0"
    assert seed["pluginType"] == TYPE_INSTRUMENT
    assert seed["pluginFormats"] == "AU VST3 Standalone"
    assert seed["juceDir"] == "/Applications/JUCE"
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


def test_create_new_project_seed_does_not_mutate_preferences_file(tmp_path):
    prefs_path = tmp_path / "preferences.json"
    prefs = Preferences(prefs_path)
    prefs.apply_profile({
        "manufacturer": "Acme Corp",
        "manufacturerCode": "Acme",
        "pluginCode": "Plug",
        "companyCopyright": "",
        "companyWebsite": "",
        "companyEmail": "",
        "destination": "/tmp/projects",
        "juceDir": "/Applications/JUCE",
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
