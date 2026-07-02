#!/usr/bin/env python3
"""Prepare and publish Luthier GitHub releases (Option B: X.Y.Z everywhere, no v prefix)."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLISH_DIR = Path(__file__).resolve().parent
GITHUB_REPO = "tensquaresoftware/luthier"
RELEASES_ROOT = PROJECT_ROOT / "_local" / "releases"
TEMPLATE_DIR = PUBLISH_DIR / "templates"

PLATFORM_ASSETS = ("macos", "windows", "linux")
CHECKSUM_FILE = "SHA256SUMS.txt"
NOTES_FILE = "RELEASE_NOTES.md"


@dataclass(frozen=True)
class AppVersion:
    version: str
    revision_date: str


@dataclass(frozen=True)
class ReleasePaths:
    version: str
    release_dir: Path

    @property
    def macos_archive(self) -> Path:
        return self.release_dir / f"Luthier-{self.version}-macos.zip"

    @property
    def windows_archive(self) -> Path:
        return self.release_dir / f"Luthier-{self.version}-windows.zip"

    @property
    def linux_archive(self) -> Path:
        return self.release_dir / f"Luthier-{self.version}-linux.zip"

    @property
    def docs_archive(self) -> Path:
        return self.release_dir / f"Luthier-{self.version}-docs.zip"

    @property
    def checksums(self) -> Path:
        return self.release_dir / CHECKSUM_FILE

    @property
    def notes(self) -> Path:
        return self.release_dir / NOTES_FILE

    def platform_archive(self, platform: str) -> Path:
        return {
            "macos": self.macos_archive,
            "windows": self.windows_archive,
            "linux": self.linux_archive,
        }[platform]

    def distributable_archives(self) -> tuple[Path, ...]:
        return (
            self.macos_archive,
            self.windows_archive,
            self.linux_archive,
            self.docs_archive,
        )


def read_app_version(root: Path = PROJECT_ROOT) -> AppVersion:
    text = (root / "app" / "version.py").read_text(encoding="utf-8")
    version_match = re.search(r'^VERSION = "([^"]+)"', text, re.MULTILINE)
    date_match = re.search(r'^REVISION_DATE = "([^"]+)"', text, re.MULTILINE)
    if not version_match or not date_match:
        raise SystemExit("Could not read VERSION / REVISION_DATE from app/version.py")
    return AppVersion(version=version_match.group(1), revision_date=date_match.group(1))


def host_platform() -> str:
    if sys.platform == "darwin":
        return "macos"
    if sys.platform == "win32":
        return "windows"
    return "linux"


def render_template(name: str, version: str) -> str:
    path = TEMPLATE_DIR / name
    if not path.is_file():
        raise SystemExit(f"Missing template: {path}")
    return path.read_text(encoding="utf-8").replace("{{VERSION}}", version)


def ensure_release_dir(paths: ReleasePaths) -> None:
    paths.release_dir.mkdir(parents=True, exist_ok=True)


def dist_bundle_root(root: Path = PROJECT_ROOT) -> Path:
    if sys.platform == "darwin":
        return root / "dist" / "Luthier.app"
    return root / "dist" / "Luthier"


def _zip_directory(
    archive_path: Path,
    readme_text: str,
    *,
    macos_app: Path | None = None,
    folder: Path | None = None,
) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", readme_text)
        if macos_app is not None:
            for item in sorted(macos_app.rglob("*")):
                if item.is_dir():
                    continue
                arcname = Path("Luthier.app") / item.relative_to(macos_app)
                zf.write(item, arcname=str(arcname).replace("\\", "/"))
        elif folder is not None:
            for item in sorted(folder.rglob("*")):
                if item.is_dir():
                    continue
                arcname = Path("Luthier") / item.relative_to(folder)
                zf.write(item, arcname=str(arcname).replace("\\", "/"))
        else:
            raise ValueError("Either macos_app or folder must be provided")


def pack_host(paths: ReleasePaths, *, force: bool) -> None:
    platform = host_platform()
    archive = paths.platform_archive(platform)
    if archive.is_file() and not force:
        raise SystemExit(f"Archive already exists: {archive}\nUse --force to overwrite.")

    bundle = dist_bundle_root()
    if not bundle.exists():
        raise SystemExit(
            f"Build output not found: {bundle}\nRun publish/build-dist.py on this machine first."
        )

    readme = render_template(f"README-{platform}.template.txt", paths.version)
    print(f"Packing {platform} -> {archive.name}")

    if platform == "macos":
        _zip_directory(archive, readme, macos_app=bundle)
    else:
        _zip_directory(archive, readme, folder=bundle)

    size_mb = archive.stat().st_size / (1024 * 1024)
    print(f"  Created {archive} ({size_mb:.1f} MiB)")


def import_archive(
    paths: ReleasePaths,
    platform: str,
    source: Path,
    *,
    force: bool,
) -> None:
    if platform not in PLATFORM_ASSETS:
        raise SystemExit(f"Unknown platform: {platform!r} (expected macos|windows|linux)")

    source = source.resolve()
    if not source.is_file():
        raise SystemExit(f"Source file not found: {source}")

    target = paths.platform_archive(platform)
    if target.is_file() and not force:
        raise SystemExit(f"Archive already exists: {target}\nUse --force to overwrite.")

    ensure_release_dir(paths)
    shutil.copy2(source, target)
    print(f"Imported {source.name} -> {target}")


def create_docs_archive(paths: ReleasePaths, *, force: bool) -> None:
    archive = paths.docs_archive
    if archive.is_file() and not force:
        print(f"Docs archive already exists: {archive.name} (use --force to overwrite)")
        return

    manuals = (
        ("user-manual.md", PROJECT_ROOT / "docs" / "user" / "user-manual.md"),
        (
            "manuel-utilisateur.md",
            PROJECT_ROOT / "docs" / "user" / "manuel-utilisateur.md",
        ),
    )
    for _, path in manuals:
        if not path.is_file():
            raise SystemExit(f"Missing manual: {path}")

    ensure_release_dir(paths)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for arcname, path in manuals:
            zf.write(path, arcname=arcname)

    print(f"Created {archive.name}")


def write_release_notes(paths: ReleasePaths, *, force: bool) -> None:
    if paths.notes.is_file() and not force:
        print(f"{NOTES_FILE} already exists (use --force to overwrite)")
        return

    ensure_release_dir(paths)
    paths.notes.write_text(
        render_template("RELEASE_NOTES.template.md", paths.version),
        encoding="utf-8",
    )
    print(f"Created {paths.notes.name}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(paths: ReleasePaths) -> None:
    missing = [p.name for p in paths.distributable_archives() if not p.is_file()]
    if missing:
        raise SystemExit(f"Cannot write checksums - missing archives: {', '.join(missing)}")

    lines = [f"{sha256_file(path)}  {path.name}" for path in paths.distributable_archives()]
    ensure_release_dir(paths)
    paths.checksums.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {paths.checksums.name}")


def verify_release(paths: ReleasePaths) -> None:
    errors: list[str] = []

    for path in paths.distributable_archives():
        if not path.is_file():
            errors.append(f"Missing archive: {path.name}")
        elif path.stat().st_size == 0:
            errors.append(f"Empty archive: {path.name}")

    if not paths.checksums.is_file():
        errors.append(f"Missing {CHECKSUM_FILE}")
    else:
        for line in paths.checksums.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                errors.append(f"Invalid checksum line: {line!r}")
                continue
            expected, name = parts
            file_path = paths.release_dir / name
            if not file_path.is_file():
                errors.append(f"Checksum references missing file: {name}")
                continue
            if sha256_file(file_path) != expected:
                errors.append(f"Checksum mismatch: {name}")

    if errors:
        print("Verification FAILED:")
        for err in errors:
            print(f"  * {err}")
        raise SystemExit(1)

    print("Verification OK - all archives present and checksums match.")


def status(paths: ReleasePaths) -> None:
    ensure_release_dir(paths)
    print(f"Version      : {paths.version}")
    print(f"Release dir  : {paths.release_dir}")
    print()
    for label, path in (
        ("macOS   ", paths.macos_archive),
        ("Windows ", paths.windows_archive),
        ("Linux   ", paths.linux_archive),
        ("Docs    ", paths.docs_archive),
        ("Checksums", paths.checksums),
        ("Notes   ", paths.notes),
    ):
        if path.is_file():
            size = path.stat().st_size / (1024 * 1024)
            print(f"  [OK] {label}  {path.name} ({size:.1f} MiB)")
        else:
            print(f"  [ ] {label}  {path.name}")


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("==>", " ".join(str(part) for part in cmd))
    subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, check=True)


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def publish_release(
    paths: ReleasePaths,
    *,
    yes: bool,
    prerelease: bool,
    skip_tag_push: bool,
) -> None:
    verify_release(paths)

    if not paths.notes.is_file():
        raise SystemExit(f"Missing {NOTES_FILE}. Run: publish/prepare-release.py finalize")

    if _git_output("status", "--porcelain"):
        raise SystemExit("Git working tree is not clean. Commit or stash changes first.")

    tag = paths.version
    if subprocess.run(["git", "rev-parse", tag], cwd=PROJECT_ROOT, capture_output=True).returncode == 0:
        raise SystemExit(f"Git tag already exists: {tag}")

    remote_tag = subprocess.run(
        ["git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if remote_tag.stdout.strip():
        raise SystemExit(f"Remote tag already exists: {tag}")

    print()
    print(f"Ready to publish Luthier {paths.version}")
    print(f"  Tag     : {tag}")
    print(f"  Assets  : {paths.release_dir}")
    print(f"  Notes   : {paths.notes.name}")
    if prerelease:
        print("  Mode    : pre-release")
    print()

    if not yes:
        answer = input("Continue? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Aborted.")
            return

    _run(["git", "tag", "-a", tag, "-m", f"Luthier {paths.version}"])
    if not skip_tag_push:
        _run(["git", "push", "origin", tag])

    cmd = [
        "gh",
        "release",
        "create",
        tag,
        "--repo",
        GITHUB_REPO,
        "--title",
        f"Luthier {paths.version}",
        "--notes-file",
        str(paths.notes),
        *[str(p) for p in paths.distributable_archives()],
        str(paths.checksums),
    ]
    if prerelease:
        cmd.append("--prerelease")

    _run(cmd, cwd=paths.release_dir)
    print()
    print(f"Published: https://github.com/{GITHUB_REPO}/releases/tag/{tag}")


def build_paths(version: str | None) -> ReleasePaths:
    app = read_app_version()
    resolved = version or app.version
    if version and version != app.version:
        print(
            f"Warning: --version {version} differs from app/version.py ({app.version})",
            file=sys.stderr,
        )
    return ReleasePaths(version=resolved, release_dir=RELEASES_ROOT / resolved)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare Luthier release assets under _local/releases/X.Y.Z/ "
            "(semver without v prefix everywhere)."
        ),
    )
    parser.add_argument(
        "--version",
        help="Release version X.Y.Z (default: app/version.py)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing archives or RELEASE_NOTES.md",
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Show which release assets exist")

    sub.add_parser("pack", help="Pack dist/ for the current OS into the release folder")

    imp = sub.add_parser(
        "import",
        help="Copy an external platform archive into the release folder",
    )
    imp.add_argument("platform", choices=PLATFORM_ASSETS)
    imp.add_argument("source", type=Path)

    sub.add_parser(
        "finalize",
        help="Create docs zip, RELEASE_NOTES.md, and SHA256SUMS.txt",
    )
    sub.add_parser("verify", help="Verify archives and checksums")

    pub = sub.add_parser(
        "publish",
        help="Create git tag, push, and GitHub release via gh",
    )
    pub.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    pub.add_argument("--prerelease", action="store_true", help="Mark as pre-release on GitHub")
    pub.add_argument(
        "--skip-tag-push",
        action="store_true",
        help="Create tag locally but do not push (for dry runs)",
    )

    args = parser.parse_args()
    paths = build_paths(args.version)

    if args.command == "status":
        status(paths)
    elif args.command == "pack":
        pack_host(paths, force=args.force)
    elif args.command == "import":
        import_archive(paths, args.platform, args.source, force=args.force)
    elif args.command == "finalize":
        create_docs_archive(paths, force=args.force)
        write_release_notes(paths, force=args.force)
        write_checksums(paths)
        print()
        status(paths)
    elif args.command == "verify":
        verify_release(paths)
    elif args.command == "publish":
        publish_release(
            paths,
            yes=args.yes,
            prerelease=args.prerelease,
            skip_tag_push=args.skip_tag_push,
        )
    else:
        parser.error(f"Unknown command: {args.command}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
