"""Unit tests for core.project_writer — atomic write and cleanup."""

import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from core import render_context
from core.project_generator import ProjectGenerator, templates_dir
from core.project_writer import ProjectWriter, _robust_rmtree
from tests.conftest import make_spec, write_project


def test_robust_rmtree_removes_readonly_files(tmp_path):
    target = tmp_path / "locked"
    target.mkdir()
    readonly = target / "object"
    readonly.write_text("git-like", encoding="utf-8")
    os.chmod(readonly, stat.S_IREAD)
    _robust_rmtree(target)
    assert not target.exists()


def test_regenerate_preserves_git_directory(tmp_path):
    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec)

    git_dir = project_dir / ".git"
    objects_dir = git_dir / "objects" / "06"
    objects_dir.mkdir(parents=True)
    git_object = objects_dir / "f8e57e6fedf09e55548fb0554bdc1f2f7c3f19"
    git_object.write_bytes(b"fake git object")
    os.chmod(git_object, stat.S_IREAD)
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    generator.generate(spec)

    assert (project_dir / ".git" / "HEAD").read_text(encoding="utf-8") == "ref: refs/heads/main\n"
    assert git_object.read_bytes() == b"fake git object"
    assert (project_dir / "CMakeLists.txt").is_file()


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
