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


def templates_dir() -> Path:
    """Bundled Templates when frozen (PyInstaller), the repo copy otherwise."""
    bundle = getattr(sys, "_MEIPASS", None)
    root = Path(bundle) if bundle else Path(__file__).resolve().parent.parent
    return root / "Templates"


class ProjectGenerator:
    """Builds a project directory from form values and copy settings."""

    def __init__(self, templates: Optional[Path] = None, overrides: Optional[Path] = None):
        self._templates = templates or templates_dir()
        self._overrides = overrides

    @property
    def error(self) -> Optional[str]:
        if self._templates.is_dir():
            return None
        return f"Templates not found at {self._templates}"

    def project_exists(self, destination: str, project_name: str) -> bool:
        return (Path(destination) / project_name).exists()

    def generate(self, spec: ProjectSpec, juce_dir: str = "") -> Path:
        project_dir = Path(spec.destination_dir) / spec.project_name
        context = render_context.build_context(spec, juce_dir=juce_dir)
        tokens = render_context.build_tokens(spec)
        ProjectWriter(self._templates, project_dir, self._overrides).write(context, tokens, spec)
        return project_dir
