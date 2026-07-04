"""AD-8 guard: core modules must not import Qt on first load."""

import importlib
import sys

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "core.project_generator",
        "core.project_writer",
    ],
)
def test_core_module_import_does_not_load_qt(module):
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    importlib.import_module(module)
    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
