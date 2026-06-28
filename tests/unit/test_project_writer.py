"""Unit tests for core.project_writer — atomic write and cleanup."""

from pathlib import Path
from unittest.mock import patch

import pytest

from core import render_context
from core.project_generator import templates_dir
from core.project_writer import ProjectWriter
from tests.conftest import make_spec, write_project


def test_write_leaves_no_tmp_dir_on_success(tmp_path):
    dest, spec = write_project(tmp_path, make_spec(tmp_path))
    assert not (dest.parent / (dest.name + ".tmp")).exists()


def test_write_cleans_tmp_on_failure(tmp_path):
    dest = tmp_path / "MyPlugin"
    spec = make_spec(tmp_path)
    writer = ProjectWriter(Path("/nonexistent"), dest)
    with pytest.raises(Exception):
        writer.write({}, {}, spec)
    tmp_path_dir = dest.parent / (dest.name + ".tmp")
    assert not tmp_path_dir.exists()
    assert not dest.exists()


def test_write_rename_failure_propagates(tmp_path):
    dest = tmp_path / "MyPlugin"
    spec = make_spec(tmp_path)
    writer = ProjectWriter(templates_dir(), dest)
    ctx = render_context.build_context(spec)
    tokens = render_context.build_tokens(spec)
    writer.write(ctx, tokens, spec)
    assert dest.exists()

    with patch.object(Path, "rename", side_effect=OSError("simulated rename failure")):
        with pytest.raises(OSError, match="simulated rename failure"):
            writer.write(ctx, tokens, spec)
