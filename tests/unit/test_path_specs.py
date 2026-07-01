"""Unit tests for shared path field specs."""

import sys

from app.pages.path_specs import (
    host_artefact_field_key,
    host_workspace_field_key,
    juce_dir_placeholder,
    workspace_destination_specs,
)
from core.paths import host_workspace_field_key as core_host_workspace_field_key


def test_juce_dir_placeholder_is_non_empty():
    assert juce_dir_placeholder()


def test_host_artefact_field_key_matches_platform(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    assert host_artefact_field_key() == "artefactsDirMacos"

    monkeypatch.setattr(sys, "platform", "win32")
    assert host_artefact_field_key() == "artefactsDirWindows"

    monkeypatch.setattr(sys, "platform", "linux")
    assert host_artefact_field_key() == "artefactsDirLinux"


def test_host_workspace_field_key_matches_platform(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    assert host_workspace_field_key("destination") == "destinationDirMacos"
    assert host_workspace_field_key("juce") == "juceDirMacos"
    assert core_host_workspace_field_key("destination") == "destinationDirMacos"

    monkeypatch.setattr(sys, "platform", "win32")
    assert host_workspace_field_key("destination") == "destinationDirWindows"
    assert host_workspace_field_key("juce") == "juceDirWindows"


def test_workspace_destination_specs_host_uses_required_validator(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    specs = workspace_destination_specs({"destinationDirMacos": "/tmp/out"})
    host = next(spec for spec in specs if spec.key == "destinationDirMacos")
    other = next(spec for spec in specs if spec.key == "destinationDirWindows")
    ok, _ = host.validator("")
    assert not ok
    ok, _ = other.validator("")
    assert ok
