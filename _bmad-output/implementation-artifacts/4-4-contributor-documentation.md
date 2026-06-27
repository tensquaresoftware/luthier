---
baseline_commit: 08086eb
---

# Story 4.4: Contributor Documentation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a contributor to Luthier,
I want comprehensive setup and contribution documentation,
So that I can configure my dev environment, run the test suite, and build a bundle in under 15 minutes.

## Acceptance Criteria

1. **Given** a new contributor following `CONTRIBUTING.md`, **when** they execute the documented steps, **then** they can: create the venv, install dependencies from `requirements-dev.txt`, run `pytest` with all tests passing, launch the app with `.venv/bin/python main.py`, and build the bundle with the documented PyInstaller command.
2. **Given** the architecture documentation, **when** a contributor reads it, **then** the three-layer diagram (`app/` → `core/` → `Templates/`), each `core/` module's contract (inputs, outputs, invariants), and the two-pass rendering mechanism are documented.
3. **Given** the `_bmad-output/` folder, **when** any team member refers to it, **then** the finalized PRD, Architecture Spine, and Epics documents are present as the authoritative product reference.

## Tasks / Subtasks

- [x] Create `CONTRIBUTING.md` at repo root (AC: 1)
  - [x] Prerequisites: Python 3.11+ (project tested on 3.14), Git, platform notes for macOS / Windows / Linux
  - [x] Step-by-step: `python -m venv .venv` → activate → `pip install -r requirements-dev.txt`
  - [x] Run app: `.venv/bin/python main.py` (macOS/Linux) and `.venv\Scripts\python main.py` (Windows)
  - [x] Headless check: `main.py --check` (same venv python)
  - [x] Test suite: `.venv/bin/pytest` — document expected count (~150 tests) and that frozen-bundle tests skip when `Dist/` absent
  - [x] Build bundle: documented PyInstaller command per platform; output paths table (macOS `.app`, Win/Linux onedir)
  - [x] Clean Code / contribution norms: link to `Rules/process-clean-code.md` if present; otherwise inline NFR1 summary from architecture spine
  - [x] Commit messages in English; UI/docs in English (NFR5)
  - [x] Link to `docs/ARCHITECTURE.md`, `docs/USER-MANUAL.md`, `_bmad-output/` product refs

