#!/usr/bin/env python3
"""Build the standalone Luthier bundle (PyInstaller) for the current OS."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _venv_python() -> Path:
    if sys.platform == "win32":
        candidate = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = PROJECT_ROOT / ".venv" / "bin" / "python"
    if candidate.is_file():
        return candidate
    raise SystemExit(
        "Virtual environment not found (.venv). Create it first, then install dev deps:\n"
        "  python -m venv .venv\n"
        "  pip install -r requirements-dev.txt"
    )


def _bundle_paths() -> tuple[Path, Path]:
    """Return (bundle_root, executable) for the host platform."""
    if sys.platform == "darwin":
        bundle = PROJECT_ROOT / "dist" / "Luthier.app"
        return bundle, bundle / "Contents" / "MacOS" / "Luthier"
    bundle = PROJECT_ROOT / "dist" / "Luthier"
    if sys.platform == "win32":
        return bundle, bundle / "Luthier.exe"
    return bundle, bundle / "Luthier"


def _platform_label() -> str:
    if sys.platform == "darwin":
        return "macOS"
    if sys.platform == "win32":
        return "Windows"
    return "Linux"


def _run(cmd: list[str | Path], *, step: str) -> None:
    print(f"\n==> {step}")
    print("    ", " ".join(str(part) for part in cmd))
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the standalone Luthier bundle for the current OS."
    )
    parser.add_argument(
        "--skip-icons",
        action="store_true",
        help="Skip icon regeneration (build fails if platform icon is missing).",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip the headless --check smoke test after the build.",
    )
    args = parser.parse_args()

    python = _venv_python()
    print(f"Building Luthier dist on {_platform_label()} ({sys.platform})")

    if not args.skip_icons:
        _run(
            [python, "build/generate_icons.py"],
            step="Regenerate app icons",
        )

    _run(
        [
            python,
            "-m",
            "PyInstaller",
            "build/luthier.spec",
            "--noconfirm",
            "--distpath",
            "dist",
            "--workpath",
            "build",
        ],
        step="PyInstaller bundle",
    )

    bundle_root, binary = _bundle_paths()
    if not binary.is_file():
        raise SystemExit(f"Build finished but executable not found: {binary}")

    print(f"\nBuild complete: {bundle_root}")

    if args.skip_check:
        return 0

    _run([binary, "--check"], step="Headless smoke test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
