"""Unit tests for core.templates_store — override read/write/reset."""

import pytest

from core.project_generator import templates_dir
from core.templates_store import (
    GITIGNORE_FILE,
    has_override,
    overrides_dir,
    read_default,
    read_effective,
    reset,
    save_override,
    templates_root,
)


def _patch_config_root(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "core.templates_store.QStandardPaths.writableLocation",
        lambda _location: str(tmp_path),
    )


def test_save_override_source_file_round_trip(tmp_path, monkeypatch):
    _patch_config_root(tmp_path, monkeypatch)
    custom = "// custom processor header\n"
    save_override("PluginProcessor.h", custom)
    assert read_effective("PluginProcessor.h") == custom


def test_save_override_gitignore_round_trip(tmp_path, monkeypatch):
    _patch_config_root(tmp_path, monkeypatch)
    custom = "*.log\n"
    save_override(GITIGNORE_FILE, custom)
    assert read_effective(GITIGNORE_FILE) == custom


def test_reset_removes_override_returns_default(tmp_path, monkeypatch):
    _patch_config_root(tmp_path, monkeypatch)
    save_override("PluginProcessor.h", "custom\n")
    assert has_override("PluginProcessor.h")
    reset("PluginProcessor.h")
    assert not has_override("PluginProcessor.h")
    assert read_effective("PluginProcessor.h") == read_default("PluginProcessor.h")


def test_has_override_false_before_save(tmp_path, monkeypatch):
    _patch_config_root(tmp_path, monkeypatch)
    assert not has_override("PluginProcessor.h")
    assert read_effective("PluginProcessor.h") == read_default("PluginProcessor.h")


def test_overrides_dir_under_templates_root(tmp_path, monkeypatch):
    _patch_config_root(tmp_path, monkeypatch)
    assert overrides_dir() == templates_root() / "Source"


def test_read_default_matches_bundled_file():
    bundled = (templates_dir() / "Source" / "PluginProcessor.h").read_text(encoding="utf-8")
    assert read_default("PluginProcessor.h") == bundled
