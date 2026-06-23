"""Unit tests for core.rendering — str.format and @KEY@ token substitution."""

import sys

import pytest

from core.rendering import render, render_tokens


def test_render_substitutes_valid_template():
    assert render("Hello {name}", {"name": "Foo"}) == "Hello Foo"


def test_render_literal_braces():
    assert render("${{VAR}}", {}) == "${VAR}"


def test_render_missing_key_raises_key_error():
    with pytest.raises(KeyError):
        render("Hello {name}", {})


def test_render_tokens_substitutes_placeholder():
    assert render_tokens("@PROJECT_NAME@", {"PROJECT_NAME": "MyPlugin"}) == "MyPlugin"


def test_render_tokens_multiple_occurrences():
    content = "@NAME@ and @NAME@ again"
    assert render_tokens(content, {"NAME": "X"}) == "X and X again"


def test_render_tokens_absent_key_noop():
    assert render_tokens("@MISSING@", {}) == "@MISSING@"


def test_rendering_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.rendering  # noqa: F401

    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
