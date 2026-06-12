# PyInstaller spec for Luthier (macOS .app). Build: pyinstaller build/luthier.spec
import os
import sys

PROJECT_ROOT = os.path.dirname(SPECPATH)
sys.path.insert(0, PROJECT_ROOT)
from core.generator_bridge import default_generator_root

GEN = str(default_generator_root())

_SKIP_DIRS = {"__pycache__", "Builds", ".git", ".cmake"}
_SKIP_FILES = {".DS_Store"}


def collect_tree(src_root, dest_prefix):
    """Collect a directory tree into PyInstaller datas, pruning build cruft."""
    entries = []
    for root, dirs, files in os.walk(src_root):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        rel = os.path.relpath(root, src_root)
        dest = dest_prefix if rel == "." else os.path.join(dest_prefix, rel)
        for name in files:
            if name in _SKIP_FILES or name.endswith(".pyc"):
                continue
            entries.append((os.path.join(root, name), dest))
    return entries


datas = (
    collect_tree(os.path.join(GEN, "Generator"), "generator/Generator")
    + collect_tree(os.path.join(GEN, "Templates"), "generator/Templates")
    + [
        (os.path.join(GEN, "generator-configuration.py"), "generator"),
        (os.path.join(GEN, "project-configuration.cmake"), "generator"),
        (os.path.join(PROJECT_ROOT, "resources", "luthier.svg"), "resources"),
    ]
)

# The generator is loaded dynamically (importlib), so PyInstaller cannot see its
# stdlib imports. Declare the ones Luthier itself does not import.
_GENERATOR_HIDDEN = ["platform", "shutil", "importlib.util", "typing", "re", "pathlib"]

a = Analysis(
    [os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    datas=datas,
    hiddenimports=_GENERATOR_HIDDEN,
    noarchive=False,
)
_IS_MACOS = sys.platform == "darwin"

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Luthier",
    console=False,
    argv_emulation=_IS_MACOS,
)
# COLLECT builds the one-folder distribution (dist/Luthier/) on every OS:
# the Luthier executable plus its dependencies and bundled data. On Windows it
# yields Luthier.exe, on Linux the Luthier binary. macOS additionally wraps it
# into a .app. PyInstaller does not cross-compile: build on each target OS.
coll = COLLECT(exe, a.binaries, a.datas, name="Luthier")
if _IS_MACOS:
    app = BUNDLE(
        coll,
        name="Luthier.app",
        icon=None,
        bundle_identifier="com.tensquaresoftware.luthier",
    )
