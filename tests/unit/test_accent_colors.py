"""Unit tests for accent colour presets."""

import pytest

from core.accent_colors import (
    ACCENT_PRESETS,
    DEFAULT_ACCENT_COLOR,
    is_valid_accent_color,
    normalize_accent_color,
)


def test_default_accent_is_magenta():
    assert DEFAULT_ACCENT_COLOR == "#A45C94"
    assert normalize_accent_color(None) == DEFAULT_ACCENT_COLOR
    assert normalize_accent_color("") == DEFAULT_ACCENT_COLOR


def test_palette_has_twelve_distinct_presets():
    colors = [color for _name, color in ACCENT_PRESETS]
    assert len(colors) == 12
    assert len(set(color.upper() for color in colors)) == 12


def test_normalize_accepts_lowercase_and_short_hex():
    assert normalize_accent_color("#a45c94") == "#A45C94"
    assert normalize_accent_color("A45C94") == "#A45C94"


def test_normalize_rejects_unknown_colours():
    assert normalize_accent_color("#FF0000") == DEFAULT_ACCENT_COLOR
    assert normalize_accent_color("not-a-color") == DEFAULT_ACCENT_COLOR


@pytest.mark.parametrize("color", [color for _name, color in ACCENT_PRESETS])
def test_each_preset_is_valid(color: str):
    assert is_valid_accent_color(color)
