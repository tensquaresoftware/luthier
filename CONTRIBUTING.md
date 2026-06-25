# Contributing to Luthier

Thank you for contributing to Luthier. This guide walks you through environment setup, running the test suite, launching the app, and building a standalone bundle.

For architecture and module contracts, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). For end-user documentation, see [docs/USER-MANUAL.md](docs/USER-MANUAL.md).

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
git clone https://github.com/tensquaresoftware/Luthier.git && cd Luthier

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Dev dependencies (PySide6 + pytest + PyInstaller)
pip install -r requirements-dev.txt

# 4. Test suite (158 tests collected; frozen-bundle tests skip when Dist/ is absent)
.venv/bin/pytest                     # Windows: .venv\Scripts\pytest

# 5. Headless template check (exit 0, error: None)
.venv/bin/python main.py --check     # Windows: .venv\Scripts\python main.py --check

# 6. Launch GUI
.venv/bin/python main.py
```

**Observed timings (macOS, maintainer machine, 2026-06-26):**

| Step | Duration |
|------|----------|
| `pip install -r requirements-dev.txt` | ~1–2 min (first install; depends on network) |
| `pytest` | ~18 s (156 passed, 2 skipped) |
| `main.py --check` | <1 s |

Steps 2–5 (venv → pip → pytest → `--check`) fit comfortably within the 15-minute onboarding goal.

## Build a standalone bundle (optional, extended step)

PyInstaller bundles templates and resources into a self-contained app. Build on each target OS — there is no cross-compilation.

```bash
.venv/bin/pyinstaller Build/luthier.spec --noconfirm --distpath Dist --workpath Build
```

On Windows, activate the venv first (`.venv\Scripts\activate`) and run `pyinstaller Build\luthier.spec`.

| OS | Output | Headless check |
|----|--------|----------------|
| macOS | `Dist/Luthier.app` | `Dist/Luthier.app/Contents/MacOS/Luthier --check` |
| Windows | `Dist/Luthier/Luthier.exe` + `_internal/` | `Dist\Luthier\Luthier.exe --check` |
| Linux | `Dist/Luthier/Luthier` + `_internal/` | `Dist/Luthier/Luthier --check` |

PyInstaller 6+ uses an onedir layout on Windows and Linux (`_internal/` subdirectory). A full bundle build may take several minutes — treat it as an optional extended step after the core dev loop.

## Test suite

```bash
.venv/bin/pytest
```

- **158 tests** collected (`pytest --collect-only`).
- **No display required** — default suite runs headless; most tests exercise `core/` directly (a few unit tests import lightweight `app/` field-spec helpers).
- **`tests/unit/`** — primarily pure `core/` logic; some modules use `tmp_path` for file I/O.
- **`tests/integration/`** — round-trip generation with pytest's `tmp_path` fixture.
- **`tests/integration/test_frozen_bundle.py`** — validates the PyInstaller bundle when `Dist/` exists; **skipped automatically** when no bundle is present. Do not be alarmed by these skips during normal development.
- Legacy `tests/test_story_*.py` unittest modules are still collected by pytest — no need to run them separately.
- Configuration: `pytest.ini` sets `testpaths = tests` and `pythonpath = .`.

Cross-platform CMake validation (`cmake -B build` on generated projects) is covered by Story 4.3 integration tests — see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#testing).

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

If `Rules/process-clean-code.md` is present in your checkout, follow it for the full process. Comments document **non-obvious why** only — never restate what the code does.

### Language conventions

- **Commit messages:** English.
- **UI strings and documentation:** English (NFR5).
- **Python identifiers:** `snake_case` for functions/variables; `PascalCase` for classes.
- **CMake template keys:** `camelCase` (`{projectName}`, `{cxxStandard}`, …).
- **File I/O:** always `encoding="utf-8"`.

### Layer boundaries

- `core/` must **never** import from `app/` (AD-8).
- `app/` must **never** import from `Templates/` directly — all generation goes through `core/`.
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture.

## Folder casing

| Path | Casing | Contents |
|------|--------|----------|
| `docs/` | lowercase | Markdown documentation (USER-MANUAL, ARCHITECTURE) |
| `Docs/` | PascalCase | Images (`Luthier.png`) |
| `Templates/` | PascalCase | Bundled JUCE project templates |
| `Build/` | PascalCase | `luthier.spec` |
| `app/`, `core/` | lowercase | Python packages |

Do not conflate `docs/` and `Docs/` in links.

## Product reference (`_bmad-output/`)

The `_bmad-output/` folder is the BMad planning and implementation artifact store — **authoritative for product intent**. Contributor onboarding docs live in `docs/` and this file; do not duplicate PRD or epics content here.

| Document | Path |
|----------|------|
| PRD | [`_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md`](_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md) |
| Architecture Spine (canonical) | [`_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md`](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md) |
| Architecture Explained (companion) | [`_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-EXPLAINED.md`](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-EXPLAINED.md) |
| Epics & stories | [`_bmad-output/planning-artifacts/epics.md`](_bmad-output/planning-artifacts/epics.md) |
| Project context (AI/dev quick reference) | [`_bmad-output/project-context.md`](_bmad-output/project-context.md) |

> **Note:** `ARCHITECTURE-EXPLAINED.md` Decision 5 (prefs.save after Open/Generate) and Decision 7 (juce_dir in Preferences only) are **superseded**. Use **ARCHITECTURE-SPINE** and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for AD-5 and AD-7.

## Further reading

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — three-layer design, module contracts, two-pass rendering
- [docs/USER-MANUAL.md](docs/USER-MANUAL.md) — end-user manual
- [README.md](README.md) — project overview and quick start

## CI

There is no GitHub Actions workflow yet (Epic 3 retrospective action item). All verification is local: `pytest`, `main.py --check`, and optional PyInstaller build.
