---
epic: 10
story: 1
story_key: 10-1-ci-multi-platform-pytest-matrix
depends_on: [7-1]
blocks: []
implementation_order: 1
correct_course_date: 2026-07-09
baseline_commit: HEAD
baseline_workflow: .github/workflows/pytest.yml
---

# Story 10.1: CI Multi-Platform (pytest matrix)

Status: review

<!-- Epic 10 — CI & Release Scope. Extends Story 7.1. Priority: SHOULD (post-v1.0.0). -->

## Story

As a contributor,
I want pytest to run automatically on Linux, Windows, and macOS for every push and pull request,
So that cross-platform regressions are caught in CI without manual re-runs on each OS after every change.

## Context

**Post-v1.0.0 correct course (2026-07-09):** Epics 1–9 are **done**. Story **7.1** delivered `.github/workflows/pytest.yml` on **`ubuntu-latest` only**. Guillaume previously validated logic on macOS, Windows, and Linux manually after changes.

**Mac Intel investigation (closed):** `investigations/macos-x86_64-intel-build-investigation.md` — **Luthier.app on x86_64 is out of scope**. macOS distribution remains **ARM64 only** (Story 4.1). **GitHub `macos-latest` runners are Apple Silicon** — this matches the retained app scope; do **not** plan Story 10.2 or self-hosted Intel runners.

**Generated JUCE projects:** Unchanged — `CMakeUserPresets.json` still includes `macos-debug-x86_64` / `macos-release-x86_64` for plugin builds. CI does not build JUCE projects.

**Planning references:**
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-09-ci-multiplatform.md`
- `_bmad-output/implementation-artifacts/7-1-github-actions-ci-for-pytest.md`
- `_bmad-output/implementation-artifacts/deferred-work.md` — pip/apt cache deferred until pain observed
- `/Volumes/Guillaume/Dev/Documentation/GitHub/Guide-GitHub-Actions.md` — matrix job pattern

### Current workflow baseline (7.1)

```yaml
# .github/workflows/pytest.yml — single leg
runs-on: ubuntu-latest
env:
  QT_QPA_PLATFORM: offscreen
# apt: libegl1 libgl1 libxkbcommon0 libdbus-1-3
# venv + pip install -r requirements-dev.txt + pytest
```

### Test skip behaviour (must preserve)

| Module | Skip condition | CI expectation |
|--------|----------------|----------------|
| `tests/integration/test_cmake_cross_platform.py` | No cmake/JUCE; `@pytest.mark.skipif` by host OS for configure tests | JSON/preset portability tests run on all legs; platform configure tests run only on matching matrix OS |
| `tests/integration/test_frozen_bundle.py` | No `dist/` PyInstaller bundle | Skip on all legs unless bundle committed (not expected) |
| `tests/unit/` | — | Run on all legs |

## Acceptance Criteria

### AC1 — Triggers unchanged

**Given** a push or pull request targeting **`main`**  
**When** GitHub Actions runs  
**Then** the pytest workflow executes (same triggers as Story 7.1)

### AC2 — Three-OS matrix

**Given** the pytest workflow  
**When** it runs  
**Then** jobs execute on **`ubuntu-latest`**, **`windows-latest`**, and **`macos-latest`** via `strategy.matrix`  
**And** each leg uses Python **3.11**, creates a **venv**, installs **`requirements-dev.txt`**, and runs **`pytest`**

### AC3 — Qt runtime per OS

**Given** any matrix leg  
**When** pytest imports PySide6-backed modules  
**Then** `QT_QPA_PLATFORM=offscreen` is set  
**And** platform-appropriate Qt runtime deps are satisfied:
- **Linux:** apt packages from 7.1 (`libegl1`, `libgl1`, `libxkbcommon0`, `libdbus-1-3`) with `DEBIAN_FRONTEND=noninteractive` and `--no-install-recommends`
- **Windows:** PySide6 wheel bundles Qt; no apt/brew step required unless a leg fails import (then document minimal fix in CONTRIBUTING)
- **macOS:** PySide6 wheel bundles Qt; no Homebrew step required unless a leg fails import

### AC4 — macOS runner = Apple Silicon (documented)

**Given** the macOS matrix leg uses **`macos-latest`**  
**Then** workflow YAML comment and **`CONTRIBUTING.md`** state that GitHub-hosted macOS runners are **Apple Silicon**, which aligns with **ARM64-only `Luthier.app`** distribution  
**And** docs do **not** imply Intel Mac CI coverage for the standalone app

### AC5 — Optional-env tests skip cleanly

**Given** CI without CMake, JUCE, or PyInstaller `dist/`  
**When** pytest runs on any leg  
**Then** `test_cmake_cross_platform.py` and `test_frozen_bundle.py` skip as today — **no false failures**  
**And** the matrix job succeeds when all non-skipped tests pass

### AC6 — Failures fail the workflow

**Given** any non-skipped test fails on any matrix leg  
**When** pytest completes  
**Then** that leg exits **non-zero** and the PR check shows **failure**

### AC7 — CONTRIBUTING.md

**Given** Story 10.1 is complete  
**When** a contributor reads **`CONTRIBUTING.md` § CI**  
**Then** it describes the **three-OS matrix**, per-OS Qt notes, and the existing status badge (same workflow file)  
**And** local Linux offscreen instructions from 7.1 remain accurate

## Tasks / Subtasks

- [x] Extend `.github/workflows/pytest.yml` (AC: 1–6)
  - [x] Add `strategy.matrix.os: [ubuntu-latest, windows-latest, macos-latest]`
  - [x] Set `runs-on: ${{ matrix.os }}`
  - [x] Factor venv + pytest step (bash on Linux/macOS; PowerShell or bash on Windows — match repo convention)
  - [x] Conditional Linux apt step (`if: matrix.os == 'ubuntu-latest'`)
  - [x] Set `QT_QPA_PLATFORM: offscreen` at job level
  - [x] Add YAML comment: macOS leg = Apple Silicon runner

- [x] Verify matrix green (AC: 5–6)
  - [x] Push branch; confirm three legs green
  - [x] Confirm skip counts sensible per OS (e.g. Windows configure test runs on windows leg)

- [x] Update `CONTRIBUTING.md` (AC: 7)
  - [x] Replace ubuntu-only wording with matrix description
  - [x] Document Apple Silicon runner note for macOS CI leg

- [x] Regression
  - [x] Local `.venv/bin/pytest` still green on dev machine

## Dev Notes

### Suggested workflow structure

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    env:
      QT_QPA_PLATFORM: offscreen
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Qt runtime dependencies (Linux)
        if: matrix.os == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
            libegl1 libgl1 libxkbcommon0 libdbus-1-3
      - name: Create venv, install dependencies, run pytest
        run: |
          # Platform-specific shell — see 7.1 for Linux/macOS;
          # Windows: python -m venv .venv && .venv\Scripts\pip ...
```

