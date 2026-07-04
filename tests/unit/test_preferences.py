"""Unit tests for Preferences profile API."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from core.accent_colors import DEFAULT_ACCENT_COLOR
from core.paths import host_workspace_field_key
from core.preferences import Preferences, factory_defaults, validate_profile
from core.plugin_settings import TYPE_AUDIO_EFFECT, TYPE_INSTRUMENT


def _valid_profile(**overrides) -> dict:
    from core.paths import host_workspace_field_key

    host_dest = host_workspace_field_key("destination")
    host_juce = host_workspace_field_key("juce")
    data = {
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
        "pluginType": TYPE_INSTRUMENT,
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
    assert defaults[host_workspace_field_key("destination")] == "/mock/Desktop"
    assert defaults["pluginType"] == TYPE_INSTRUMENT
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
    assert defaults[host_workspace_field_key("destination")] == str(Path.home())


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
    host_dest = host_workspace_field_key("destination")
    assert data[host_dest] == "/mock/Desktop"
    assert data["pluginType"] == TYPE_INSTRUMENT


def test_to_dict_apply_profile_round_trip(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    profile = _valid_profile(**{host_workspace_field_key("destination"): "/projects/out"}, pluginType=TYPE_AUDIO_EFFECT)
    prefs.apply_profile(profile)
    prefs.save()
    reloaded = Preferences(path)
    reloaded.load()
    assert reloaded.to_dict() == prefs.to_dict()
    assert reloaded.get("pluginType") == TYPE_AUDIO_EFFECT
    assert reloaded.get(host_workspace_field_key("destination")) == "/projects/out"


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
    host_dest = host_workspace_field_key("destination")
    prefs.apply_profile(_valid_profile(
        manufacturer="Seed Co",
        **{host_dest: "/seed/dest"},
        pluginFormats="VST3",
    ))
    seed = prefs.seed_dict()
    assert seed["manufacturerName"] == "Seed Co"
    assert seed[host_dest] == "/seed/dest"
    assert seed["pluginFormats"] == "VST3"
    assert seed["manufacturer"] == "Seed Co"
    assert "accentColor" not in seed


def test_seed_dict_round_trips_through_project_spec(tmp_path):
    from core.project_spec import ProjectSpec

    prefs = Preferences(tmp_path / "preferences.json")
    host_dest = host_workspace_field_key("destination")
    host_juce = host_workspace_field_key("juce")
    prefs.apply_profile(_valid_profile(
        **{host_dest: "/seed/dest", host_juce: "/Applications/JUCE"},
        pluginType=TYPE_AUDIO_EFFECT,
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
    assert spec.host_destination_dir() == "/seed/dest"
    assert spec.host_juce_dir() == "/Applications/JUCE"
    assert spec.plugin_type == TYPE_AUDIO_EFFECT
    assert spec.plugin_formats == "AU VST3"
    assert spec.cxx_standard == "C++20"


def test_accent_color_defaults_on_first_run(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        prefs.ensure_initialized()
    assert prefs.accent_color == DEFAULT_ACCENT_COLOR
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["accentColor"] == DEFAULT_ACCENT_COLOR


def test_accent_color_persists_and_normalizes(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile())
    prefs.set_accent_color("#3232C3")
    prefs.save()
    reloaded = Preferences(tmp_path / "preferences.json")
    reloaded.load()
    assert reloaded.accent_color == "#3232C3"


def test_accent_color_survives_invalid_profile_reset(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.apply_profile(_valid_profile())
    prefs.set_accent_color("#D959B9")
    prefs.save()
    path.write_text(json.dumps({"accentColor": "#D959B9", "pluginFormats": ""}), encoding="utf-8")
    reloaded = Preferences(path)
    reloaded.load()
    assert reloaded.accent_color == "#D959B9"
    assert reloaded.load_warning is None


def test_export_profile_includes_accent_color(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile())
    prefs.set_accent_color("#3232C3")
    prefs.save()
    data = json.loads((tmp_path / "preferences.json").read_text(encoding="utf-8"))
    assert data["accentColor"] == "#3232C3"


def test_export_profile_includes_all_workspace_keys(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    profile = _valid_profile(
        destinationDirWindows="C:/win",
        destinationDirMacos="/mac",
        destinationDirLinux="/linux",
        juceDirWindows="C:/juce",
        juceDirMacos="/juce/mac",
        juceDirLinux="/juce/linux",
    )
    prefs.apply_profile(profile)
    prefs.save()
    data = json.loads((tmp_path / "preferences.json").read_text(encoding="utf-8"))
    for key in (
        "destinationDirWindows",
        "destinationDirMacos",
        "destinationDirLinux",
        "juceDirWindows",
        "juceDirMacos",
        "juceDirLinux",
    ):
        assert data[key] == profile[key]


def test_import_profile_restores_accent_color(tmp_path):
    path = tmp_path / "client.json"
    path.write_text(
        json.dumps({**_valid_profile(), "accentColor": "#D959B9"}),
        encoding="utf-8",
    )
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(json.loads(path.read_text(encoding="utf-8")))
    assert prefs.accent_color == "#D959B9"


def test_to_dict_excludes_accent_color(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile())
    prefs.set_accent_color("#6113D7")
    assert "accentColor" not in prefs.to_dict()


def test_validate_profile_rejects_invalid_accent_color(tmp_path):
    profile = {**_valid_profile(), "accentColor": "#FF0000"}
    ok, message = validate_profile(profile)
    assert not ok
    assert "accentColor" in message


def test_load_invalid_accent_corrects_file_and_sets_warning(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.apply_profile(_valid_profile())
    prefs.set_accent_color("#3232C3")
    prefs.save()
    data = json.loads(path.read_text(encoding="utf-8"))
    data["accentColor"] = "#FF0000"
    path.write_text(json.dumps(data), encoding="utf-8")

    reloaded = Preferences(path)
    reloaded.load()

    assert reloaded.accent_color == DEFAULT_ACCENT_COLOR
    assert reloaded.accent_color_warning is not None
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["accentColor"] == DEFAULT_ACCENT_COLOR


def test_load_normalizes_valid_accent_case_without_warning(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.apply_profile(_valid_profile())
    prefs.save()
    data = json.loads(path.read_text(encoding="utf-8"))
    data["accentColor"] = "#3232c3"
    path.write_text(json.dumps(data), encoding="utf-8")

    reloaded = Preferences(path)
    reloaded.load()

    assert reloaded.accent_color == "#3232C3"
    assert reloaded.accent_color_warning is None
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["accentColor"] == "#3232C3"


def test_apply_profile_rejects_invalid_accent_color(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    with pytest.raises(ValueError, match="accentColor"):
        prefs.apply_profile({**_valid_profile(), "accentColor": "not-a-color"})


def test_save_uses_atomic_write(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.apply_profile(_valid_profile())
    prefs.save()
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))
    assert not (tmp_path / "preferences.json.tmp").exists()


def test_save_leaves_original_unchanged_on_crash(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.apply_profile(_valid_profile())
    prefs.save()
    original = path.read_bytes()
    prefs.apply_profile(_valid_profile(manufacturer="After Crash"))
    with patch.object(Path, "replace", side_effect=OSError("simulated crash")):
        with pytest.raises(OSError, match="simulated crash"):
            prefs.save()
    assert path.read_bytes() == original
    assert not (tmp_path / "preferences.json.tmp").exists()


def test_load_corrupt_json_resets_and_sets_warning(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text("{ truncated", encoding="utf-8")
    prefs = Preferences(path)
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        prefs.load()
    assert prefs.load_warning is not None
    assert "corrupt" in prefs.load_warning.lower()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["manufacturer"] == "My Company"
    assert data["accentColor"] == DEFAULT_ACCENT_COLOR


def test_load_non_dict_root_resets_and_sets_warning(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    prefs = Preferences(path)
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        prefs.load()
    assert prefs.load_warning is not None
    assert json.loads(path.read_text(encoding="utf-8"))["manufacturer"] == "My Company"


def test_load_missing_file_sets_no_warning(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.load()
    assert prefs.load_warning is None


def test_load_read_oserror_resets_and_sets_warning(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text("{}", encoding="utf-8")
    prefs = Preferences(path)
    with patch.object(Path, "read_text", side_effect=OSError("read failed")):
        with patch(
            "core.preferences.QStandardPaths.writableLocation",
            return_value="/mock/Desktop",
        ):
            prefs.load()
    assert prefs.load_warning is not None
    assert "corrupt" in prefs.load_warning.lower()


def test_load_warning_survives_second_ensure_initialized(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text("{ truncated", encoding="utf-8")
    prefs = Preferences(path)
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        prefs.ensure_initialized()
        assert prefs.load_warning is not None
        prefs.ensure_initialized()
    assert prefs.load_warning is not None


def test_reset_corrupt_file_survives_save_failure(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text("not json", encoding="utf-8")
    prefs = Preferences(path)
    with patch(
        "core.preferences.QStandardPaths.writableLocation",
        return_value="/mock/Desktop",
    ):
        with patch(
            "core.preferences.atomic_write_text",
            side_effect=OSError("disk full"),
        ):
            prefs.load()
    assert prefs.load_warning is not None


def test_load_null_path_fields_coerced_to_empty_string(tmp_path):
    path = tmp_path / "preferences.json"
    host_juce = host_workspace_field_key("juce")
    path.write_text(
        json.dumps({
            **_valid_profile(),
            host_juce: None,
            "artefactsDirWindows": None,
            "accentColor": DEFAULT_ACCENT_COLOR,
        }),
        encoding="utf-8",
    )
    prefs = Preferences(path)
    prefs.load()
    assert prefs.get(host_juce) == ""
    assert prefs.get("artefactsDirWindows") == ""
    assert prefs.to_dict()[host_juce] == ""
    assert prefs.to_dict()["artefactsDirWindows"] == ""


def test_apply_profile_null_string_fields_become_empty(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    host_juce = host_workspace_field_key("juce")
    prefs.apply_profile(_valid_profile(**{host_juce: None}, headerSearchPaths=None))
    assert prefs.get(host_juce) == ""
    assert prefs.get("headerSearchPaths") == ""


def test_apply_profile_invalid_accent_does_not_mutate_profile(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile(manufacturer="Stable Co"))
    before = prefs.to_dict()
    with pytest.raises(ValueError, match="accentColor"):
        prefs.apply_profile({**_valid_profile(manufacturer="Changed"), "accentColor": "bad"})
    assert prefs.to_dict() == before


def test_import_save_failure_restores_profile(tmp_path):
    path = tmp_path / "preferences.json"
    prefs = Preferences(path)
    prefs.apply_profile(_valid_profile(manufacturer="Keep Me"))
    prefs.save()
    before = prefs.to_dict()
    new_profile = _valid_profile(manufacturer="New Name")
    with patch.object(Preferences, "save", side_effect=OSError("disk full")):
        with pytest.raises(OSError, match="disk full"):
            prefs.apply_profile(new_profile)
            prefs.save()
    prefs.apply_profile(before)
    assert prefs.to_dict() == before


def test_import_rollback_restores_accent_color(tmp_path):
    prefs = Preferences(tmp_path / "preferences.json")
    prefs.apply_profile(_valid_profile())
    prefs.set_accent_color("#6113D7")
    prefs.save()
    before = prefs.to_dict()
    before_accent = prefs.accent_color
    new_profile = {**_valid_profile(manufacturer="New Co"), "accentColor": "#3232C3"}
    prefs.apply_profile(new_profile)
    with patch.object(Preferences, "save", side_effect=OSError("disk full")):
        with pytest.raises(OSError, match="disk full"):
            prefs.save()
    prefs.apply_profile(before)
    prefs.set_accent_color(before_accent)
    assert prefs.to_dict() == before
    assert prefs.accent_color == "#6113D7"
