# Contributing to Luthier

Thank you for contributing to Luthier. This guide walks you through environment setup, running the test suite, launching the app, and building a standalone bundle.

For architecture and module contracts, see [_bmad-output/architecture.md](_bmad-output/architecture.md). For end-user documentation, see [docs/user/user-manual.md](docs/user/user-manual.md) (English) or [docs/user/manuel-utilisateur.md](docs/user/manuel-utilisateur.md) (French).

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.11+** | Required. Tested on Python 3.14 (maintainer machine). |
| **Git** | Clone the repository and work on a feature branch. |
| **Platform** | macOS, Windows, or Linux. PyInstaller bundles are built on the target OS only (no cross-compilation). |

No JUCE installation is required to develop Luthier itself — only to build the *generated* plugin projects.

## Quick start (core dev loop)

These steps should complete in **under 15 minutes** on a typical machine (verified on macOS, 2026-06-26).

```bash
# 1. Clone and enter the repo
git clone https://github.com/tensquaresoftware/luthier.git && cd luthier

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Dev dependencies (PySide6 + pytest + PyInstaller)
pip install -r requirements-dev.txt

# 4. Test suite (158 tests collected; frozen-bundle tests skip when dist/ is absent)
.venv/bin/pytest                     # Windows: .venv\Scripts\pytest

# 5. Headless template check (exit 0, error: None)
.venv/bin/python main.py --check     # Windows: .venv\Scripts\python main.py --check

# 6. Launch GUI
.venv/bin/python main.py
```

On **macOS**, `main.py` sets the Dock icon from `resources/icons/luthier.png` during development. The squircle mask comes from `luthier.icns` in `dist/Luthier.app` only after a PyInstaller build. If you see the generic Python icon, you are likely running the interpreter directly without an app icon — relaunch after pulling assets, or open `dist/Luthier.app`.

### App icons

Source artwork: `resources/icons/luthier-icon.png` (**1024×1024**, square, background included — export from Figma at 1x) and `resources/luthier-logo.png` / `luthier-logo@2x.png` (About tab). Generated assets (committed):

| File | Use |
|------|-----|
| `resources/icons/luthier.png` | Qt window/Dock icon in dev; Linux PyInstaller executable |
| `resources/icons/luthier.icns` | macOS `Luthier.app` bundle |
| `resources/icons/luthier.ico` | Windows `Luthier.exe` |

Regenerate after editing `luthier-icon.png`:

```bash
.venv/bin/python build/generate_icons.py
```

PyInstaller **fails fast** if the platform icon file is missing (`build/luthier.spec`). `publish/build-dist.py` regenerates icons before each build; on macOS the generator also produces `.ico` for Windows commits. Run `build/generate_icons.py` manually only when you changed `luthier-icon.png` and are not doing a full bundle build.

**Observed timings (macOS, maintainer machine, 2026-06-26):**

| Step | Duration |
|------|----------|
| `pip install -r requirements-dev.txt` | ~1–2 min (first install; depends on network) |
| `pytest` | ~18 s (156 passed, 2 skipped) |
| `main.py --check` | <1 s |

Steps 2–5 (venv → pip → pytest → `--check`) fit comfortably within the 15-minute onboarding goal.

## Build a standalone bundle (optional, extended step)

PyInstaller bundles templates and resources into a self-contained app. Build on each target OS — there is no cross-compilation. Use **`publish/build-dist.py`** (icons, PyInstaller, and a headless `--check` smoke test):

```bash
.venv/bin/python publish/build-dist.py
```

On Windows: `.venv\Scripts\python.exe publish/build-dist.py`

| OS | Output | Headless check |
|----|--------|----------------|
| macOS | `dist/Luthier.app` | included in `publish/build-dist.py` |
| Windows | `dist/Luthier/Luthier.exe` + `_internal/` | included in `publish/build-dist.py` |
| Linux | `dist/Luthier/Luthier` + `_internal/` | included in `publish/build-dist.py` |

Options: `--skip-icons`, `--skip-check`. There is no separate debug bundle — use `python main.py` for day-to-day development.

PyInstaller 6+ uses an onedir layout on Windows and Linux (`_internal/` subdirectory). A full bundle build may take several minutes — treat it as an optional extended step after the core dev loop. Windows x64 and Linux x86_64 bundles were validated manually in Story 4.2 (2026-06-26).

## Test suite

```bash
.venv/bin/pytest
```

- **158 tests** collected (`pytest --collect-only`).
- **No display required** — default suite runs headless; most tests exercise `core/` directly (a few unit tests import lightweight `app/` field-spec helpers).
- **`tests/unit/`** — primarily pure `core/` logic; some modules use `tmp_path` for file I/O.
- **`tests/integration/`** — round-trip generation with pytest's `tmp_path` fixture.
- **`tests/integration/test_frozen_bundle.py`** — validates the PyInstaller bundle when `dist/` exists; **skipped automatically** when no bundle is present. Do not be alarmed by these skips during normal development.
- Legacy `tests/test_story_*.py` unittest modules are still collected by pytest — no need to run them separately.
- Configuration: `pytest.ini` sets `testpaths = tests` and `pythonpath = .`.

