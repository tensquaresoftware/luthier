"""Shared helpers for integration and pytest tests."""

import os
import re
import shutil
from dataclasses import fields
from pathlib import Path

from core.paths import host_workspace_field_key
from core.project_spec import ProjectSpec
from core.plugin_settings import TYPE_INSTRUMENT

_LEGACY_COPY_CONFIG = """\
set(USER_COPY_TO_SYSTEM_FOLDERS ON)
set(USER_COPY_TO_ARTEFACTS_DIR OFF)
set(COPY_TO_SYSTEM_FOLDERS ${USER_COPY_TO_SYSTEM_FOLDERS} CACHE BOOL "Copy plugins to system folders after build (all OS)" FORCE)
set(COPY_TO_ARTEFACTS_DIR ${USER_COPY_TO_ARTEFACTS_DIR} CACHE BOOL "Copy build outputs to central artefacts folder (organized by platform/architecture)" FORCE)
set(ARTEFACTS_DIR_WINDOWS "C:\\legacy\\win")
set(ARTEFACTS_DIR_MACOS "/legacy/mac")
set(ARTEFACTS_DIR_LINUX "/legacy/linux")
"""

_WORKSPACE_JSON_TO_ATTR = {
    "destinationDirWindows": "destination_dir_windows",
    "destinationDirMacos": "destination_dir_macos",
    "destinationDirLinux": "destination_dir_linux",
    "juceDirWindows": "juce_dir_windows",
    "juceDirMacos": "juce_dir_macos",
    "juceDirLinux": "juce_dir_linux",
}


def workspace_attr(json_key: str) -> str:
    return _WORKSPACE_JSON_TO_ATTR[json_key]


def _default_spec_fields(tmp_path) -> dict:
    fields_dict = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        project_version="1.0.0",
        manufacturer_name="Acme",
        manufacturer_code="Acme",
        plugin_code="Mypl",
        company_copyright="Copyright 2026",
        company_website="https://acme.example",
        company_email="dev@acme.example",
        destination_dir_windows="",
        destination_dir_macos="",
        destination_dir_linux="",
        juce_dir_windows="",
        juce_dir_macos="",
        juce_dir_linux="",
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
    host_dest = host_workspace_field_key("destination")
    fields_dict[workspace_attr(host_dest)] = str(tmp_path)
    return fields_dict


def make_spec(tmp_path, **kwargs) -> ProjectSpec:
    defaults = _default_spec_fields(tmp_path)
    if "destination_dir" in kwargs:
        dest = kwargs.pop("destination_dir")
        host_dest = host_workspace_field_key("destination")
        defaults[workspace_attr(host_dest)] = dest
    if "juce_dir" in kwargs:
        juce = kwargs.pop("juce_dir")
        host_juce = host_workspace_field_key("juce")
        defaults[workspace_attr(host_juce)] = juce
    defaults.update(kwargs)
    return ProjectSpec(**defaults)


def all_files(root: Path) -> dict[Path, bytes]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root)] = path.read_bytes()
    return result


def assert_spec_equal(actual: ProjectSpec, expected: ProjectSpec) -> None:
    for field in fields(expected):
        assert getattr(actual, field.name) == getattr(expected, field.name), field.name


def assert_trees_equal(before: dict[Path, bytes], after: dict[Path, bytes]) -> None:
    assert set(before) == set(after)
    for rel in before:
        assert before[rel] == after[rel], str(rel)


def install_legacy_project_configuration_cmake(project_dir: Path) -> None:
    (project_dir / ".luthier.json").unlink()
    cmake = project_dir / "CMakeLists.txt"
    text = cmake.read_text(encoding="utf-8")
    text = re.sub(
        r"# =+\n# PLUGIN COPY CONFIGURATION.*?set\(ARTEFACTS_DIR_LINUX.*?\)\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    cmake.write_text(text, encoding="utf-8")
    (project_dir / "project-configuration.cmake").write_text(
        _LEGACY_COPY_CONFIG, encoding="utf-8"
    )


def write_project(tmp_path, spec, *, overrides=None) -> tuple[Path, ProjectSpec]:
    from core import render_context
    from core.project_generator import templates_dir
    from core.project_writer import ProjectWriter

    spec = spec or make_spec(tmp_path)
    dest = Path(spec.host_destination_dir()) / spec.project_name
    writer = ProjectWriter(templates_dir(), dest, overrides)
    writer.write(
        render_context.build_context(spec),
        render_context.build_tokens(spec),
        spec,
    )
    return dest, spec


def generate_project(
    tmp_path, spec=None, *, overrides=None
) -> tuple[Path, ProjectSpec]:
    from core.project_generator import ProjectGenerator

    spec = spec or make_spec(tmp_path)
    generator = ProjectGenerator(overrides=overrides)
    project_dir = generator.generate(spec)
    return project_dir, spec


def cmake_available() -> bool:
    return shutil.which("cmake") is not None


def juce_dir_for_tests() -> str | None:
    env_path = os.environ.get("JUCE_DIR", "").strip()
    if env_path and Path(env_path).is_dir():
        return env_path
    for candidate in (
        "/Applications/JUCE",
        "C:/Program Files/JUCE",
        "/usr/local/JUCE",
    ):
        if Path(candidate).is_dir():
            return candidate
    return None


def canonical_cross_platform_spec(tmp_path, **kwargs) -> ProjectSpec:
    juce = kwargs.pop("juce_dir", None) or juce_dir_for_tests() or "/Applications/JUCE"
    return make_spec(
        tmp_path,
        juce_dir=juce,
        artefacts_dir_windows="C:/out/win",
        artefacts_dir_macos="/out/mac",
        artefacts_dir_linux="/out/linux",
        copy_to_artefacts_dir=True,
        **kwargs,
    )
