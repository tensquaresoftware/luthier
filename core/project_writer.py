"""Write a generated project tree from the template files."""

import json
import os
import shutil
import stat
import sys
import time
from pathlib import Path
from typing import Callable, Optional, TypeVar

from core import rendering
from core.project_spec import ProjectSpec

_T = TypeVar("_T")


def _is_sharing_violation(exc: BaseException) -> bool:
    if isinstance(exc, PermissionError):
        return True
    if isinstance(exc, OSError):
        winerror = getattr(exc, "winerror", None)
        if winerror in (32, 5):
            return True
    return False


def _retry_on_sharing_violation(
    func: Callable[[], _T],
    *,
    attempts: int = 10,
    base_delay: float = 0.1,
) -> _T:
    last: BaseException | None = None
    for attempt in range(attempts):
        try:
            return func()
        except OSError as exc:
            last = exc
            if (
                sys.platform == "win32"
                and _is_sharing_violation(exc)
                and attempt + 1 < attempts
            ):
                time.sleep(base_delay * (2**attempt))
                continue
            raise
    assert last is not None
    raise last


def _robust_rmtree(path: Path) -> None:
    """Remove a directory tree, clearing read-only files (e.g. Git objects on Windows)."""

    def _remove() -> None:
        def _onerror(func, p, _exc_info):
            os.chmod(p, stat.S_IWRITE)
            func(p)

        shutil.rmtree(path, onerror=_onerror)

    if sys.platform == "win32":
        _retry_on_sharing_violation(_remove)
    else:
        _remove()


def _rename_path(src: Path, dst: Path) -> None:
    if sys.platform == "win32":
        _retry_on_sharing_violation(lambda: src.rename(dst))
    else:
        src.rename(dst)


def _copy_git_directory(src: Path, dst: Path) -> None:
    """Copy ``.git`` into a fresh project tree (source is left untouched)."""
    if dst.exists():
        _robust_rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)


def _swap_project_tree(project: Path, tmp: Path, stash: Path) -> None:
    """Replace ``project`` with ``tmp``, moving the previous tree to ``stash``.

    Avoids deleting ``.git`` in place on Windows (WinError 32 when Git or the
    shell holds handles). The caller must copy ``.git`` into ``tmp`` first when
    preservation is required.
    """
    if stash.exists():
        _robust_rmtree(stash)
    _rename_path(project, stash)
    try:
        _rename_path(tmp, project)
    except Exception:
        if stash.exists() and not project.exists():
            _rename_path(stash, project)
        raise
    if stash.exists():
        try:
            _robust_rmtree(stash)
        except OSError:
            pass


_RENDERED = (
    "CMakeLists.txt",
    "CMakeUserPresets.json",
    ".vscode/settings.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    "README.md",
)

_TOKENIZED = (
    "Source/PluginProcessor.h",
    "Source/PluginProcessor.cpp",
    "Source/PluginEditor.h",
    "Source/PluginEditor.cpp",
)

_VERBATIM = (
    ".vscode/extensions.json",
    ".cursorrules",
    ".gitignore",
    "CMake/CopyVst3Elevated.ps1",
)


class ProjectWriter:
    """Renders and writes every project file into the destination directory."""

    def __init__(self, templates_dir: Path, project_dir: Path, overrides: Optional[Path] = None):
        self._templates = templates_dir
        self._project = project_dir
        self._overrides = overrides

    def write(self, context: dict, tokens: dict, spec: ProjectSpec) -> None:
        """Render and atomically replace the project directory.

        If the final ``rename`` fails after moving the existing tree aside, the
        previous project is restored from the stash when possible. The temporary
        directory is cleaned up on failure when possible.
        """
        tmp = self._project.parent / (self._project.name + ".tmp")
        stash = self._project.parent / (self._project.name + ".old")
        if tmp.exists():
            _robust_rmtree(tmp)
        try:
            self._write_all(tmp, context, tokens)
            self._write_sidecar(tmp, spec)
            if self._project.is_dir():
                git_src = self._project / ".git"
                if git_src.is_dir():
                    _copy_git_directory(git_src, tmp / ".git")
                _swap_project_tree(self._project, tmp, stash)
            else:
                tmp.rename(self._project)
        except Exception:
            try:
                if tmp.exists():
                    _robust_rmtree(tmp)
            except Exception:
                pass
            raise

    def _write_all(self, dest: Path, context: dict, tokens: dict) -> None:
        for relative in _RENDERED:
            self._write_file(dest, relative, rendering.render(self._read(relative), context))
        for relative in _TOKENIZED:
            self._write_file(dest, relative, rendering.render_tokens(self._read(relative), tokens))
        for relative in _VERBATIM:
            self._write_file(dest, relative, self._read(relative))

    def _write_sidecar(self, dest: Path, spec: ProjectSpec) -> None:
        (dest / ".luthier.json").write_text(
            json.dumps(spec.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _read(self, relative: str) -> str:
        source = self._override_for(relative) or self._templates / relative
        return source.read_text(encoding="utf-8")

    def _override_for(self, relative: str) -> Optional[Path]:
        if not self._overrides:
            return None
        if relative in _TOKENIZED:
            candidate = self._overrides / Path(relative).name
            return candidate if candidate.exists() else None
        if relative == ".gitignore":
            candidate = self._overrides.parent / ".gitignore"
            return candidate if candidate.exists() else None
        return None

    def _write_file(self, root: Path, relative: str, content: str) -> None:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
