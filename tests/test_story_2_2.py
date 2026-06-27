"""Tests for story 2-2: CMake Regex Fallback for Legacy Projects."""

import re
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from tests.test_story_2_1 import _all_files, _make_spec


def _write_project(tmp: str, spec=None):
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


class TestCmakeFallback(unittest.TestCase):
    def test_cmake_fallback_without_sidecar(self):
        from core import project_reader

        with tempfile.TemporaryDirectory() as tmp:
            dest, original = _write_project(tmp)
            (dest / ".luthier.json").unlink()
            result = project_reader.read_project_result(dest)
            self.assertIsNotNone(result.spec)
            self.assertEqual(result.missing_fields, ())
            for field in fields(original):
                self.assertEqual(
                    getattr(result.spec, field.name),
                    getattr(original, field.name),
                    msg=field.name,
                )

    def test_cmake_fallback_round_trip(self):
        from core import project_reader
        from core.project_generator import ProjectGenerator

        with tempfile.TemporaryDirectory() as tmp:
            spec = _make_spec(destination_dir=tmp)
            generator = ProjectGenerator()
            project_dir = generator.generate(spec)
            before = _all_files(project_dir)
            (project_dir / ".luthier.json").unlink()

            loaded = project_reader.read_project_result(project_dir)
            self.assertIsNotNone(loaded.spec)
            self.assertEqual(loaded.missing_fields, ())
            project_dir = generator.generate(loaded.spec)
            after = _all_files(project_dir)

            self.assertEqual(set(before), set(after))
            for rel in before:
                self.assertEqual(before[rel], after[rel], msg=str(rel))

    def test_partial_cmake_returns_none_with_missing_fields(self):
        from core import project_reader

        with tempfile.TemporaryDirectory() as tmp:
            dest, _ = _write_project(tmp)
            (dest / ".luthier.json").unlink()
            cmake = dest / "CMakeLists.txt"
            text = cmake.read_text(encoding="utf-8")
            text = re.sub(r'^\s*COMPANY_NAME\s+"[^"]*"\s*$', "", text, flags=re.MULTILINE)
            cmake.write_text(text, encoding="utf-8")

            result = project_reader.read_project_result(dest)
            self.assertIsNone(result.spec)
            self.assertIn("Company Name", result.missing_fields)

    def test_no_cmakelists_returns_none(self):
        from core import project_reader

        with tempfile.TemporaryDirectory() as tmp:
            result = project_reader.read_project_result(Path(tmp))
            self.assertIsNone(result.spec)
            self.assertEqual(result.missing_fields, ())

    def test_legacy_project_configuration_cmake(self):
        from core import project_reader

        legacy_copy_config = """\
set(USER_COPY_TO_SYSTEM_FOLDERS ON)
set(USER_COPY_TO_ARTEFACTS_DIR OFF)
set(COPY_TO_SYSTEM_FOLDERS ${USER_COPY_TO_SYSTEM_FOLDERS} CACHE BOOL "Copy plugins to system folders after build (all OS)")
set(COPY_TO_ARTEFACTS_DIR ${USER_COPY_TO_ARTEFACTS_DIR} CACHE BOOL "Copy build outputs to central artefacts folder (organized by platform/architecture)")
set(ARTEFACTS_DIR_WINDOWS "C:\\legacy\\win")
set(ARTEFACTS_DIR_MACOS "/legacy/mac")
set(ARTEFACTS_DIR_LINUX "/legacy/linux")
"""
        with tempfile.TemporaryDirectory() as tmp:
            dest, original = _write_project(tmp)
            (dest / ".luthier.json").unlink()
            cmake = dest / "CMakeLists.txt"
            text = cmake.read_text(encoding="utf-8")
            text = re.sub(
                r"# =+\n# PLUGIN COPY CONFIGURATION.*?set\(ARTEFACTS_DIR_LINUX.*?\)\n",
                "",
                text,
                count=1,
                flags=re.DOTALL,
            )
            cmake.write_text(text, encoding="utf-8")
            (dest / "project-configuration.cmake").write_text(legacy_copy_config, encoding="utf-8")

            result = project_reader.read_project_result(dest)
            self.assertIsNotNone(result.spec)
            self.assertEqual(result.missing_fields, ())
            self.assertTrue(result.spec.copy_to_system_folders)
            self.assertFalse(result.spec.copy_to_artefacts_dir)
            self.assertEqual(result.spec.artefacts_dir_windows, "C:\\legacy\\win")
            self.assertEqual(result.spec.artefacts_dir_macos, "/legacy/mac")
            self.assertEqual(result.spec.artefacts_dir_linux, "/legacy/linux")
            self.assertEqual(result.spec.project_name, original.project_name)


if __name__ == "__main__":
    unittest.main()
