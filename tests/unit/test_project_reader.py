"""Unit tests for core.project_reader — sidecar validation and CMake edge cases."""

import json
import sys

import pytest

from core import plugin_settings
from core.project_reader import read_project_result


def _valid_sidecar(**overrides):
    data = {
        "projectName": "MyPlugin",
        "pluginFormats": "VST3",
        "pluginType": plugin_settings.TYPE_INSTRUMENT,
    }
    data.update(overrides)
    return data


def _write_sidecar(project_dir, data):
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / ".luthier.json").write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def test_empty_sidecar_returns_error(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    _write_sidecar(project_dir, {})
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error
    assert "empty" in result.error.lower()


def test_malformed_json_returns_error(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / ".luthier.json").write_text("{not json", encoding="utf-8")
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error
    assert "json" in result.error.lower()


def test_sidecar_null_project_name_fails(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    _write_sidecar(project_dir, _valid_sidecar(projectName=None))
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error
    assert "projectName" in result.error


def test_sidecar_wrong_type_project_name_fails(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    _write_sidecar(project_dir, _valid_sidecar(projectName=123))
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error
    assert "projectName" in result.error


def test_sidecar_empty_project_name_fails(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    _write_sidecar(project_dir, _valid_sidecar(projectName="   "))
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error


def test_sidecar_null_plugin_formats_fails(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    _write_sidecar(project_dir, _valid_sidecar(pluginFormats=None))
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error
    assert "pluginFormats" in result.error


def test_sidecar_unknown_plugin_type_fails(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    _write_sidecar(project_dir, _valid_sidecar(pluginType="Instrument"))
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error
    assert "pluginType" in result.error


def test_sidecar_string_bools_coerced(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    data = _valid_sidecar(
        copyToSystemFolders="ON",
        copyToArtefactsDir="false",
    )
    _write_sidecar(project_dir, data)
    result = read_project_result(project_dir)
    assert result.spec is not None
    assert result.error is None
    assert result.spec.copy_to_system_folders is True
    assert result.spec.copy_to_artefacts_dir is False


def test_cmake_escaped_quotes_in_company_name(tmp_path):
    from tests.conftest import write_project, make_spec

    dest, _ = write_project(tmp_path, make_spec(tmp_path))
    (dest / ".luthier.json").unlink()
    cmake = dest / "CMakeLists.txt"
    text = cmake.read_text(encoding="utf-8")
    text = text.replace('COMPANY_NAME "Acme"', r'COMPANY_NAME "O\"Reilly"')
    cmake.write_text(text, encoding="utf-8")

    result = read_project_result(dest)
    assert result.spec is not None
    assert result.spec.manufacturer_name == 'O"Reilly'


def test_project_reader_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.project_reader  # noqa: F401

    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
