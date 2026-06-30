"""Unit tests for core.validation — pure field validators."""

import sys

import pytest

from core.validation import (
    generate_manufacturer_code,
    generate_plugin_code,
    validate_destination,
    validate_display_name,
    validate_manufacturer_code,
    validate_manufacturer_name,
    validate_optional,
    validate_optional_path,
    validate_plugin_code,
    validate_project_name,
    validate_version,
)


def _assert_result(result, *, expect_ok: bool):
    assert isinstance(result, tuple)
    assert len(result) == 2
    ok, msg = result
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    assert ok is expect_ok


@pytest.mark.parametrize(
    "value, expect_ok, msg_fragment",
    [
        ("MyPlugin", True, ""),
        ("A_b-1", True, ""),
        ("1bad", False, "letter"),
        ("has space", False, "letter"),
        ("", False, "letter"),
    ],
)
def test_validate_project_name(value, expect_ok, msg_fragment):
    result = validate_project_name(value)
    _assert_result(result, expect_ok=expect_ok)
    if not expect_ok:
        assert msg_fragment.lower() in result[1].lower()


@pytest.mark.parametrize(
    "value, expect_ok",
    [
        ("My Plugin-1", True),
        ("bad@char", False),
        ("", True),
    ],
)
def test_validate_display_name(value, expect_ok):
    result = validate_display_name(value)
    _assert_result(result, expect_ok=expect_ok)
    if not expect_ok:
        assert "Invalid characters" in result[1]


@pytest.mark.parametrize(
    "value, expect_ok",
    [
        ("1.0.0", True),
        ("   ", False),
        ("", False),
    ],
)
def test_validate_version(value, expect_ok):
    result = validate_version(value)
    _assert_result(result, expect_ok=expect_ok)
    if not expect_ok:
        assert "required" in result[1].lower()


@pytest.mark.parametrize(
    "value, expect_ok",
    [
        ("Acme Corp", True),
        ("   ", False),
        ("", False),
    ],
)
def test_validate_manufacturer_name(value, expect_ok):
    result = validate_manufacturer_name(value)
    _assert_result(result, expect_ok=expect_ok)
    if not expect_ok:
        assert "required" in result[1].lower()


@pytest.mark.parametrize(
    "value, expect_ok",
    [
        ("Myco", True),
        ("Abcd", True),
        ("abcd", False),
        ("Ab12", False),
        ("MYCO", False),
        ("", False),
    ],
)
def test_validate_manufacturer_code(value, expect_ok):
    result = validate_manufacturer_code(value)
    _assert_result(result, expect_ok=expect_ok)
    if not expect_ok:
        assert "uppercase" in result[1].lower()


@pytest.mark.parametrize(
    "value, expect_ok",
    [
        ("Mypl", True),
        ("Dem0", True),
        ("DEMO", False),
        ("1234", False),
        ("MYPL", False),
        ("mypl", False),
        ("abc", False),
        ("toolong", False),
        ("", False),
    ],
)
def test_validate_plugin_code(value, expect_ok):
    result = validate_plugin_code(value)
    _assert_result(result, expect_ok=expect_ok)
    if not expect_ok and value.upper() != "DEMO":
        assert "uppercase" in result[1].lower()
    if value.upper() == "DEMO":
        assert "reserved" in result[1].lower()


def test_generate_manufacturer_code_produces_valid_codes():
    for _ in range(30):
        code = generate_manufacturer_code()
        assert len(code) == 4
        assert validate_manufacturer_code(code)[0]


def test_generate_plugin_code_produces_valid_codes():
    for _ in range(30):
        code = generate_plugin_code()
        assert len(code) == 4
        assert code.upper() != "DEMO"
        assert validate_plugin_code(code)[0]


@pytest.mark.parametrize(
    "value, expect_ok",
    [
        ("/Users/dev/out", True),
        ("/café/path", True),
        ("", False),
        ("   ", False),
    ],
)
def test_validate_destination(value, expect_ok):
    result = validate_destination(value)
    _assert_result(result, expect_ok=expect_ok)
    if not expect_ok:
        assert "required" in result[1].lower()


@pytest.mark.parametrize(
    "value, expect_ok",
    [
        ("", True),
        ("/valid", True),
        ("/café", True),
    ],
)
def test_validate_optional_path(value, expect_ok):
    result = validate_optional_path(value)
    _assert_result(result, expect_ok=expect_ok)


@pytest.mark.parametrize("value", ["", "anything", "   "])
def test_validate_optional_always_valid(value):
    result = validate_optional(value)
    _assert_result(result, expect_ok=True)


def test_validation_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.validation  # noqa: F401

    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