- [x] Create `docs/ARCHITECTURE.md` (AC: 2)
  - [x] Three-layer mermaid diagram matching ARCHITECTURE-SPINE (strict downward deps; `tests/` → `core/` only)
  - [x] Golden rule: `core/` never imports `app/` (AD-8)
  - [x] `ProjectSpec` as cross-layer contract (AD-1, AD-2) — link to `core/project_spec.py`
  - [x] Two-pass rendering section with file lists from `ProjectWriter`:
    - Pass 1: `rendering.render()` / `{camelCase}` keys — `_RENDERED` files (CMakeLists.txt, CMakeUserPresets.json, .vscode/*.json, README.md)
    - Pass 2: `rendering.render_tokens()` / `@KEY@` — `_TOKENIZED` Source/*.h/cpp
    - Verbatim copy list: `_VERBATIM` (.gitignore, .cursorrules, etc.)
    - CMake literal braces: `${{VAR}}` survives `str.format`
  - [x] Module contract table for every `core/*.py` module (inputs, outputs, invariants) — see Dev Notes table
  - [x] Data-flow summary: form → `ProjectSpec` → `ProjectGenerator.generate()` → `ProjectWriter.write()` → disk + `.luthier.json`
  - [x] Round-trip: `project_reader.read_project()` — sidecar first, CMake regex fallback (AD-3)
  - [x] Preferences / app_state persistence rules (AD-5 revised): Open/Generate never write `preferences.json`
  - [x] `juce_dir` on `ProjectSpec`, Preferences as seed only (AD-7 revised)
  - [x] Explicit note: `ARCHITECTURE-EXPLAINED.md` Decision 5 & 7 are **superseded** — cite ARCHITECTURE-SPINE as canonical

- [x] Update `README.md` (AC: 1)
  - [x] Add prominent link to `CONTRIBUTING.md` for developers
  - [x] Deduplicate: keep user-facing quick start; move dev depth to CONTRIBUTING
  - [x] Align Python invocation with project convention (`.venv/bin/python`, not bare `python main.py` where possible)
  - [x] Preserve existing standalone-app build table (already correct for 4.1/4.2)

- [x] Verify `_bmad-output/` product reference layout (AC: 3)
  - [x] Confirm paths exist and document them in CONTRIBUTING (no file moves required unless missing):
    - PRD: `_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md`
    - Architecture Spine: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md`
    - Epics: `_bmad-output/planning-artifacts/epics.md`
  - [x] Add `_bmad-output/project-context.md` as AI/dev quick-reference (optional but recommended)
  - [x] Do **not** duplicate full PRD/epics content into `docs/` — link only

- [x] Onboarding smoke verification (AC: 1 — 15-minute goal)
  - [x] Walk through CONTRIBUTING steps on a clean venv (or document timed checklist)
  - [x] Record: venv + pip + pytest + `--check` + optional PyInstaller build durations
  - [x] If full PyInstaller build exceeds 15 min alone, document "core dev loop" (venv → pytest → run) as <15 min and bundle build as optional extended step — do not claim false timings

- [x] Regression (documentation-only story)
  - [x] No production code changes expected; if any code touched for doc accuracy, run `.venv/bin/pytest`
  - [x] Spell-check links: relative paths must resolve from repo root

## Dev Notes

### Scope — Documentation Only (NFR4 / Epic 4 Closure)

Story 4.4 delivers **contributor-facing documentation** to satisfy NFR4. It closes the documentation pillar of Epic 4 alongside distribution (4.1–4.2) and CMake validation (4.3).

**In scope:** `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, README cross-links, AC3 verification of `_bmad-output/` artifacts, honest onboarding timing notes.

**Out of scope:** CI workflow (`.github/` still absent), code signing docs, USER-MANUAL rewrite (already PO-validated), automated doc generation, translating docs to French (NFR5: docs in English), Story 4.3 CMake validation procedures (link as "upcoming" if 4.3 still backlog), modifying `_bmad-output/planning-artifacts/*` content (read-only reference).

### Brownfield Baseline — What Already Exists

| Artifact | State | Action |
|----------|-------|--------|
| `README.md` | User-facing features, basic run/build | UPDATE — link CONTRIBUTING; minor command alignment |
| `docs/USER-MANUAL.md` | PO-validated end-user manual | LINK only — do not rewrite |
| `CONTRIBUTING.md` | **Missing** | CREATE |
| `docs/ARCHITECTURE.md` | **Missing** | CREATE |
| `_bmad-output/planning-artifacts/` | PRD, Spine, Epics present | VERIFY + document paths (AC3) |
| `_bmad-output/project-context.md` | AI agent rules, layout, patterns | LINK as dev quick-ref |
| `ARCHITECTURE-EXPLAINED.md` | Narrative companion | **Partially outdated** (AD-5, AD-7) — do not copy stale sections |
| `Rules/process-clean-code.md` | NFR1 clean code rules | LINK if tracked; rules may be gitignored locally |

Stories 4.1 and 4.2 explicitly deferred `CONTRIBUTING.md` to this story. Story 3-1 noted the same.

### Target Onboarding Flow (AC1)

Document this exact sequence (platform variants in parentheses):

```bash
# 1. Clone and enter repo
git clone https://github.com/tensquaresoftware/luthier.git && cd luthier

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Dev dependencies (PySide6 + pytest + PyInstaller)
pip install -r requirements-dev.txt

# 4. Test suite (expect ~150 passed; frozen tests skip without Dist/)
.venv/bin/pytest                     # Windows: .venv\Scripts\pytest

# 5. Headless template check
.venv/bin/python main.py --check     # exit 0, error: None

# 6. Launch GUI
.venv/bin/python main.py

# 7. Build standalone bundle (same OS only — no cross-compile)
.venv/bin/pyinstaller Build/luthier.spec --noconfirm --distpath Dist --workpath Build
```

**Platform outputs** (from README / Stories 4.1–4.2):

| OS | Output | Headless check |
|----|--------|----------------|
| macOS | `Dist/Luthier.app` | `Dist/Luthier.app/Contents/MacOS/Luthier --check` |
| Windows | `Dist/Luthier/Luthier.exe` + `_internal/` | `Dist\Luthier\Luthier.exe --check` |
| Linux | `Dist/Luthier/Luthier` + `_internal/` | `Dist/Luthier/Luthier --check` |

**15-minute goal:** Steps 2–5 should complete in under 15 minutes on a typical dev machine. PyInstaller (step 7) may take longer — document separately.

### `core/` Module Contracts (Required for AC2)

Document each module in `docs/ARCHITECTURE.md` using this schema: **Purpose | Inputs | Outputs | Invariants**.

| Module | Purpose | Inputs | Outputs | Invariants |
|--------|---------|--------|---------|------------|
| `project_spec.py` | Typed cross-layer data model | Field values / JSON dict | `ProjectSpec`, `to_dict()` | No raw dict across boundaries (AD-1); snake_case fields |
| `project_generator.py` | Orchestrates generation | `ProjectSpec`, optional template/override paths | `Path` to project dir | Uses `templates_dir()`; raises via writer on failure |
| `project_writer.py` | Renders + writes project tree | `context`, `tokens`, `ProjectSpec` | Files on disk + `.luthier.json` | Atomic temp-dir rename (AD-4); overrides at write time (AD-9) |
| `project_reader.py` | Reload project into spec | `project_dir: Path` | `Optional[ProjectSpec]`, warnings | Sidecar first; partial CMake → `None` (AD-3) |
| `render_context.py` | Spec → template data | `ProjectSpec` | `build_context()` dict, `build_tokens()` dict | Reads `spec.juce_dir` (AD-7); camelCase template keys |
| `rendering.py` | Template substitution | template str + dict | rendered str | Two mechanisms: `format` vs `@KEY@` replace |
| `validation.py` | Field validators | `str` field value | `(bool, str)` tuple | Pure functions; no I/O |
| `plugin_settings.py` | JUCE flag/category helpers | type strings / flags | dicts, bundle_id, categories | Pure; no side effects |
| `preferences.py` | Global profile JSON | dict / file I/O | `Preferences` object | Save only via app layer (AD-5); factory defaults on first launch |
| `app_state.py` | Last-used parent dir | path strings | `AppState` JSON | Separate from Import/Export profile |
| `templates_store.py` | User C++ template overrides | filename, content | read/write override files | Overrides under `QStandardPaths`; not in ProjectSpec |
| `project_form_state.py` | Dirty guard for Create New Project | form snapshots | bool equality | Used by `app/` only |

### Two-Pass Rendering — Must Document Precisely

From `core/project_writer.py`:

```python
_RENDERED = ("CMakeLists.txt", "CMakeUserPresets.json", ".vscode/settings.json", ...)
_TOKENIZED = ("Source/PluginProcessor.h", "Source/PluginProcessor.cpp", ...)
_VERBATIM = (".vscode/extensions.json", ".cursorrules", ".gitignore", ...)
```

| Pass | Function | Placeholder style | Example files |
|------|----------|-------------------|---------------|
| str.format | `rendering.render()` | `{projectName}`, `{cxxStandard}` | CMakeLists.txt, presets, README.md |
| Token replace | `rendering.render_tokens()` | `@PROJECT_NAME@`, `@PROJECT_DISPLAY_NAME@` | Source/*.h, Source/*.cpp |
| None | direct copy | — | .gitignore, CopyVst3Elevated.ps1 |

Only two C++ tokens exist. C++ templates must remain valid without substitution.

### Architecture Diagram — Copy from Spine, Extend for Tests

Use the mermaid diagram from ARCHITECTURE-SPINE §Design Paradigm. Add `tests/` → `core/` edge. Explicitly show `app/` must **never** import `Templates/` directly.

### `_bmad-output/` Reference Map (AC3)

These files **already exist** — AC3 is verification + documentation, not authoring:

| Document | Path |
|----------|------|
| PRD | `_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md` |
| Architecture Spine | `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md` |
| Architecture Explained (companion) | `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-EXPLAINED.md` |
| Epics & stories | `_bmad-output/planning-artifacts/epics.md` |
| Project context (dev rules) | `_bmad-output/project-context.md` |

CONTRIBUTING should explain `_bmad-output/` is the BMad planning/implementation artifact store — authoritative for product intent; `docs/` is contributor/onboarding entry.

### Stale Content Warning — Do Not Propagate

`ARCHITECTURE-EXPLAINED.md` contains outdated narrative:

- **Decision 5** says `prefs.save()` after every Open/Generate — **wrong** since Epic 5 / AD-5 revision (2026-06-25)
- **Decision 7** says `juce_dir` in Preferences only — **wrong**; now on `ProjectSpec` with Preferences as seed (AD-7 revision)

When writing `docs/ARCHITECTURE.md`, use **ARCHITECTURE-SPINE** and **project-context.md** as sources of truth. Optionally add a one-line staleness note in CONTRIBUTING pointing maintainers to Spine over Explained for AD-5/AD-7.

### Folder Casing Conventions

| Path | Casing | Contents |
|------|--------|----------|
| `docs/` | lowercase | Markdown documentation (USER-MANUAL, ARCHITECTURE) |
| `Docs/` | PascalCase | Images (`Luthier.png`) |
| `Templates/` | PascalCase | Bundled JUCE project templates |
| `Build/` | PascalCase | `luthier.spec` |
| `app/`, `core/` | lowercase | Python packages |

Do not conflate `docs/` and `Docs/` in links.

### Testing Documentation Requirements

From AD-6 and Epic 3:

- **150 tests** collected (as of story creation baseline `08086eb`)
- `tests/unit/` — pure `core/` functions, no Qt
- `tests/integration/` — round-trip with `tmp_path`; includes `test_frozen_bundle.py` (skip-gated on `Dist/`)
- Legacy `tests/test_story_*.py` unittest modules still collected — mention but don't require contributors to run separately
- `pytest.ini`: `testpaths = tests`, `pythonpath = .`

Document that contributors need **no display** for the default test suite.

### Files Expected to Change

| File | Action |
|------|--------|
| `CONTRIBUTING.md` | **CREATE** |
| `docs/ARCHITECTURE.md` | **CREATE** |
| `README.md` | UPDATE — link to CONTRIBUTING, minor command alignment |
| `_bmad-output/implementation-artifacts/sprint-status.yaml` | UPDATE — story status (via create-story workflow) |

**Do not modify:** `core/`, `app/`, `Templates/`, `Build/luthier.spec`, `_bmad-output/planning-artifacts/*` content, `docs/USER-MANUAL.md` (unless fixing a broken link only).

### Previous Story Intelligence (4.2, 4.1)

| Learning | Apply to 4.4 |
|----------|--------------|
| Build command identical across OS | Document once with platform activate/path variants |
| PyInstaller 6+ onedir `_internal/` on Win/Linux | Include in bundle section |
| macOS `Contents/Frameworks/` for bundled assets | Platform table in CONTRIBUTING |
| `--check` headless gate | Document as mandatory smoke before GUI |
| 4.1/4.2 deferred CONTRIBUTING | **This story owns it** |
| Frozen tests skip when no `Dist/` | Explain so contributors aren't alarmed by skips |
| Win/Linux AC1–AC3 may be SKIP on dev Mac | Document honestly; commands still valid for target OS |

### Epic 4 Cross-Story Context

| Story | Focus | Status at story creation |
|-------|-------|--------------------------|
| 4.1 | macOS bundle | done |
| 4.2 | Windows + Linux bundle | in-progress |
| 4.3 | `cmake -B build` cross-platform | backlog |
| 4.4 | Contributor docs | **this story** |

4.4 can proceed in parallel with 4.2/4.3 — docs should reflect current README/build commands even if Win/Linux validation is pending. Link 4.3 CMake validation as future contributor test when available.

### Git Intelligence (Recent Commits)

| Commit | Relevance |
|--------|-----------|
| `08086eb` | Story 4.2 — cross-platform frozen test paths; document in ARCHITECTURE testing section |
| `1d2fa79` | Story 4.1 — macOS bundle validated; reuse build output table |
| `7649847` | Epic 5 docs pattern — manual smoke reports as reference for doc style |
| Epic 3 suite | 150 tests — update count from actual `pytest --collect-only` at implementation time |

### Latest Technical Notes

- **Python 3.14** on maintainer machine; README says 3.11+ — CONTRIBUTING should say "3.11+ required, 3.14 tested"
- **PyInstaller ≥ 6.0** — onedir layout; Win/Linux use `_internal/` subdirectory (6.1+)
- **pytest ≥ 8.0** in requirements-dev.txt
- **No CI** — CONTRIBUTING documents local-only verification; note Epic 3 retro action item for future CI

### Project Context Reference

- [Source: _bmad-output/project-context.md]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.4]
- [Source: README.md]
- [Source: core/project_writer.py — _RENDERED, _TOKENIZED, _VERBATIM]
- [Source: core/rendering.py]
- [Source: _bmad-output/implementation-artifacts/4-1-pyinstaller-bundle-macos.md]
- [Source: _bmad-output/implementation-artifacts/4-2-pyinstaller-bundle-windows-and-linux.md]

## Dev Agent Record

### Agent Model Used

Composer (Cursor Agent)

### Debug Log References

- Onboarding smoke (2026-06-26): `main.py --check` <1s; `pytest` 156 passed / 2 skipped in ~18s; 158 tests collected.
- All `_bmad-output/` AC3 paths verified present on disk.
- `Rules/process-clean-code.md` not tracked in repo — NFR1 limits inlined in CONTRIBUTING.

### Completion Notes List

- Created `CONTRIBUTING.md` with full onboarding flow, platform variants, bundle build table, NFR1 clean-code summary, `_bmad-output/` reference map, and honest 15-minute timing (core dev loop <15 min; PyInstaller optional/extended).
- Created `docs/ARCHITECTURE.md` with mermaid three-layer diagram, all 12 `core/` module contracts, two-pass rendering detail, AD-3/5/7/8/9 rules, and stale ARCHITECTURE-EXPLAINED warning.
- Updated `README.md`: link to CONTRIBUTING + ARCHITECTURE; aligned venv/python commands; preserved build table.
- Verified AC3 product reference paths; documented in CONTRIBUTING (no file moves).
- Regression: 156 passed, 2 skipped — no production code changed.

### File List

- `CONTRIBUTING.md` (created)
- `docs/ARCHITECTURE.md` (created)
- `README.md` (updated)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (updated)
- `_bmad-output/implementation-artifacts/4-4-contributor-documentation.md` (updated)

### Change Log

- 2026-06-26: Story 4.4 implementation — contributor documentation (CONTRIBUTING.md, docs/ARCHITECTURE.md, README cross-links).
- 2026-06-26: Follow-up — Win/Linux bundle and CMake configure validation completed (stories 4.2/4.3); CONTRIBUTING and ARCHITECTURE testing sections updated.

### Review Findings

- [x] [Review][Decision] README conserve la section PyInstaller complète vs déduplication vers CONTRIBUTING — **Résolu (2)** : tableau minimal user-facing + lien CONTRIBUTING pour le détail ; `_internal/` Win/Linux ajouté.

- [x] [Review][Patch] README Requirements pointe encore `requirements.txt` alors que Run from source utilise `requirements-dev.txt` [README.md:23]

- [x] [Review][Patch] Bloc `--check` README sans variante Windows [README.md:37-38]

- [x] [Review][Patch] CONTRIBUTING prétend que les unit tests n'importent que `core/` — `tests/unit/test_path_specs.py` importe `app.pages.path_specs` [CONTRIBUTING.md:77]

- [x] [Review][Patch] CONTRIBUTING décrit `tests/unit/` comme fonctions pures sans I/O — plusieurs modules unitaires écrivent via `tmp_path` [CONTRIBUTING.md:78]

- [x] [Review][Patch] ARCHITECTURE.md : « Preferences carries no Qt dependency » — `core/preferences.py`, `app_state.py`, `templates_store.py` importent `QStandardPaths` [docs/ARCHITECTURE.md:26]

- [x] [Review][Patch] ARCHITECTURE.md référence `Preferences.update(ProjectSpec)` — API supprimée ; grep ne trouve plus d'appel [docs/ARCHITECTURE.md:121]

- [x] [Review][Patch] Contrat `project_reader.py` : Outputs « warnings » — code expose `ProjectReadResult.missing_fields`, pas warnings [docs/ARCHITECTURE.md:143]

- [x] [Review][Patch] Tableau build README omet `_internal/` Win/Linux (PyInstaller 6+) [README.md:57-61]

- [x] [Review][Patch] ARCHITECTURE.md ancre « Story 4.3 » dans la doc système — préférer le nom de fichier seul [docs/ARCHITECTURE.md:164]

- [x] [Review][Patch] Contrat `project_form_state.py` : « Used by app/ only » — aussi importé par `tests/unit/test_project_dirty_guard.py` [docs/ARCHITECTURE.md:151]

- [x] [Review][Defer] `Docs/Luthier.png` / dossier `Docs/` absent du dépôt — lien README pré-existant ; table CONTRIBUTING documente une convention pas encore matérialisée [README.md:5, CONTRIBUTING.md:121] — deferred, pre-existing

- [x] [Review][Defer] Collision `docs/` vs `Docs/` sur macOS case-insensitive — seul `docs/` existe dans git ; table de convention, pas régression story 4.4 [CONTRIBUTING.md:119-121] — deferred, pre-existing

## Story Completion Status

- **Status:** done
- **Completion note:** All ACs satisfied; documentation-only story; code review patches applied (README dedup option 2, doc/code alignment).