Use **`fail-fast: false`** so one OS failure does not cancel other legs (easier triage).

### Windows venv path

- Pip: `.venv\Scripts\pip`
- Pytest: `.venv\Scripts\pytest`
- Prefer a single step with `shell: bash` on Windows if GitHub bash is acceptable (consistent with many Python projects); otherwise use explicit PowerShell.

### Expected test distribution per leg

| Leg | Extra tests vs ubuntu-only |
|-----|----------------------------|
| `ubuntu-latest` | Linux cmake configure (if cmake+JUCE absent → skip) |
| `windows-latest` | Windows cmake configure (if cmake+JUCE absent → skip); Windows path normalization |
| `macos-latest` | macOS-only cmake dev test (if cmake+JUCE absent → skip); darwin-specific paths |

Most tests (~300+) run identically on all legs.

### Out of scope (do not implement)

- PyInstaller build in CI
- macOS x86_64 / Intel runner / self-hosted MacBook i7
- CMake + JUCE install in CI
- pip/apt cache (deferred — `deferred-work.md`)
- Qt widget tests (AD-6)

### References

- `.github/workflows/pytest.yml` — current 7.1 implementation
- `pytest.ini` — `testpaths = tests`, `pythonpath = .`
- `tests/integration/test_cmake_cross_platform.py` — skip markers by platform
- `tests/integration/test_frozen_bundle.py` — `_require_frozen_bundle()` skip
- `CONTRIBUTING.md` § CI — update target
- Story 7.1 completion notes — Qt apt list, path normalization fixes

## Dev Agent Record

### Agent Model Used

Composer (Cursor)

### Debug Log

- Windows leg failed on first CI run: direct `.venv/Scripts/pip install --upgrade pip` rejected on GHA — fixed with `python -m pip`.
- Windows leg failed on second run: 6 test failures from `C:\` vs `C:/` path mismatch and `~` expansion using `USERPROFILE` not `HOME` — fixed test fixtures in conftest and tilde tests.

### Completion Notes

- ✅ AC1–7 satisfied: triggers unchanged; three-OS matrix with Python 3.11, venv, `requirements-dev.txt`, `pytest`, `QT_QPA_PLATFORM=offscreen`; Linux apt conditional; macOS Apple Silicon documented in workflow comment and CONTRIBUTING.
- Local regression: 313 passed, 3 skipped (~1.1s).
- CI matrix run [29044513527](https://github.com/tensquaresoftware/luthier/actions/runs/29044513527): all three legs green — 310 passed, 6 skipped per leg (cmake/bundle skips as expected).
- PR [#2](https://github.com/tensquaresoftware/luthier/pull/2) on branch `story/10-1-ci-multi-platform-pytest-matrix`.

### File List

- `.github/workflows/pytest.yml` (modified)
- `CONTRIBUTING.md` (modified)
- `tests/conftest.py` (modified)
- `tests/integration/test_startup.py` (modified)
- `tests/unit/test_paths.py` (modified)
- `tests/unit/test_preferences.py` (modified)
- `_bmad-output/implementation-artifacts/10-1-ci-multi-platform-pytest-matrix.md` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

## Change Log

- 2026-07-09: Story created via Correct Course — Epic 10 CI multi-platform matrix; ARM64-only macOS app scope documented.
- 2026-07-09: Story 10.1 implemented — three-OS pytest matrix; Windows test path normalization fixes; CI green on PR #2.
