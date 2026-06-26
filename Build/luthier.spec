# PyInstaller spec for Luthier. Build: pyinstaller Build/luthier.spec
import os
import sys

PROJECT_ROOT = os.path.dirname(SPECPATH)

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
    collect_tree(os.path.join(PROJECT_ROOT, "Templates"), "Templates")
    + [
        (os.path.join(PROJECT_ROOT, "Resources", "luthier-logo.png"), "Resources"),
        (os.path.join(PROJECT_ROOT, "Resources", "luthier-logo@2x.png"), "Resources"),
        (os.path.join(PROJECT_ROOT, "Resources", "luthier.png"), "Resources"),
    ]
)

a = Analysis(
    [os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    datas=datas,
    noarchive=False,
)
_IS_MACOS = sys.platform == "darwin"
_IS_WINDOWS = sys.platform == "win32"
if _IS_MACOS:
    _icon_name = "luthier.icns"
elif _IS_WINDOWS:
    _icon_name = "luthier.ico"
else:
    _icon_name = "luthier.png"
_icon = os.path.join(PROJECT_ROOT, "Resources", _icon_name)
if not os.path.isfile(_icon):
    raise SystemExit(
        f"Missing app icon Resources/{_icon_name}. "
        "Run: .venv/bin/python Build/generate_icons.py"
    )

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Luthier",
    console=False,
    argv_emulation=_IS_MACOS,
    icon=_icon if not _IS_MACOS else None,
)
# COLLECT builds the one-folder distribution (Dist/Luthier/) on every OS:
# the Luthier executable plus its dependencies and bundled data. On Windows it
# yields Luthier.exe, on Linux the Luthier binary. macOS additionally wraps it
# into a .app. PyInstaller does not cross-compile: build on each target OS.
coll = COLLECT(exe, a.binaries, a.datas, name="Luthier")
if _IS_MACOS:
    app = BUNDLE(
        coll,
        name="Luthier.app",
        icon=_icon,
        bundle_identifier="com.tensquaresoftware.luthier",
    )
