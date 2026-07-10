---
baseline_commit: fa28b57
target_version: 1.0.0
---

# Story 8.2: Pre-release legacy cleanup (strict 1.0.0)

Status: done

## Story

As the sole pre-release developer of Luthier,
I want obsolete compatibility paths removed and generated-project docs aligned with the current model,
So that v1.0.0 ships with a smaller, clearer codebase and no misleading legacy behaviour before public distribution.

## Context

- **Product version:** remains **1.0.0** until web distribution.
- **Precondition:** app never shipped; single user — **no obligation** to keep CMake-regex reload or JSON key migration from pre-8.1 formats.
- **Epic 8** reopens for this story (8.1 delivered Workspace).
- **BMad artifacts are sacred:** `_bmad-output/` (planning, stories, sprint status, deferred-work, project-context) **must not be deleted**. Update in place only where this story requires factual alignment (e.g. AD-3 wording, project-context paths).

### In scope — runtime & shipped templates

| Area | Today | After 8.2 |
|------|-------|-----------|
| Open without `.luthier.json` | CMake regex fallback (~150 lines) | **Rejected** with clear error |
| `project-configuration.cmake` reader | Fallback branch in `_parse_build_settings` | **Removed** (only sidecar + generated inline CMake) |
| `migrate_workspace_keys()` | `destination` / `destinationDir` / `juceDir` → host keys | **Removed** |
| `read_project()` wrapper | Returns `spec` only | **Removed**; callers use `read_project_result()` |
| `ProjectReadResult.missing_fields` | CMake parse field list | **Removed** (sidecar-only errors use `error` string) |
| Generated `templates/README.md`, `.cursorrules` | Mention `project-configuration.cmake` | **USER OPTIONS** section in `CMakeLists.txt` |
| User manuals + `docs/architecture.md` | Document CMake fallback / legacy open | **Sidecar required** |
| QA checklists | Archive test « projet sans sidecar » | Updated expectation |

### Explicitly out of scope

- **Deleting or pruning `_bmad-output/`** — historical stories, epics, proposals stay.
- Changing Workspace / Artefacts product behaviour (8.1).
- `manufacturer` (prefs) vs `manufacturerName` (project) dual-key design — active model, not legacy.
- JSON schema `version` field for prefs (deferred-work item).
- Removing `_bmad-output/planning-artifacts/` or past story files (1.x–7.x, 8.1).

## Acceptance Criteria

### AC1 — Sidecar required on Open

**Given** a project directory **without** a valid `.luthier.json`,
**When** **Open Project…** runs,
**Then** Luthier does **not** parse `CMakeLists.txt` for configuration.

**And** the user sees a clear error, e.g. *Not a Luthier project* or *Companion file `.luthier.json` is missing or invalid* — not a CMake field bullet list.

**Given** a directory with valid `.luthier.json`,
**When** Open succeeds,
**Then** behaviour is unchanged from 8.1 (host destination updated from filesystem parent).

### AC2 — `project_reader.py` simplified

**Given** story 8.2 is complete,
**When** inspecting `core/project_reader.py`,
**Then** it contains **only** sidecar read/validate logic plus host-destination injection on open.

**And** removed: `_parse_cmakelists`, `_read_from_cmake*`, `_parse_build_settings`, `_parse_set_vars`, regex constants used solely for CMake reload, `read_project()`.

**And** `ProjectReadResult` has fields `spec`, `error` only (no `missing_fields`).

### AC3 — Workspace JSON migration removed

**Given** `preferences.json` or `.luthier.json` containing only legacy keys `destination`, `destinationDir`, or `juceDir`,
**When** Luthier loads the file,
**Then** those keys are **not** auto-migrated (ignored or treated as unknown — host workspace paths remain empty unless six-key shape present).

**And** `migrate_workspace_keys`, `_LEGACY_WORKSPACE_KEYS`, and `had_legacy_workspace` reload/save paths in `Preferences.load()` are removed.

**And** `normalize_path_dict_values()` still normalizes slashes for known path keys (no migration call).

**Dev note:** sole user should re-export Preferences or reset `preferences.json` once after deploy; document in Completion Notes — no automated migration script required.

### AC4 — Generated template docs

**Given** **Generate Project** on a new project,
**When** reading `README.md` and `.cursorrules` in the output,
**Then** artefact/copy instructions reference the **USER OPTIONS** block at the top of `CMakeLists.txt`.

**And** no reference to `project-configuration.cmake` as an editable file (file is not generated).

### AC5 — Docs & agent context updated (not deleted)

**Given** user-facing docs,
**When** 8.2 is complete,
**Then** updated:

- `docs/user-manual.md` — Open requires `.luthier.json`; remove CMake fallback bullets
- `docs/manuel-utilisateur.md` — same (FR)
- `docs/architecture.md` — AD-3: sidecar-only reload
- `_bmad-output/project-context.md` — paths, Workspace keys, sidecar-only reader (fix stale `Templates/project-configuration.cmake`, old destination keys)

