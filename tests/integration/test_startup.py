"""Startup and main-window construction tests."""

import pytest
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from core.paths import resolve_dir
from core.preferences import Preferences


@pytest.fixture(scope="session")
def qapp():
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    return application


def test_main_window_constructs_with_corrupt_preferences(tmp_path, qapp):
    prefs_path = tmp_path / "preferences.json"
    prefs_path.write_text("{", encoding="utf-8")
    prefs = Preferences(prefs_path)
    prefs.bootstrap()
    assert prefs.load_warning is not None

    window = MainWindow(prefs)
    try:
        assert window._prefs.load_warning is not None
    finally:
        window.close()


def test_bootstrap_falls_back_when_preferences_cannot_be_created(tmp_path, qapp, monkeypatch):
    prefs_path = tmp_path / "prefs" / "preferences.json"
    prefs = Preferences(prefs_path)

    def fail_save(_path, _content):
        raise OSError("disk full")

    monkeypatch.setattr("core.preferences.atomic_write_text", fail_save)
    prefs.bootstrap()

    assert prefs._initialized is True
    assert prefs.load_warning is not None
    assert prefs.get("manufacturer") == "My Company"


def test_resolve_dir_expands_user_home(tmp_path, monkeypatch):
    nested = tmp_path / "été 2026"
    nested.mkdir()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert resolve_dir(f"~/{nested.name}") == nested.resolve()
