"""Unit tests for publish/prepare-release.py helpers."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREPARE_RELEASE = PROJECT_ROOT / "publish" / "prepare-release.py"
RELEASE_WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "release.yml"


def _load_prepare_release():
    spec = importlib.util.spec_from_file_location("prepare_release", PREPARE_RELEASE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["prepare_release"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def prepare_release():
    return _load_prepare_release()


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.0.0", False),
        ("1.0.0-rc1", True),
        ("1.0.1-beta2", True),
        ("2.3.4-alpha.1", True),
    ],
)
def test_is_prerelease_version(prepare_release, version, expected):
    assert prepare_release.is_prerelease_version(version) is expected


def test_publish_ci_invokes_gh_not_git(prepare_release, tmp_path):
    release_dir = tmp_path / "1.0.0-rc1"
    release_dir.mkdir()
    paths = prepare_release.ReleasePaths(version="1.0.0-rc1", release_dir=release_dir)

    for name in ("macos", "windows", "linux", "docs"):
        (release_dir / f"Luthier-1.0.0-rc1-{name}.zip").write_bytes(b"zip")

    (release_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
    (release_dir / "SHA256SUMS.txt").write_text("deadbeef  fake\n", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_run(cmd, *, cwd=None, check=True):
        calls.append([str(part) for part in cmd])
        return subprocess.CompletedProcess(cmd, 0)

    with patch.object(prepare_release, "verify_release"), patch.object(
        prepare_release, "_gh_release_exists", return_value=False
    ), patch.object(prepare_release, "_run", side_effect=fake_run):
        prepare_release.publish_ci(paths, yes=True)

    joined = [" ".join(cmd) for cmd in calls]
    assert any("gh release create" in line for line in joined)
    assert any("--prerelease" in line for line in joined)
    assert not any(cmd[0] == "git" for cmd in calls)


def test_publish_ci_stable_release_omits_prerelease_flag(prepare_release, tmp_path):
    release_dir = tmp_path / "1.0.0"
    release_dir.mkdir()
    paths = prepare_release.ReleasePaths(version="1.0.0", release_dir=release_dir)

    for name in ("macos", "windows", "linux", "docs"):
        (release_dir / f"Luthier-1.0.0-{name}.zip").write_bytes(b"zip")
    (release_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
    (release_dir / "SHA256SUMS.txt").write_text("deadbeef  fake\n", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_run(cmd, *, cwd=None, check=True):
        calls.append([str(part) for part in cmd])
        return subprocess.CompletedProcess(cmd, 0)

    with patch.object(prepare_release, "verify_release"), patch.object(
        prepare_release, "_gh_release_exists", return_value=False
    ), patch.object(prepare_release, "_run", side_effect=fake_run):
        prepare_release.publish_ci(paths, yes=True)

    gh_cmd = next(cmd for cmd in calls if cmd[0:3] == ["gh", "release", "create"])
    assert "--prerelease" not in gh_cmd


def test_gh_release_create_uploads_when_release_exists(prepare_release, tmp_path):
    release_dir = tmp_path / "1.0.0-rc1"
    release_dir.mkdir()
    paths = prepare_release.ReleasePaths(version="1.0.0-rc1", release_dir=release_dir)

    for name in ("macos", "windows", "linux", "docs"):
        (release_dir / f"Luthier-1.0.0-rc1-{name}.zip").write_bytes(b"zip")
    (release_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
    (release_dir / "SHA256SUMS.txt").write_text("deadbeef  fake\n", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_run(cmd, *, cwd=None, check=True):
        calls.append([str(part) for part in cmd])
        return subprocess.CompletedProcess(cmd, 0)

    with patch.object(prepare_release, "verify_release"), patch.object(
        prepare_release, "_gh_release_exists", return_value=True
    ), patch.object(prepare_release, "_run", side_effect=fake_run):
        prepare_release.gh_release_create(paths, prerelease=True)

    assert not any(cmd[0:3] == ["gh", "release", "create"] for cmd in calls)
    upload_cmd = next(cmd for cmd in calls if cmd[0:3] == ["gh", "release", "upload"])
    assert "--clobber" in upload_cmd
    edit_cmd = next(cmd for cmd in calls if cmd[0:3] == ["gh", "release", "edit"])
    assert "--prerelease" in edit_cmd


def test_release_workflow_structure():
    workflow = yaml.safe_load(RELEASE_WORKFLOW.read_text(encoding="utf-8"))
    # PyYAML parses bare `on:` as boolean True
    triggers = workflow.get("on") or workflow.get(True) or {}

    assert "workflow_dispatch" not in triggers
    assert "push" in triggers
    assert "tags" in triggers["push"]
    assert workflow["permissions"]["contents"] == "write"
    assert workflow["concurrency"]["cancel-in-progress"] is False

    jobs = workflow["jobs"]
    assert set(jobs) == {"validate-tag", "build", "publish"}
    assert jobs["build"]["needs"] in (["validate-tag"], "validate-tag")
    assert jobs["publish"]["needs"] in (["build"], "build")

    build_yaml = yaml.dump(jobs["build"])
    assert "publish/build-dist.py" in build_yaml
    assert "prepare-release.py --version" in build_yaml
    assert "--force pack" in build_yaml
    assert "macos-latest" in build_yaml
    assert "windows-latest" in build_yaml
    assert "ubuntu-latest" in build_yaml

    publish_yaml = yaml.dump(jobs["publish"])
    assert "prepare-release.py --version" in publish_yaml
    assert "--force finalize" in publish_yaml
    assert "publish-ci --yes" in publish_yaml
