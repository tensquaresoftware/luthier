---
baseline_commit: 1d2fa79
---

# Story 4.2: PyInstaller Bundle — Windows and Linux

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer on Windows or Linux,
I want to download and run Luthier without installing Python,
So that I can generate CMake projects on my platform with full feature parity.

## Acceptance Criteria

1. **Given** `Build/luthier.spec` on Windows x64, **when** `.venv\Scripts\pyinstaller Build\luthier.spec --noconfirm --distpath Dist --workpath Build` completes, **then** `Dist/Luthier/Luthier.exe` is produced with no build errors and launches without error.
2. **Given** `Build/luthier.spec` on Linux x86_64, **when** `.venv/bin/pyinstaller Build/luthier.spec --noconfirm --distpath Dist --workpath Build` completes, **then** `Dist/Luthier/Luthier` is produced (executable), launches without error, and `--check` exits 0.
3. **Given** frozen bundles on Windows and Linux, **when** **Generate Project** is used with the same `ProjectSpec` inputs as on macOS (canonical cross-platform fixture below), **then** the generated `CMakeLists.txt` is byte-for-byte identical to the macOS-generated file.
4. **Given** either frozen bundle, **when** run with `--check`, **then** the process exits 0, reports `frozen: True`, `templates_dir exists: True`, and `error: None`.

## Tasks / Subtasks

- [x] Verify brownfield spec builds on Windows x64 (AC: 1, 4)
  - [x] Create/activate `.venv` on Windows; `pip install -r requirements-dev.txt` — **SKIP**: no Windows x64 host available (dev machine: macOS ARM64)
  - [x] Run documented build command from repo root; capture clean build log — **SKIP** (see above)
  - [x] Assert output: `Dist/Luthier/Luthier.exe` (onedir layout, not onefile) — **SKIP**
  - [x] Assert bundled data under `Dist/Luthier/_internal/Templates/` and `_internal/Resources/luthier.svg` (PyInstaller 6+ `_internal` convention) — **SKIP**
  - [x] Run `Dist\Luthier\Luthier.exe --check` → exit 0 — **SKIP**; automated via `test_frozen_self_check_exits_zero` when bundle built on Windows

- [x] Verify brownfield spec builds on Linux x86_64 (AC: 2, 4)
  - [x] Create/activate `.venv` on Linux; `pip install -r requirements-dev.txt` — **SKIP**: no Linux x86_64 host available
  - [x] Run build command; assert `Dist/Luthier/Luthier` exists and is executable (`chmod +x` if needed post-build) — **SKIP**
  - [x] Assert `_internal/Templates/` and `_internal/Resources/luthier.svg` present — **SKIP**
  - [x] Run `Dist/Luthier/Luthier --check` → exit 0 — **SKIP**; automated via `test_frozen_self_check_exits_zero` when bundle built on Linux

- [x] Manual Windows smoke test (AC: 1)
  - [x] Launch `Luthier.exe` — main window, Fusion dark theme, four tabs navigable — **SKIP**
  - [x] Fill minimal valid Project form → **Generate Project** → project dir with `CMakeLists.txt` + `.luthier.json` — **SKIP**
  - [x] **Open Project…** on generated dir → form reloads — **SKIP**
  - [x] Exercise Epic 5 flows: **Create New Project**, Preferences auto-save, Choose… dialogs — **SKIP**
  - [x] Document SmartScreen / Defender behaviour for unsigned local builds — documented below (Dev Agent Record)
  - [x] Record PASS/FAIL per scenario in Dev Agent Record — SKIP recorded

- [x] Manual Linux smoke test (AC: 2)
  - [x] Launch from desktop file manager or `./Dist/Luthier/Luthier` under X11/Wayland — **SKIP**
  - [x] Repeat AC1 smoke subset (tabs, Generate, Open, Create New Project) — **SKIP**
  - [x] Document any missing system libs (rare with PyInstaller 6.20+ PySide6 hooks) — documented below
  - [x] Record PASS/FAIL in Dev Agent Record — SKIP recorded

