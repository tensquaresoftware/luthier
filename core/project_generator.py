"""Generate a JUCE plugin project from the bundled templates.

Native, self-contained engine: Luthier owns the templates and the rendering,
with no dependency on any external generator.
"""

import sys
from pathlib import Path
from typing import Optional

from core import render_context
from core.project_spec import ProjectSpec
from core.project_writer import ProjectWriter

GENERATE_BLOCKED_MESSAGE = (
    "This folder already exists and is not empty. "
    "Luthier only creates new projects. "
    "Choose an empty folder or a different project name."
)


class GenerateBlockedError(Exception):
    def __init__(self, message: str = GENERATE_BLOCKED_MESSAGE) -> None:
        super().__init__(message)
        self.message = message


def project_dir_for_spec(spec: ProjectSpec) -> Path:
    return Path(spec.host_destination_dir()) / spec.project_name


def resolved_project_dir_for_spec(spec: ProjectSpec) -> Path:
    dest = spec.host_destination_dir().strip()
    if not dest:
        return project_dir_for_spec(spec)
    try:
        base = Path(dest).expanduser().resolve(strict=False)
    except OSError:
        base = Path(dest).expanduser()
    return base / spec.project_name


def session_regenerate_eligible(project_dir: Path, last_generated: Path | None) -> bool:
    if last_generated is None:
        return False
    try:
        return (
            project_dir.expanduser().resolve()
            == last_generated.expanduser().resolve()
        )
    except OSError:
        return False


def destination_blocks_generate(project_dir: Path) -> bool:
    if not project_dir.exists():
        return False
    if not project_dir.is_dir():
        return True
    return any(project_dir.iterdir())


def templates_dir() -> Path:
    """Bundled templates when frozen (PyInstaller), the repo copy otherwise."""
    bundle = getattr(sys, "_MEIPASS", None)
    root = Path(bundle) if bundle else Path(__file__).resolve().parent.parent
    return root / "templates"


class ProjectGenerator:
    """Builds a project directory from form values and copy settings."""

    def __init__(self, templates: Optional[Path] = None, overrides: Optional[Path] = None):
        self._templates = templates or templates_dir()
        self._overrides = overrides

    @property
    def error(self) -> Optional[str]:
        if self._templates.is_dir():
            return None
        return f"templates not found at {self._templates}"

    def generate(self, spec: ProjectSpec, *, allow_overwrite: bool = False) -> Path:
        project_dir = resolved_project_dir_for_spec(spec)
        if not allow_overwrite and destination_blocks_generate(project_dir):
            raise GenerateBlockedError()
        context = render_context.build_context(spec)
        tokens = render_context.build_tokens(spec)
        ProjectWriter(self._templates, project_dir, self._overrides).write(context, tokens, spec)
        return project_dir
