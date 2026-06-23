"""Tests for story 1-2: Core Generation Pipeline Accepts ProjectSpec."""

import json
import sys
import tempfile
import unittest
from pathlib import Path


def _make_spec(**kwargs):
    from core.project_spec import ProjectSpec

    defaults = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        project_version="1.0.0",
        manufacturer_name="Acme",
        manufacturer_code="Acme",
        plugin_code="Mypl",
        destination_dir=str(Path(tempfile.gettempdir())),
        plugin_type="synth",
        plugin_formats="VST3",
    )
    defaults.update(kwargs)
    return ProjectSpec(**defaults)


class TestRenderContextAcceptsSpec(unittest.TestCase):
    def test_build_context_accepts_spec(self):
        from core import render_context
        from core.project_spec import ProjectSpec

        spec = _make_spec()
        ctx = render_context.build_context(spec)
        self.assertEqual(ctx["projectName"], "MyPlugin")
        self.assertEqual(ctx["projectDisplayName"], "My Plugin")

    def test_build_tokens_accepts_spec(self):
        from core import render_context

        spec = _make_spec()
        tokens = render_context.build_tokens(spec)
        self.assertEqual(tokens["PROJECT_NAME"], "MyPlugin")
        self.assertEqual(tokens["PROJECT_DISPLAY_NAME"], "My Plugin")


class TestProjectGeneratorAcceptsSpec(unittest.TestCase):
    def test_generate_signature_accepts_spec(self):
        import inspect

        from core.project_generator import ProjectGenerator

        sig = inspect.signature(ProjectGenerator.generate)
        params = list(sig.parameters)
        self.assertIn("spec", params)
        self.assertNotIn("values", params)
        self.assertNotIn("config", params)


class TestProjectWriterAtomicWrite(unittest.TestCase):
    def _make_writer(self, project_dir: Path):
        from core.project_writer import ProjectWriter

        templates = Path(__file__).resolve().parent.parent / "Templates"
        return ProjectWriter(templates, project_dir)

    def test_write_creates_sidecar(self):
        from core import render_context
        from core.project_writer import ProjectWriter

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "MyPlugin"
            spec = _make_spec(destination_dir=tmp)
            writer = self._make_writer(dest)
            ctx = render_context.build_context(spec)
            tokens = render_context.build_tokens(spec)
            writer.write(ctx, tokens, spec)
            sidecar = dest / ".luthier.json"
            self.assertTrue(sidecar.exists())
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual(data["projectName"], "MyPlugin")

    def test_write_atomic_cleans_tmp_on_failure(self):
        from core.project_spec import ProjectSpec
        from core.project_writer import ProjectWriter

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "MyPlugin"
            spec = _make_spec(destination_dir=tmp)
            writer = ProjectWriter(Path("/nonexistent"), dest)
            try:
                writer.write({}, {}, spec)
            except Exception:
                pass
            tmp_path = dest.parent / (dest.name + ".tmp")
            self.assertFalse(tmp_path.exists(), "temp dir must be cleaned up on failure")
            self.assertFalse(dest.exists(), "dest must not exist when write failed cleanly")

    def test_write_no_tmp_dir_leftover_on_success(self):
        from core import render_context

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "MyPlugin"
            spec = _make_spec(destination_dir=tmp)
            writer = self._make_writer(dest)
            ctx = render_context.build_context(spec)
            tokens = render_context.build_tokens(spec)
            writer.write(ctx, tokens, spec)
            tmp_path = dest.parent / (dest.name + ".tmp")
            self.assertFalse(tmp_path.exists())


class TestProjectReaderReturnsSpec(unittest.TestCase):
    def test_read_project_returns_project_spec(self):
        from core import project_reader
        from core.project_spec import ProjectSpec

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "MyPlugin"
            spec = _make_spec(destination_dir=tmp)
            from core import render_context
            from core.project_writer import ProjectWriter

            templates = Path(__file__).resolve().parent.parent / "Templates"
            writer = ProjectWriter(templates, dest)
            ctx = render_context.build_context(spec)
            tokens = render_context.build_tokens(spec)
            writer.write(ctx, tokens, spec)
            result = project_reader.read_project(dest)
            self.assertIsInstance(result, ProjectSpec)
            self.assertEqual(result.project_name, "MyPlugin")

    def test_read_project_nonexistent_returns_none(self):
        from core import project_reader

        result = project_reader.read_project(Path("/nonexistent/path"))
        self.assertIsNone(result)


class TestNoQtImport(unittest.TestCase):
    def _qt_modules_before(self):
        return {k for k in sys.modules if "PySide6" in k or "PyQt" in k}

    def test_project_generator_no_qt(self):
        before = self._qt_modules_before()
        import core.project_generator  # noqa: F401

        after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
        self.assertEqual(before, after, f"Qt modules leaked: {after - before}")

    def test_project_writer_no_qt(self):
        before = self._qt_modules_before()
        import core.project_writer  # noqa: F401

        after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
        self.assertEqual(before, after, f"Qt modules leaked: {after - before}")

    def test_project_reader_no_qt(self):
        before = self._qt_modules_before()
        import core.project_reader  # noqa: F401

        after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
        self.assertEqual(before, after, f"Qt modules leaked: {after - before}")