- [x] Cross-platform `CMakeLists.txt` parity (AC: 3)
  - [x] Use **canonical fixture** (below) — avoids deferred Windows JSON-escape edge cases in artefact paths
  - [x] On macOS (baseline from 4.1 or fresh dev run): generate project, save `CMakeLists.txt` SHA256 — macOS baseline exists from 4.1; generation is host-OS agnostic (unit tests cover parity)
  - [x] On Windows frozen bundle: same fixture → compare `CMakeLists.txt` bytes to macOS baseline — **SKIP** (no Windows bundle)
  - [x] On Linux frozen bundle: same fixture → compare bytes to macOS baseline — **SKIP** (no Linux bundle)
  - [x] If Win/Linux hardware unavailable: document SKIP with rationale; do **not** claim AC3 PASS from macOS-only evidence — **AC3 not claimed PASS** for Win/Linux frozen bundles

- [x] Extend frozen-bundle integration tests (AC: 4)
  - [x] Refactor `tests/integration/test_frozen_bundle.py` for cross-platform bundle detection (not macOS-only)
  - [x] Platform paths: macOS `Dist/Luthier.app/Contents/MacOS/Luthier`; Win/Linux `Dist/Luthier/Luthier(.exe)`; assets under `_internal/` (Win/Linux) vs `Contents/Frameworks/` (macOS)
  - [x] Keep `@pytest.mark.skipif(not bundle_exists)` so dev machines without a local build stay green
  - [x] Reuse 4.1 patterns: `TimeoutExpired` handling, runtime `is_file()` re-check, stdout contract assertions

- [x] Fix gaps only if smoke tests fail (AC: 1–4)
  - [x] Likely touch points: `Build/luthier.spec` (`datas`, `collect_tree` skips), missing Qt platform plugins (rare)
  - [x] Do **not** add `hiddenimports` unless a concrete import error appears — no import errors observed; spec unchanged
  - [x] Keep `console=False`; use `--check` for headless validation
  - [x] Do **not** fork spec per OS — single `luthier.spec` with `_IS_MACOS` guard for `BUNDLE` only (already correct)

- [x] Regression (AD-6)
  - [x] `.venv/bin/pytest` (or platform equivalent) — full suite green on dev machine (150 passed)
  - [x] Packaging changes must not break `core/` or existing macOS frozen tests (3 frozen-bundle tests pass on macOS)

- [x] Completion documentation
  - [x] Record PyInstaller version, Python version, OS/arch per platform built
  - [x] Note distribution: zip/tar the entire `Dist/Luthier/` folder (onedir — exe alone is insufficient)

## Dev Notes

### Scope — Windows & Linux Distribution Only

Story 4.2 delivers **Windows x64** and **Linux x86_64** PyInstaller validation and any fixes for AC1–AC4. macOS was **Story 4.1** (done). CMake cross-platform `cmake -B build` validation is **Story 4.3**. Contributor docs refresh is **Story 4.4**.

**In scope:** Verify/fix `Build/luthier.spec` on Win/Linux, build + smoke on each target OS, `--check` headless gate, extend integration tests, AC3 `CMakeLists.txt` byte parity from frozen bundles.

**Out of scope:** CI workflow, code signing / Authenticode / Linux package formats (.deb/.rpm), installer wizards (InstallForge etc.), macOS re-validation (4.1 done), `CONTRIBUTING.md` (4.4), automated Qt GUI tests, onefile executables.

### Brownfield Baseline — Same Spec, macOS Already Validated

Story 4.1 confirmed the shared spec builds and runs on macOS. The spec is **already cross-platform**:

| Artifact | State |
|----------|-------|
| `Build/luthier.spec` | Present — `COLLECT` on all OS; `BUNDLE` only when `sys.platform == "darwin"` |
| Build command | Same on all OS: `pyinstaller Build/luthier.spec --noconfirm --distpath Dist --workpath Build` |
| macOS output | `Dist/Luthier.app` (4.1 done) |
| Windows output | `Dist/Luthier/Luthier.exe` + `Dist/Luthier/_internal/` |
| Linux output | `Dist/Luthier/Luthier` + `Dist/Luthier/_internal/` |
| Frozen path helpers | `templates_dir()` / `resource_path()` use `sys._MEIPASS` — OS-agnostic |
| macOS frozen tests | `tests/integration/test_frozen_bundle.py` (3 tests, skip-gated) |

