"""Tests for story 2-1: Project Reload via .luthier.json Sidecar."""

import tempfile
import unittest
from dataclasses import fields
from pathlib import Path


def _make_spec(**kwargs):
    from core.plugin_settings import TYPE_INSTRUMENT
    from core.project_spec import ProjectSpec

    defaults = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        project_version="1.0.0",
        manufacturer_name="Acme",
        manufacturer_code="Acme",
        plugin_code="Mypl",
        company_copyright="Copyright 2026",
        company_website="https://acme.example",
        company_email="dev@acme.example",
        destination_dir=str(Path(tempfile.gettempdir())),
        plugin_type=TYPE_INSTRUMENT,
        plugin_formats="VST3",
        cxx_standard="C++20",
        preprocessor_definitions="FOO=1",
        header_search_paths="/extra/include",
        copy_to_system_folders=True,
        copy_to_artefacts_dir=False,
        artefacts_dir_windows="C:/out",
        artefacts_dir_macos="/out/mac",
        artefacts_dir_linux="/out/linux",
    )
    defaults.update(kwargs)
    return ProjectSpec(**defaults)


def _all_files(root: Path) -> dict[Path, bytes]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root)] = path.read_bytes()
    return result


class TestReadSidecar(unittest.TestCase):
    def _write_project(self, tmp: str, spec=None):
        from core import render_context
        from core.project_writer import ProjectWriter

        dest_parent = Path(tmp)
        spec = spec or _make_spec(destination_dir=tmp)
        dest = dest_parent / spec.project_name
        templates = Path(__file__).resolve().parent.parent / "templates"
        writer = ProjectWriter(templates, dest)
        ctx = render_context.build_context(spec)
        tokens = render_context.build_tokens(spec)
        writer.write(ctx, tokens, spec)
        return dest, spec

    def test_read_sidecar_returns_all_fields(self):
        from core import project_reader

        with tempfile.TemporaryDirectory() as tmp:
            dest, original = self._write_project(tmp)
            result = project_reader.read_project(dest)
            self.assertIsNotNone(result)
            for field in fields(original):
                self.assertEqual(
                    getattr(result, field.name),
                    getattr(original, field.name),
                    msg=field.name,
                )

    def test_malformed_sidecar_returns_none_no_cmake_fallback(self):
        from core import project_reader

        with tempfile.TemporaryDirectory() as tmp:
            dest, _ = self._write_project(tmp)
            (dest / ".luthier.json").write_text("{not valid json", encoding="utf-8")
            self.assertTrue((dest / "CMakeLists.txt").exists())
            self.assertIsNone(project_reader.read_project(dest))

    def test_sidecar_non_dict_returns_none(self):
        from core import project_reader

        with tempfile.TemporaryDirectory() as tmp:
            dest, _ = self._write_project(tmp)
            for payload in ('"hello"', "[]"):
                with self.subTest(payload=payload):
                    (dest / ".luthier.json").write_text(payload, encoding="utf-8")
                    self.assertIsNone(project_reader.read_project(dest))


class TestRoundTrip(unittest.TestCase):
    def test_round_trip_empty_diff(self):
        from core import project_reader
        from core.project_generator import ProjectGenerator

        with tempfile.TemporaryDirectory() as tmp:
            spec = _make_spec(destination_dir=tmp)
            generator = ProjectGenerator()
            project_dir = generator.generate(spec)
            before = _all_files(project_dir)

            loaded = project_reader.read_project(project_dir)
            self.assertIsNotNone(loaded)
            project_dir = generator.generate(loaded)
            after = _all_files(project_dir)

            self.assertEqual(set(before), set(after))
            for rel in before:
                self.assertEqual(before[rel], after[rel], msg=str(rel))


if __name__ == "__main__":
    unittest.main()
