"""Unit tests for core.project_spec — to_dict / from_dict serialization."""

import json
import sys
from dataclasses import fields

import pytest

from core.project_spec import ProjectSpec


def _make_spec(**kwargs):
    defaults = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        project_version="2.1.0",
        manufacturer_name="Acme",
        manufacturer_code="Acme",
        plugin_code="Mypl",
        company_copyright="Copyright 2026",
        company_website="https://acme.example",
        company_email="dev@acme.example",
        destination_dir="/tmp/out",
        plugin_type="synth",
        plugin_formats="VST3 AU",
        cxx_standard="C++20",
        preprocessor_definitions="FOO=1",
        header_search_paths="/extra/include",
        copy_to_system_folders=True,
        copy_to_artefacts_dir=False,
        artefacts_dir_windows="C:\\out",
        artefacts_dir_macos="/out/mac",
        artefacts_dir_linux="/out/linux",
    )
    defaults.update(kwargs)
    return ProjectSpec(**defaults)


def _assert_fields_equal(restored: ProjectSpec, original: ProjectSpec) -> None:
    for field in fields(original):
        assert getattr(restored, field.name) == getattr(original, field.name), field.name


def test_to_dict_from_dict_round_trip_all_fields():
    original = _make_spec()
    restored = ProjectSpec.from_dict(original.to_dict())
    _assert_fields_equal(restored, original)


def test_to_dict_from_dict_round_trip_defaults():
    original = ProjectSpec()
    restored = ProjectSpec.from_dict(original.to_dict())
    _assert_fields_equal(restored, original)


def test_to_dict_json_serializable_empty_optionals():
    spec = ProjectSpec()
    json.dumps(spec.to_dict())


@pytest.mark.parametrize(
    "copy_to_system_folders,copy_to_artefacts_dir",
    [(False, True), (True, False), (True, True), (False, False)],
)
def test_to_dict_json_serializable_populated(copy_to_system_folders, copy_to_artefacts_dir):
    spec = _make_spec(
        copy_to_system_folders=copy_to_system_folders,
        copy_to_artefacts_dir=copy_to_artefacts_dir,
    )
    json.dumps(spec.to_dict())


def test_from_dict_missing_keys_use_defaults():
    restored = ProjectSpec.from_dict({"projectName": "OnlyName"})
    defaults = ProjectSpec()
    assert restored.project_name == "OnlyName"
    for field in fields(defaults):
        if field.name == "project_name":
            continue
        assert getattr(restored, field.name) == getattr(defaults, field.name), field.name


def test_to_dict_camel_case_keys():
    spec = _make_spec(
        project_name="Alpha",
        copy_to_artefacts_dir=False,
        artefacts_dir_linux="/linux/out",
    )
    d = spec.to_dict()
    assert d["projectName"] == "Alpha"
    assert d["copyToArtefactsDir"] is False
    assert d["artefactsDirLinux"] == "/linux/out"
    assert ProjectSpec.from_dict(d).project_name == "Alpha"


def test_project_spec_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.project_spec  # noqa: F401

    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