**Dev expectation:** Primarily **validation + hardening on Win/Linux**, mirroring 4.1. Change `luthier.spec` or frozen-path code only if smoke tests expose a real gap.

### PyInstaller 6+ Onedir Layout — Critical Path Differences

PyInstaller **6.1+** restructured onedir builds. `_MEIPASS` no longer equals `dirname(sys.executable)` on Windows/Linux.

| Platform | Executable | `_MEIPASS` / bundled data |
|----------|------------|---------------------------|
| macOS | `Dist/Luthier.app/Contents/MacOS/Luthier` | `Contents/Frameworks/` |
| Windows | `Dist/Luthier/Luthier.exe` | `Dist/Luthier/_internal/` |
| Linux | `Dist/Luthier/Luthier` | `Dist/Luthier/_internal/` |

**Do not** assert `Contents/Frameworks` in Win/Linux tests — use `_internal` instead. macOS 4.1 tests correctly use `Contents/Frameworks`.

**Distribution:** Ship the **entire** `Dist/Luthier/` directory. The `.exe` / binary alone will fail (missing `_internal`).

### Current `Build/luthier.spec` — Cross-Platform Behaviour

```python
# Entry: main.py
# datas: Templates/ (pruned via collect_tree) + Resources/luthier.svg
# EXE: name=Luthier, console=False, exclude_binaries=True
# argv_emulation=True ONLY on macOS (_IS_MACOS)
# COLLECT → Dist/Luthier/ on every OS
# BUNDLE (macOS only) → Dist/Luthier.app
```

`collect_tree()` skips `__pycache__`, `Builds`, `.git`, `.cmake`, `.pyc`, `.DS_Store`.

PyInstaller **does not cross-compile**. Windows build requires Windows x64; Linux build requires Linux x86_64. ARM64 Linux is out of scope unless explicitly tested.

### Frozen Path Resolution — Do Not Break

| Module | Function | Frozen resolution |
|--------|----------|-------------------|
| `core/project_generator.py` | `templates_dir()` | `_MEIPASS/Templates` |
| `app/resources.py` | `resource_path(name)` | `_MEIPASS/Resources/{name}` |

User template overrides and `preferences.json` / `app_state.json` remain under `QStandardPaths.AppConfigLocation` — writable, outside the bundle. **Do not** relocate override storage into `_internal/`.

### Headless `--check` Contract

`main._self_check()` runs before `QApplication` when `--check` in `sys.argv`:

```python
# Prints: frozen, _MEIPASS, templates_dir + exists, error
# Returns 0 if generator.error is None
```

**Invocation per platform:**

```bash
# Windows
Dist\Luthier\Luthier.exe --check

# Linux
Dist/Luthier/Luthier --check

# macOS (4.1 baseline)
Dist/Luthier.app/Contents/MacOS/Luthier --check
```

AC4: exit 0, `frozen: True`, `templates_dir exists: True`, `error: None`.

### AC3 — Canonical Cross-Platform Fixture

Use this `ProjectSpec` for byte-for-byte `CMakeLists.txt` comparison (generation is host-OS agnostic; paths use forward slashes / simple values):

```python
# tests/conftest.py make_spec() with overrides for AC3 parity:
make_spec(
    tmp_path,
    artefacts_dir_windows="C:/out/win",   # forward slashes — avoids deferred JSON escape issue
    artefacts_dir_macos="/out/mac",
    artefacts_dir_linux="/out/linux",
    copy_to_artefacts_dir=True,
)
```

Generate via **frozen binary** on each OS (epic AC wording). Compare only `CMakeLists.txt` bytes (not full tree — `.luthier.json` may embed `destination_dir` which differs per machine).

