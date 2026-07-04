"""Unit tests for generate destination guard (Story 9.2)."""

import pytest

from core.project_generator import (
    GENERATE_BLOCKED_MESSAGE,
    GenerateBlockedError,
    ProjectGenerator,
    destination_blocks_generate,
    project_dir_for_spec,
)
from tests.conftest import make_spec


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
