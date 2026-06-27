"""Unit tests for shared path field specs."""

import sys

from app.pages.path_specs import (
    destination_field_spec,
    host_artefact_field_key,
    juce_dir_placeholder,
    juce_field_spec,
)


def test_destination_field_spec_project_defaults():
    spec = destination_field_spec("/tmp/out")
    assert spec.key == "destinationDir"
    assert spec.label == "Destination folder *"
    assert spec.default == "/tmp/out"
    ok, _ = spec.validator("/tmp/out")
    assert ok


def test_destination_field_spec_preferences_key():
    spec = destination_field_spec("/prefs", key="destination", label="Destination folder")
    assert spec.key == "destination"
    assert spec.label == "Destination folder"


def test_juce_field_spec_optional_validation():
    spec = juce_field_spec("/Applications/JUCE")
    assert spec.key == "juceDir"
    assert spec.placeholder == juce_dir_placeholder()
    ok, _ = spec.validator("")
    assert ok
    ok, _ = spec.validator("/Applications/JUCE")
    assert ok


def test_juce_field_spec_accepts_empty_path():
    spec = juce_field_spec("")
    ok, _ = spec.validator("")
    assert ok


def test_host_artefact_field_key_matches_platform(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    assert host_artefact_field_key() == "artefactsDirMacos"

    monkeypatch.setattr(sys, "platform", "win32")
    assert host_artefact_field_key() == "artefactsDirWindows"

    monkeypatch.setattr(sys, "platform", "linux")
    assert host_artefact_field_key() == "artefactsDirLinux"