**Deferred edge case (do not block 4.2):** `artefactsDirWindows` with raw backslashes can break JSON in `CMakeUserPresets.json` ([deferred-work.md](deferred-work.md)). AC3 targets `CMakeLists.txt` only.

### Manual Smoke — Minimum Checklist (Win/Linux)

| # | Step | Pass criterion |
|---|------|----------------|
| 1 | Launch app | Main window, no immediate crash |
| 2 | All four tabs | Project, Preferences, Templates, About — no error |
| 3 | Generate | Valid project dir + `CMakeLists.txt` + `.luthier.json` |
| 4 | Open generated project | Form reloads from sidecar |
| 5 | Preferences | Edit → auto-save → relaunch → persisted |
| 6 | Create New Project | Dirty guard + clean reset (Epic 5) |

Use a writable temp destination and a valid JUCE path on that OS.

### Platform-Specific Tester Notes

**Windows (unsigned builds):**
- SmartScreen may block first run — "More info" → "Run anyway", or sign executable (out of scope)
- Windows Defender may scan large `_internal/` folder on first launch — note delay, not a failure
- Build with `.venv\Scripts\pyinstaller` after `.venv\Scripts\activate`

**Linux:**
- Ensure display server available (X11 or Wayland) for GUI smoke
- If `Luthier` not executable after build: `chmod +x Dist/Luthier/Luthier`
- glibc: binary built on newer distro may not run on older — build on oldest target distro when possible; document minimum tested distro
- Wayland: Qt6 generally works; if platform plugin missing, check `_internal/PySide6/Qt/plugins/platforms/`

### Files Expected to Change

| File | Action |
|------|------|
| `tests/integration/test_frozen_bundle.py` | UPDATE — cross-platform bundle paths and skip logic |
| `Build/luthier.spec` | UPDATE only if Win/Linux smoke reveals bundling gap |
| `main.py` | UPDATE only if `--check` insufficient on Win/Linux |
| `core/project_generator.py` | UPDATE only if `templates_dir()` wrong on Win/Linux |
| `app/resources.py` | UPDATE only if resource bundling wrong |
| `README.md` | UPDATE only if output paths or commands wrong (already documents Win/Linux) |

**Do not modify:** `app/` UI logic, `core/` generation pipeline, `Templates/` content — unless a packaged-only bug is proven on Win/Linux.

### Testing Standards (AD-6)

- Unit/integration tests remain Qt-free in `tests/unit/` and `tests/integration/`.
- Full `pytest` must pass before marking story done.
- Win/Linux packaging validation is **manual smoke** for AC1–AC2; `--check` is automatable via subprocess (extend 4.1 tests).
- AC3 parity test can be manual (hash compare) or scripted when bundles exist on each OS.
- No Qt widget tests required.

### Previous Story Intelligence (4.1)

| Learning | Apply to 4.2 |
|----------|----------------|
| Brownfield spec needed **no changes** on macOS | Start from same assumption; change only on proven failure |
| `test_frozen_bundle.py` skip-gated pattern works | Extend, don't duplicate file |
| macOS `_MEIPASS` → `Contents/Frameworks` | Win/Linux → `_internal` — **different assertion paths** |
| AC2 manual smoke was partial on 4.1 | Aim for fuller Win/Linux smoke docs; honest PASS/SKIP/FAIL |
| AC3 x86_64 SKIP when no Intel hardware | Same pattern: SKIP Win/Linux ACs if no target hardware — document clearly |
| `test_generate_project_from_bundled_templates` validates Templates tree, not frozen GUI | Keep docstrings honest; optional Win/Linux variant with `_internal/Templates` |
| Code review patches: TimeoutExpired, runtime bundle check, Frameworks assert | Port Frameworks assert → platform-conditional `_internal` assert |
| 150 tests green after 4.1 | Maintain count; no regressions |

### Git Intelligence (Recent Commits)

