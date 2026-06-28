"""Unit tests for atomic JSON file writes."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from core.json_files import atomic_write_text


def test_atomic_write_text_creates_valid_json(tmp_path):
    path = tmp_path / "config.json"
    atomic_write_text(path, '{"key": "value"}')
    assert json.loads(path.read_text(encoding="utf-8")) == {"key": "value"}
    assert not (tmp_path / "config.json.tmp").exists()


def test_atomic_write_leaves_original_unchanged_on_replace_failure(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"original": true}', encoding="utf-8")
    original = path.read_bytes()
    with patch.object(Path, "replace", side_effect=OSError("simulated crash")):
        with pytest.raises(OSError, match="simulated crash"):
            atomic_write_text(path, '{"new": false}')
    assert path.read_bytes() == original
    assert not (tmp_path / "config.json.tmp").exists()