**And** QA checklists:

- `docs/checklist-qa-single-pass.md` — sidecar required on Open
- `docs/checklist-qa-manual.md` — replace archive « sans `.luthier.json` » test with « missing sidecar → clear error »

### AC6 — Tests & CI green

**Given** full `pytest` run,
**When** 8.2 is complete,
**Then** all tests pass.

**And** removed or rewritten:

- `test_cmake_fallback_*`, `test_partial_cmake_*`, `test_no_cmakelists_*` (integration)
- `test_legacy_project_configuration_cmake_compat`
- `test_cmake_escaped_quotes_in_company_name` (unit — CMake-only)
- `install_legacy_project_configuration_cmake` helper in `conftest.py` (if unused)
- `tests/unit/test_workspace_migration.py` — legacy migration cases only; keep host-resolution / normalize tests if still valid

**And** added/updated:

- Open without sidecar → `spec is None` + actionable `error`
- `test_sidecar_required_for_cross_origin_juce_dir` — deleting sidecar must **fail** reload (invert current assertion)

### AC7 — App layer

**Given** `MainWindow._load_project`,
**When** `read_project_result` fails,
**Then** no branch references `missing_fields` or « Could not parse … CMakeLists.txt ».

## Tasks / Subtasks

- [x] Slim `core/project_reader.py` (AC1, AC2)
  - [x] Delete CMake regex path and `read_project()`
  - [x] Simplify `ProjectReadResult`; export only `read_project_result`
  - [x] Sidecar missing → structured `error` (distinct messages: absent file vs invalid JSON vs validation)
- [x] Remove workspace migration (AC3)
  - [x] Delete `migrate_workspace_keys` from `core/paths.py`
  - [x] Remove legacy keys from `_PATH_DICT_KEYS` if only used for migration (`destination`, `destinationDir`, `juceDir`)
  - [x] Clean `Preferences.load()` / `_complete_profile` / import paths
- [x] Update callers (AC2, AC7)
  - [x] `app/main_window.py` — error messages
  - [x] Tests/integration: replace `read_project` with `read_project_result(...).spec` or direct result asserts
- [x] Template docs (AC4)
  - [x] `templates/README.md` — USER OPTIONS / `CMakeLists.txt`
  - [x] `templates/.cursorrules` — same
- [x] User docs & architecture (AC5)
  - [x] `docs/user-manual.md`, `docs/manuel-utilisateur.md`, `docs/architecture.md`
  - [x] `docs/checklist-qa-*.md`
  - [x] `_bmad-output/project-context.md` (update only — do not delete `_bmad-output/`)
- [x] Tests (AC6)
  - [x] Remove legacy CMake/migration tests; add sidecar-required tests
  - [x] `.venv/bin/pytest` green
- [x] Tracking (AC5)
  - [x] Mark story `review` in this file; `sprint-status.yaml` → `8-2: review` (epic-8 → `in-progress` until code review)

### Review Findings

- [x] [Review][Decision] Legacy `preferences.json` with only legacy workspace keys — **1A** : strip legacy keys on load, preserve identity; host destination seeded from Desktop when empty [`core/preferences.py`]
- [x] [Review][Decision] Sidecar with legacy workspace keys only — **2B** : accept open; sole user re-exports manually (no code change)
- [x] [Review][Decision] Optional `CMakeLists.txt` presence check on Open — **3B** : not implemented (YAGNI for v1.0.0)

- [x] [Review][Patch] BMad tracking doc drift — synced [`epics.md`, `deferred-work.md`, `sprint-status.yaml`]
- [x] [Review][Patch] `epics.md` AD-1/AD-3 updated to `read_project_result()` sidecar-only [`epics.md`]
- [x] [Review][Patch] Stale `spec.destination_dir` → `host_destination_dir()` [`project-context.md:105`]
- [x] [Review][Patch] Stale « No tests » line updated [`project-context.md:258`]
- [x] [Review][Patch] `test_sidecar_non_dict` asserts actionable `error` [`tests/unit/test_project_reader.py`]
- [x] [Review][Patch] Test module docstring trimmed [`tests/unit/test_project_reader.py:1`]

- [x] [Review][Defer] `architecture-spine.md` AD-3 still mandates CMake fallback — deferred, pre-existing; story scope excluded planning spine; `docs/architecture.md` updated [`architecture-spine.md:58`]
- [x] [Review][Defer] Shallow sidecar validation (3 fields only) allows partial spec load — deferred, pre-existing from Story 7.3 [`core/project_reader.py:75-104`]
- [x] [Review][Defer] Unreachable `plugin_formats` guard in `MainWindow._load_project` — deferred, pre-existing defensive branch [`app/main_window.py`]
- [x] [Review][Defer] `test_workspace_migration.py` filename misleading after migration removal — deferred, cosmetic rename
- [x] [Review][Defer] No integration test asserting generated `README.md` references USER OPTIONS — deferred, AC4 templates correct; manual QA covers