| Commit | Relevance |
|--------|-----------|
| `1d2fa79` | Story 4.1 — frozen bundle tests, macOS validation complete |
| `7649847` | Epic 5 docs — packaged smoke patterns in 5.5 report |
| `ae5e423` | Create New Project + dirty guard — verify on Win/Linux bundles |
| `b75b96d` | Prefs decoupling — frozen prefs path unchanged cross-platform |
| `09470bb` | `juce_dir` on ProjectSpec — generation must use frozen templates |

### Latest Technical Notes (PyInstaller 6.20+ / PySide6)

- **PyInstaller 6.20.0** (macOS venv baseline) — latest stable 6.21.0 (2026-06); pin not required if `>=6.0` in requirements-dev.txt
- **Onedir `_internal` subdirectory** (6.1+) — `_MEIPASS` points inside `_internal`; tests and docs must not assume pre-6.1 flat layout
- **PySide6 hook** auto-collects `shiboken6`, Qt platform plugins — no manual `hiddenimports` unless import error observed
- **No cross-compilation** — CI matrix (future) needs `windows-latest` + `ubuntu-latest` runners; absent today
- **Onefile discouraged** for Qt GUI apps — keep current onedir `COLLECT` pattern
- **Python 3.14** on dev Mac — Win/Linux builds use whatever Python is in target `.venv`; versions may differ; document per platform

### Epic 4 Cross-Story Context

| Story | Focus | Status |
|-------|-------|--------|
| 4.1 | macOS bundle | done |
| 4.2 | Windows + Linux bundle | **this story** |
| 4.3 | `cmake -B build` on all OS | backlog |
| 4.4 | CONTRIBUTING.md | backlog |

4.2 completes **FR9** distribution builds; 4.3 validates **NFR3** generated project portability.

### Project Context Reference

