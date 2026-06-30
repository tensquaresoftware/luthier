from core import validation
from core.paths import (
    is_path_validator,
    normalize_path_dict_values,
    normalize_portable_path,
    resolve_dir,
)


def test_normalize_portable_path_forward_slashes_windows():
    assert normalize_portable_path(r"C:\Users\dev\JUCE") == "C:/Users/dev/JUCE"


def test_normalize_portable_path_strips_and_preserves_unix():
    assert normalize_portable_path("  /opt/juce  ") == "/opt/juce"


def test_normalize_portable_path_empty():
    assert normalize_portable_path("") == ""


def test_is_path_validator():
    assert is_path_validator(validation.validate_destination)
    assert is_path_validator(validation.validate_optional_path)
    assert not is_path_validator(validation.validate_project_name)


def test_normalize_path_dict_values():
    data = {
        "destinationDir": r"C:\out",
        "juceDir": "C:/JUCE",
        "projectName": "MyPlugin",
    }
    out = normalize_path_dict_values(data)
    assert out["destinationDir"] == "C:/out"
    assert out["juceDir"] == "C:/JUCE"
    assert out["projectName"] == "MyPlugin"


def test_resolve_dir_expands_user_and_accepts_unicode(tmp_path, monkeypatch):
    folder = tmp_path / "Téléchargements"
    folder.mkdir()
    monkeypatch.setenv("HOME", str(tmp_path))
    assert resolve_dir("~/Téléchargements") == folder.resolve()


def test_resolve_dir_missing_returns_none():
    assert resolve_dir("/path/that/does/not/exist") is None
    assert resolve_dir("") is None