## Dev Notes

### `project_reader.py` target shape (~80–100 lines)

```
read_project_result(dir):
  if not (dir / ".luthier.json").exists():
    return ProjectReadResult(None, error="Companion file .luthier.json is missing.")
  ... existing sidecar validate + load ...
  data[host_dest] = parent(dir)
  return ProjectReadResult(ProjectSpec.from_dict(data))
```

Optional: still require `CMakeLists.txt` to exist for « looks like a project » — return a different message if only sidecar present without CMake (edge case).

### Files to touch (expected)

| File | Action |
|------|--------|
| `core/project_reader.py` | Major delete |
| `core/paths.py` | Remove migration |
| `core/preferences.py` | Remove legacy reload hook |
| `app/main_window.py` | Simplify open errors |
| `templates/README.md`, `templates/.cursorrules` | Doc fix |
| `docs/user-manual.md`, `docs/manuel-utilisateur.md`, `docs/architecture.md` | Doc fix |
| `docs/checklist-qa-single-pass.md`, `docs/checklist-qa-manual.md` | QA fix |
| `_bmad-output/project-context.md` | Agent context sync |
| `tests/integration/test_round_trip.py` | Remove cmake tests |
| `tests/integration/test_cmake_cross_platform.py` | Fix sidecar test |
| `tests/unit/test_project_reader.py` | Remove cmake test |
| `tests/unit/test_workspace_migration.py` | Trim migration tests |
| `tests/conftest.py` | Remove `install_legacy_project_configuration_cmake` |

### Do NOT touch

- `_bmad-output/implementation-artifacts/*.md` (historical stories) except **this file** + `sprint-status.yaml` + `deferred-work.md` (one-line note when done)
- `_bmad-output/planning-artifacts/**` except optional one-line Epic 8.2 entry in `epics.md`

### Manual smoke (dev)

1. Generate project → delete `.luthier.json` → **Open** → clear error, no crash.
2. Valid project → **Open** → loads; host Workspace destination updated.
3. Fresh `preferences.json` with only six workspace keys → Preferences OK.
4. New generate → README mentions `CMakeLists.txt` USER OPTIONS, not `project-configuration.cmake`.

## Test plan

1. Unit: sidecar validation cases unchanged; new « missing sidecar » case.
2. Integration: round-trip via sidecar only; no cmake fallback tests.
3. Full pytest green.
4. `dist/Luthier.app/.../Luthier --check` if bundle rebuilt locally (optional).

## Dev Agent Record

### Implementation Plan

- Reduced `project_reader.py` to sidecar-only (~103 lines): missing sidecar returns explicit `error`; no CMake regex path.
- Removed `migrate_workspace_keys`, legacy `_PATH_DICT_KEYS`, and `Preferences.load()` auto-save on legacy keys.
- Simplified `MainWindow._load_project` to surface `result.error` only.
- Updated templates, user docs, architecture, QA checklists, and `project-context.md`.
- Replaced/removed CMake fallback and migration tests; inverted `test_sidecar_required_for_cross_origin_juce_dir`.

### Debug Log

- Fixed `test_app_state.py` and `test_paths.py` after migration removal (host workspace keys required in profiles).

### Completion Notes

- **249 passed, 2 skipped** — full `pytest` green.
- **Manual post-deploy:** re-export Preferences or reset `preferences.json` to the six-key Workspace shape if an old file still contains `destination` / `juceDir` (no auto-migration).
- Story ready for `code-review` (recommend a different LLM than the implementer).

## File List

- `core/project_reader.py` — modified
- `core/paths.py` — modified
- `core/preferences.py` — modified
- `app/main_window.py` — modified
- `templates/README.md` — modified
- `templates/.cursorrules` — modified
- `docs/user-manual.md` — modified
- `docs/manuel-utilisateur.md` — modified
- `docs/architecture.md` — modified
- `docs/checklist-qa-single-pass.md` — modified
- `docs/checklist-qa-manual.md` — modified
- `_bmad-output/project-context.md` — modified
- `_bmad-output/implementation-artifacts/deferred-work.md` — modified
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — modified
- `tests/conftest.py` — modified
- `tests/integration/test_round_trip.py` — modified
- `tests/integration/test_cmake_cross_platform.py` — modified
- `tests/integration/test_frozen_bundle.py` — modified
- `tests/unit/test_project_reader.py` — modified
- `tests/unit/test_workspace_migration.py` — modified
- `tests/unit/test_paths.py` — modified
- `tests/unit/test_app_state.py` — modified

## Change Log

- 2026-07-01: Story 8.2 implemented — sidecar-only reload, workspace migration removed, docs/templates/tests aligned for v1.0.0 pre-release.
- 2026-07-01: Code review — decisions 1A/2B/3B applied; tracking docs synced; `Preferences.load()` strips legacy workspace keys while preserving identity.

---

*Epic 8.2 — strict 1.0.0 pre-public cleanup. BMad `_bmad-output/` preserved.*
