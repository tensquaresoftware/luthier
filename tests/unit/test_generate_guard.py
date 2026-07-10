"""Unit tests for generate destination guard (Story 9.2) and session regenerate (9.8)."""

import os

import pytest

from core.app_state import AppState
from core.project_generator import (
    GENERATE_BLOCKED_MESSAGE,
    GenerateBlockedError,
    ProjectGenerator,
    destination_blocks_generate,
    project_dir_for_spec,
    resolved_project_dir_for_spec,
    session_regenerate_eligible,
)
from tests.conftest import make_spec


def test_session_regenerate_eligible_same_path(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    assert session_regenerate_eligible(project_dir, project_dir) is True


def test_session_regenerate_eligible_different_path(tmp_path):
    a = tmp_path / "PluginA"
    b = tmp_path / "PluginB"
    a.mkdir()
    b.mkdir()
    assert session_regenerate_eligible(b, a) is False


def test_session_regenerate_eligible_no_last_generated(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    assert session_regenerate_eligible(project_dir, None) is False


def test_fresh_app_state_blocks_non_empty_without_session(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / "CMakeLists.txt").write_text("cmake", encoding="utf-8")
    state = AppState(tmp_path / "app_state.json")
    assert destination_blocks_generate(project_dir) is True
    assert session_regenerate_eligible(project_dir, state.last_generated_project_dir()) is False


def test_generate_overwrite_updates_project(tmp_path):
    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    generator.generate(spec)
    spec = make_spec(tmp_path, project_display_name="Renamed Plugin")
    project_dir = generator.generate(spec, allow_overwrite=True)
    assert project_dir == tmp_path / "MyPlugin"
    sidecar = project_dir / ".luthier.json"
    assert sidecar.is_file()
    assert "Renamed Plugin" in sidecar.read_text(encoding="utf-8")


def test_generate_overwrite_preserves_git(tmp_path):
    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec)
    git_dir = project_dir / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    generator.generate(spec, allow_overwrite=True)
    assert git_dir.is_dir()
    assert (git_dir / "HEAD").read_text(encoding="utf-8") == "ref: refs/heads/main\n"


def test_generate_overwrite_preserves_git_init_repo(tmp_path):
    """Session regenerate after real ``git init`` (Windows file-lock regression)."""
    import shutil
    import subprocess

    if shutil.which("git") is None:
        pytest.skip("git not on PATH")

    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Luthier Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Luthier Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=project_dir,
        check=True,
        capture_output=True,
        env=env,
    )
    spec = make_spec(tmp_path, project_version="2.0.0")
    generator.generate(spec, allow_overwrite=True)
    assert (project_dir / ".git" / "HEAD").is_file()
    assert (project_dir / ".luthier.json").read_text(encoding="utf-8").find("2.0.0") >= 0


def test_resolved_project_dir_for_spec(tmp_path):
    spec = make_spec(tmp_path)
    assert resolved_project_dir_for_spec(spec) == tmp_path / "MyPlugin"


def test_session_memory_matches_resolved_path_with_tilde(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    projects = tmp_path / "Projects"
    projects.mkdir()
    spec = make_spec(tmp_path, destination_dir="~/Projects")
    generator = ProjectGenerator()
    state = AppState(tmp_path / "app_state.json")

    project_dir = generator.generate(spec)
    state.remember_generated_project(project_dir)
    resolved = resolved_project_dir_for_spec(spec)

    assert project_dir == resolved
    assert session_regenerate_eligible(resolved, state.last_generated_project_dir()) is True


def test_destination_blocks_non_empty_dir(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / "CMakeLists.txt").write_text("cmake", encoding="utf-8")
    assert destination_blocks_generate(project_dir) is True


def test_destination_allows_empty_dir(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    assert destination_blocks_generate(project_dir) is False


def test_destination_allows_missing_dir(tmp_path):
    assert destination_blocks_generate(tmp_path / "MyPlugin") is False


def test_destination_blocks_non_directory(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.write_text("not a directory", encoding="utf-8")
    assert destination_blocks_generate(project_dir) is True


def test_destination_blocks_hidden_ds_store(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / ".DS_Store").write_bytes(b"\x00")
    assert destination_blocks_generate(project_dir) is True


def test_destination_blocks_git_directory(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()
    assert destination_blocks_generate(project_dir) is True


def test_project_dir_for_spec(tmp_path):
    spec = make_spec(tmp_path)
    assert project_dir_for_spec(spec) == tmp_path / "MyPlugin"


def test_generate_blocked_on_non_empty(tmp_path):
    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    generator.generate(spec)
    with pytest.raises(GenerateBlockedError) as exc_info:
        generator.generate(spec)
    assert exc_info.value.message == GENERATE_BLOCKED_MESSAGE


def test_generate_allowed_into_empty_dir(tmp_path):
    spec = make_spec(tmp_path)
    project_dir = tmp_path / spec.project_name
    project_dir.mkdir()
    generator = ProjectGenerator()
    result = generator.generate(spec)
    assert result == project_dir
    assert (project_dir / "CMakeLists.txt").is_file()


def test_generate_allowed_into_fresh_path(tmp_path):
    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec)
    assert project_dir == tmp_path / "MyPlugin"
    assert (project_dir / ".luthier.json").is_file()
