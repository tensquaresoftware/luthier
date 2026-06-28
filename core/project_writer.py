"""Write a generated project tree from the template files."""

import json
import shutil
from pathlib import Path
from typing import Optional

from core import rendering
from core.project_spec import ProjectSpec

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

        If ``rename`` fails after removing the existing project directory, the
        previous project tree is lost; only manual recovery (VCS/backup) is
        possible. The temporary directory is cleaned up on failure when possible.
        """
        tmp = self._project.parent / (self._project.name + ".tmp")
        if tmp.exists():
            shutil.rmtree(tmp)
        try:
            self._write_all(tmp, context, tokens)
            self._write_sidecar(tmp, spec)
            if self._project.exists():
                shutil.rmtree(self._project)
            tmp.rename(self._project)
        except Exception:
            try:
                if tmp.exists():
                    shutil.rmtree(tmp)
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