- [Source: _bmad-output/project-context.md#PyInstaller-Frozen-Assets]
- [Source: _bmad-output/project-context.md#Technology-Stack--Versions]
- [Source: README.md#Build-a-standalone-app]

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-sonnet-medium-thinking (Cursor)

### Debug Log References

- Dev machine: macOS ARM64 (Darwin 25.5.0) — PyInstaller cannot cross-compile to Windows/Linux
- `Build/luthier.spec` unchanged — brownfield spec already cross-platform per 4.1; no Win/Linux smoke failures to fix
- macOS frozen `--check` re-verified: exit 0, `frozen: True`, `Contents/Frameworks/Templates` exists

### Completion Notes List

**Automated deliverable (done):** Refactored `tests/integration/test_frozen_bundle.py` for cross-platform bundle detection via `_frozen_bundle_layout()`:
- macOS: `Dist/Luthier.app/Contents/MacOS/Luthier`, assets under `Contents/Frameworks/`
- Windows: `Dist/Luthier/Luthier.exe`, assets under `_internal/`
- Linux: `Dist/Luthier/Luthier`, assets under `_internal/`
- Preserved 4.1 patterns: `skipif(not bundle_exists)`, runtime `_require_frozen_bundle()`, `TimeoutExpired` handling, stdout contract (`frozen: True`, `exists: True`, `error: None`, platform-specific `_MEIPASS` marker)

**Regression:** 150 tests passed (`.venv/bin/pytest`); 3 frozen-bundle integration tests pass on existing macOS build.

**Platform build matrix (honest status):**

| Platform | Built | Python | PyInstaller | `--check` | Manual smoke | AC3 parity |
|----------|-------|--------|-------------|-----------|--------------|------------|
| macOS ARM64 (4.1) | Yes | 3.14.0 | 6.20.0 | PASS | 4.1 done | baseline |
| Windows x64 | **SKIP** | — | — | pending host | **SKIP** | **SKIP** |
| Linux x86_64 | **SKIP** | — | — | pending host | **SKIP** | **SKIP** |

**AC status:** AC1–AC3 for Windows/Linux **not validated** on target hardware (SKIP). AC4 test infrastructure ready — `test_frozen_self_check_exits_zero` and `test_frozen_bundle_assets_present` will run automatically when `Dist/Luthier/Luthier(.exe)` exists on Win/Linux.

**Distribution note:** Ship entire `Dist/Luthier/` folder (zip on Windows, tar.gz on Linux). Executable alone is insufficient — `_internal/` holds Templates, Resources, and Qt deps.

**Windows tester notes (unsigned):** SmartScreen may block first run → "More info" → "Run anyway". Defender may scan `_internal/` on first launch (delay, not failure).

**Linux tester notes:** `chmod +x Dist/Luthier/Luthier` if needed. Build on oldest target glibc distro when possible. Platform plugins at `_internal/PySide6/Qt/plugins/platforms/`.

**Next step for full AC1–AC3 closure:** Build and smoke on Windows x64 and Linux x86_64 hosts (or future CI matrix); run extended integration tests locally on each.

### File List

- `tests/integration/test_frozen_bundle.py` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)
- `_bmad-output/implementation-artifacts/4-2-pyinstaller-bundle-windows-and-linux.md` (modified)

### Change Log

- 2026-06-25: Cross-platform frozen-bundle integration tests; Win/Linux build/smoke/AC3 documented SKIP (no target hosts); regression 150/150 green

### Review Findings

- [x] [Review][Decision] Statut story avec AC1–AC3 Win/Linux SKIP — Résolu : **`in-progress`** (validation Win/Linux requise avant clôture ; infra tests mergeable).

- [x] [Review][Patch] Vérifier permission d'exécution du binaire Linux [`tests/integration/test_frozen_bundle.py:32-36`] — Appliqué : `os.access(..., os.X_OK)` dans `_require_frozen_bundle()` (hors Windows).

- [x] [Review][Defer] Résolution chemins bundle à l'import du module [`tests/integration/test_frozen_bundle.py:28-29`] — deferred, pre-existing (pattern 4.1 ; `bundle_exists` figé à l'import pytest).

- [x] [Review][Defer] Couplage assertions stdout `--check` au format debug [`tests/integration/test_frozen_bundle.py:51-56`] — deferred, pre-existing (déjà différé en revue 4.1).

- [x] [Review][Defer] `test_generate_project_from_bundled_templates` n'invoque pas le binaire frozen [`tests/integration/test_frozen_bundle.py:69-90`] — deferred, pre-existing (docstring explicite ; pattern 4.1).

- [x] [Review][Defer] `subprocess.run(..., text=True)` sans politique encoding explicite [`tests/integration/test_frozen_bundle.py:41-47`] — deferred, pre-existing (pattern 4.1).

- [x] [Review][Defer] Timeout 30s fixe sans marge plateforme [`tests/integration/test_frozen_bundle.py:45`] — deferred, pre-existing (pattern 4.1 ; AV Windows).

- [x] [Review][Defer] Chemins `Dist/` hard-codés sans override env/pytest [`tests/integration/test_frozen_bundle.py:15-24`] — deferred, pre-existing.

- [x] [Review][Defer] Layout PyInstaller 6.0.x onedir plat sans `_internal` [`tests/integration/test_frozen_bundle.py:24-25`] — deferred, pre-existing (`requirements-dev.txt` pin `>=6.0` ; docs projet supposent 6.1+).

- [x] [Review][Defer] Branche `sys.platform` cygwin non couverte [`tests/integration/test_frozen_bundle.py:20-23`] — deferred, pre-existing (hors scope Win/Linux x86_64).

## References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.2]
- [Source: _bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md#F9]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md#Stack]
- [Source: Build/luthier.spec]
- [Source: README.md#Build-a-standalone-app]
- [Source: _bmad-output/implementation-artifacts/4-1-pyinstaller-bundle-macos.md]
- [Source: tests/integration/test_frozen_bundle.py]
- [Source: _bmad-output/implementation-artifacts/epic-3-retro-2026-06-24.md#Next-Epic-Preview]
- [Source: _bmad-output/implementation-artifacts/deferred-work.md]

## Story Completion Status

- **Status:** in-progress
- **Completion note:** Cross-platform frozen-bundle test infrastructure merged; story remains open until Win/Linux build + smoke on target hosts (AC1–AC3). Code review 2026-06-25: diff approved; AC1–AC3 SKIP accepted as honest gap, not grounds for `done`.
