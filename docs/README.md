# Luthier documentation

Index of published documentation for the [Luthier](https://github.com/tensquaresoftware/luthier) repository.

## User documentation

End-user manuals (English and French).

| Document | Language | Description |
|----------|----------|-------------|
| [user-manual.md](user/user-manual.md) | English | Full user manual — context, UI, workflows, troubleshooting |
| [manuel-utilisateur.md](user/manuel-utilisateur.md) | French | Manuel utilisateur complet |

## Developer documentation

Contributor setup, architecture, and release process.

| Document | Description |
|----------|-------------|
| [architecture.md](dev/architecture.md) | Three-layer design, module contracts, rendering pipeline |
| [release-guide.md](dev/release-guide.md) | GitHub Release assembly with `publish/prepare-release.py` |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Dev environment, pytest, CI, publishing flow |

## QA documentation

Manual test procedures (reusable) and archived reports from past release cycles.

### Procedures (reusable)

Run these before tagging a pre-release or final semver release. Download artefacts from the GitHub Release — do not build locally unless debugging the pipeline.

| Document | Scope |
|----------|-------|
| [smoke-test-three-os.md](qa/smoke-test-three-os.md) | Full smoke test — macOS, Windows, Linux |
| [smoke-test-windows-addon.md](qa/smoke-test-windows-addon.md) | Windows supplement — VS presets, regen with `.git/`, D2 clone |

### Archive

Historical checklists and completed smoke-test reports. Kept for traceability; not required for day-to-day contributing.

| Folder | Contents |
|--------|----------|
| [qa/archive/v1.0.0-beta/](qa/archive/v1.0.0-beta/) | Pre-v1.0.0 beta QA checklists |
| [qa/archive/v1.0.0/](qa/archive/v1.0.0/) | Completed 1.0.0 release smoke-test reports |

## Automated tests

Unit and integration tests live in the repository root [`tests/`](../tests/) directory (pytest). They are separate from manual QA procedures in `docs/qa/`.