Cross-platform CMake validation (`cmake -B build` on generated projects) is covered by `tests/integration/test_cmake_cross_platform.py` — Windows x64 and Linux x86_64 configure tests run on matching hosts only (`@pytest.mark.skipif` by platform). Validated on all three OS families (2026-06-26). See [_bmad-output/architecture.md](_bmad-output/architecture.md#testing).

## Code style and contribution norms

Luthier follows a mandatory **3-phase process** (Design → Implementation → Auto-review) with hard metric limits (NFR1):

| Metric | Limit |
|--------|-------|
| Function/method | ≤ 15 lines (20 max for pure orchestration) |
| Class | ≤ 200 lines |
| Parameters | ≤ 3 (use a dataclass if more) |
| Cyclomatic complexity | < 5 |
| Indentation levels | ≤ 2 |

Principles: KISS, YAGNI, ETC, DRY/WET, CQS, Boy Scout. Priority when conflicts arise: **correctness > KISS/YAGNI > SOLID > premature DRY**.

If `rules/process-clean-code.md` is present in your checkout, follow it for the full process. Comments document **non-obvious why** only — never restate what the code does.

### Language conventions

- **Commit messages:** English.
- **UI strings and documentation:** English (NFR5).
- **Python identifiers:** `snake_case` for functions/variables; `PascalCase` for classes.
- **CMake template keys:** `camelCase` (`{projectName}`, `{cxxStandard}`, …).
- **File I/O:** always `encoding="utf-8"`.

### Layer boundaries

- `core/` must **never** import from `app/` (AD-8).
- `app/` must **never** import from `templates/` directly — all generation goes through `core/`.
- See [_bmad-output/architecture.md](_bmad-output/architecture.md) for the full architecture.

## Folder casing

| Path | Casing | Contents |
|------|--------|----------|
| `docs/` | lowercase | End-user docs and QA checklists (`user/`, `tests/`) |
| `templates/` | lowercase | Bundled JUCE project templates (`Source/`, `CMake/` stay PascalCase) |
| `resources/` | lowercase | Logos and static assets (`icons/` for app icon files) |
| `build/` | lowercase | `luthier.spec`, PyInstaller workpath |
| `dist/` | lowercase | PyInstaller output (`Luthier.app`, `Luthier/` onedir) |
| `rules/` | lowercase | Local dev rules (gitignored) |
| `app/`, `core/` | lowercase | Python packages |

Do not use a separate `Docs/` folder — keep documentation assets in lowercase `docs/` to avoid case collisions on macOS.

## Product reference (`_bmad-output/`)

The `_bmad-output/` folder is the BMad planning and implementation artifact store — **authoritative for product intent**, including contributor architecture reference (`architecture.md`). End-user and QA docs live in `docs/`; do not duplicate PRD or epics content into either tree.

| Document | Path |
|----------|------|
| PRD | [`_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md`](_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md) |
| Architecture Spine (canonical) | [`_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md`](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md) |
| Architecture Explained (companion) | [`_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-explained.md`](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-explained.md) |
| Epics & stories | [`_bmad-output/planning-artifacts/epics.md`](_bmad-output/planning-artifacts/epics.md) |
| Architecture (contributor reference) | [`_bmad-output/architecture.md`](_bmad-output/architecture.md) |
| Project context (AI/dev quick reference) | [`_bmad-output/project-context.md`](_bmad-output/project-context.md) |

> **Note:** For the narrative companion, see [`architecture-explained.md`](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-explained.md) (Decisions 5–7 include superseded Epic 1 history). AD-5 and AD-7: use **architecture-spine** and [_bmad-output/architecture.md](_bmad-output/architecture.md).

## Further reading

- [_bmad-output/architecture.md](_bmad-output/architecture.md) — three-layer design, module contracts, two-pass rendering
- [docs/user/user-manual.md](docs/user/user-manual.md) — end-user manual (English)
- [docs/user/manuel-utilisateur.md](docs/user/manuel-utilisateur.md) — manuel utilisateur (français)
- [README.md](README.md) — project overview and quick start

## CI

[![pytest](https://github.com/tensquaresoftware/luthier/actions/workflows/pytest.yml/badge.svg)](https://github.com/tensquaresoftware/luthier/actions/workflows/pytest.yml)

Every push and pull request to `main` runs [`.github/workflows/pytest.yml`](.github/workflows/pytest.yml) on `ubuntu-latest`:

1. Install Python 3.11+
2. Install Qt runtime libraries for headless PySide6 (`libegl1`, `libgl1`, `libxkbcommon0`, `libdbus-1-3` on Debian/Ubuntu)
3. Create a venv and `pip install -r requirements-dev.txt`
4. Run `pytest` with `QT_QPA_PLATFORM=offscreen` (unit + integration under `tests/`)

No CMake, JUCE, or PyInstaller build runs in CI. Tests that need those tools skip automatically (`test_cmake_cross_platform.py` without cmake/JUCE; `test_frozen_bundle.py` without a `dist/` bundle).

On Linux, match CI when running tests locally: install the same Qt runtime packages and set `export QT_QPA_PLATFORM=offscreen` before `pytest`.

Local checks beyond CI: `main.py --check` and optional `publish/build-dist.py`.
