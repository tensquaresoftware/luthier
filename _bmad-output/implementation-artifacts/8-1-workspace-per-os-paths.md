---
baseline_commit: da5b2f915c6d9077bb236fef93ec5a8c42f4b2f6
target_version: 1.0.0
doc_version: 1.0
---

# Story 8.1: Workspace — per-OS destination and JUCE paths

Status: done

## Story

As a JUCE developer who builds the same Luthier projects on macOS, Windows, and Linux,
I want **Destination folder** and **JUCE directory** stored per platform in **Workspace** (Project and Preferences),
So that I configure paths once per profile and no longer re-enter them when I clone, open, or switch machines.

## Context

- **Product version:** reset to **1.0.0** at public release (repo still private; single user pre-release).
- **Manuals:** `docs/user-manual.md` and `docs/manuel-utilisateur.md` — doc version **1.0**, product target **1.0.0**.
- **Section name:** **Workspace** (short; echoes **Artefacts**).
- **Placement:** new section **above Artefacts**, at the bottom of the scrollable form (just before the action bar) on **Project** and **Preferences** tabs.

### Tab section order (after)

| Order | Project tab | Preferences tab |
|-------|-------------|-------------------|
| top | Luthier Accent Color | Luthier Accent Color |
| 1 | Project Info | Identity |
| 2 | Plugin Type | Plugin Type |
| 3 | Formats | Formats |
| 4 | Compilation | Compilation |
| 5 | **Workspace** | **Workspace** |
| 6 | Artefacts | Artefacts |

**Project Info** retains identity fields and Bundle ID only — no path fields.

## Acceptance Criteria

### AC1 — Workspace section UI

**Given** the Project or Preferences tab,
**When** I scroll to the bottom of the form (above the action bar),
**Then** I see a **Workspace** section **above Artefacts** containing:

1. **Destination folder** * — three rows labelled **Windows**, **macOS**, **Linux**
2. **JUCE directory** — three rows labelled **Windows**, **macOS**, **Linux**

**And** the row for the **host OS** has **Choose…** (native folder picker); the other two rows are text-only (same pattern as Artefacts).

**And** layout per row is **label → Choose… (host only) → text field** (field remains editable).

### AC2 — Runtime resolution (host OS)

**Given** Luthier is running on a given OS,
**When** **Generate Project** runs (or destination/JUCE is read for validation, CMake, or dialogs),
**Then** the **host OS** values are used:

| Host | Destination key | JUCE key |
|------|-----------------|----------|
| Windows | `destinationDirWindows` | `juceDirWindows` |
| macOS | `destinationDirMacos` | `juceDirMacos` |
| Linux | `destinationDirLinux` | `juceDirLinux` |

**And** non-host paths are ignored at generation time but preserved in `.luthier.json` / `preferences.json`.

### AC3 — Validation

**Given** the Project tab,
**When** I attempt **Generate Project**,
**Then** the **host** **Destination folder** must be non-empty and pass `validate_destination`.

**And** the **host** **JUCE directory** is optional; if set, it must pass `validate_optional_path`.

**And** non-host workspace paths: if non-empty, validate format (`validate_optional_path`); empty is allowed — no blocking error.

**Given** Preferences auto-save,
**When** any workspace field is edited,
**Then** only **host destination** is required for a valid profile (same rule as today for single `destination`).

### AC4 — Open Project…

**Given** I open a project folder via **Open Project…**,
**When** the load succeeds,
**Then** only the **host** **Destination folder** row is overwritten with `parent(project_dir)`.

**And** the other five workspace values are loaded unchanged from `.luthier.json` (or legacy migration — see AC6).

### AC5 — Create New Project / Preferences seed

**Given** I click **Create New Project**,
**When** the form resets,
**Then** workspace fields are re-seeded from `preferences.json` (all six keys).

**Given** first launch factory defaults,
**When** `preferences.json` is created,
**Then** the **host** **Destination folder** is set to Desktop (current behaviour); the five other workspace paths are empty.

### AC6 — Migration (legacy single-path keys)

**Given** an existing `preferences.json` or `.luthier.json` with only `destination` / `destinationDir` and `juceDir`,
**When** Luthier loads the file,
**Then** legacy values are migrated in memory:

| Legacy key | Copied to (host OS only) |
|------------|--------------------------|
| `destination` or `destinationDir` | `destinationDir{Windows\|Macos\|Linux}` for host |
| `juceDir` | `juceDir{Windows\|Macos\|Linux}` for host |

**And** on next save/generate, the sidecar/profile is written with the new six-key shape (legacy keys omitted or stripped).

**And** importing an old export JSON with legacy keys applies the same migration.

### AC7 — Import / Export / round-trip

**Given** I **Export Preferences…**,
**When** the file is written,
**Then** it contains all six workspace keys (plus existing profile fields).

**Given** I **Import Preferences…** a valid profile with six workspace paths,
**When** import succeeds,
**Then** all six values are stored; **Create New Project** seeds Project tab from them.

**Given** a generated project with six workspace paths in `.luthier.json`,
**When** I **Open Project…** on another OS,
**Then** the non-host paths from the sidecar are intact; I only adjust host JUCE if needed before **Generate Project**.

### AC8 — Generate behaviour unchanged (semantics)

**Given** valid host workspace paths,
**When** **Generate Project** succeeds,
**Then** output is still `host_destination / project_name`, `JUCE_DIR` in `CMakeLists.txt` uses host JUCE path, and `app_state.json` remembers last parent folder (host destination).

**Given** host destination empty or invalid,
**When** I click **Generate Project**,
**Then** Luthier prompts **Choose destination folder** (existing behaviour, scoped to host key).

## Tasks / Subtasks

- [x] Core model and migration (AC2, AC6, AC7)
  - [x] Add six workspace fields to `ProjectSpec`; `host_destination_dir()` / `host_juce_dir()` helpers
  - [x] Update `Preferences` profile keys, `factory_defaults`, `validate_profile`, `to_dict` / import
  - [x] Legacy migration: `destination` / `destinationDir` / `juceDir` → host OS keys on load
  - [x] Update `project_reader.py`: Open overwrites host destination only
- [x] UI — `WorkspaceSection` (AC1)
  - [x] New `app/pages/workspace.py` (mirror `ArtefactsSection` Choose… pattern)
  - [x] Wire Project tab: remove paths from `ProjectInfoPage`; section order Compilation → Workspace → Artefacts
  - [x] Wire Preferences tab: replace **Paths** with **Workspace**; auto-save integration
  - [x] `path_specs.py`: `host_workspace_field_key()`
- [x] Generate / Open pipeline (AC2, AC4, AC8)
  - [x] `MainWindow`, `project_generator`, `render_context` use host workspace paths
  - [x] Validation: host destination required; non-host optional
- [x] Tests (AC6, AC7)
  - [x] Unit: migration, host resolution, validation, Open host-only update
  - [x] Integration: round-trip six keys in `.luthier.json`
  - [x] Full `pytest` green
- [ ] Release metadata (out of scope AC but in context)
  - [ ] `app/version.py` → `1.0.0` when epic complete

## Data model

### JSON keys (camelCase, flat — mirrors artefacts)

| Key | Scope | Description |
|-----|-------|-------------|
| `destinationDirWindows` | Preferences + Project | Parent folder for new projects on Windows |
| `destinationDirMacos` | Preferences + Project | Parent folder on macOS |
| `destinationDirLinux` | Preferences + Project | Parent folder on Linux |
| `juceDirWindows` | Preferences + Project | JUCE SDK path on Windows |
| `juceDirMacos` | Preferences + Project | JUCE SDK path on macOS |
| `juceDirLinux` | Preferences + Project | JUCE SDK path on Linux |

**Removed after migration:** `destination`, `destinationDir` (project), `juceDir` (single).

### `ProjectSpec` fields

Add six `str` fields; remove `destination_dir` and `juce_dir` singles.

Convenience (implementation):

```python
def host_destination_dir(self) -> str: ...
def host_juce_dir(self) -> str: ...
```

Resolve via `host_workspace_field_key("destination")` / `host_workspace_field_key("juce")` in `app/pages/path_specs.py` (parallel to `host_artefact_field_key()`).

### `Preferences` profile keys

Replace `destination` and `juceDir` in `_PROFILE_KEYS`, `_IDENTITY_KEYS` with the six workspace keys. `_WORKSPACE_KEYS` tuple for section save/load.

`factory_defaults()`: set `destinationDir{Host}` = Desktop; others `""`.

`validate_profile()`: validate host destination required; six paths optional format checks.

## UI implementation notes

### New widget

`app/pages/workspace.py` — `WorkspaceSection` modelled on `ArtefactsSection`:

- Two labelled groups: **Destination folder** * (subsection label) + 3 OS rows; **JUCE directory** + 3 OS rows.
- `host_workspace_field_key()` picks which row gets `FolderField` vs `ValidatedField`.
- `values()`, `load()`, `is_valid()`, `validityChanged`, `flash_saved` / `is_saved_sender` for Preferences auto-save integration.

### Project tab

- Remove `_destination` / `_juce_dir` from `ProjectInfoPage`.
- Add `WorkspaceSection` to `ProjectPage` between Compilation and Artefacts.
- `ProjectPage.spec()` / `values()` include workspace dict.
- `set_destination(value)` → sets host destination field only (for Open + Generate picker).
- `is_valid()` includes workspace section.

### Preferences tab

- Remove standalone `_destination` / `_juce_dir` and **Paths** section.
- Add `WorkspaceSection`; wire auto-save like artefacts.
- `apply_form` / `to_dict` / import validation updated.

### `path_specs.py`

- `host_workspace_field_key(kind: Literal["destination", "juce"]) -> str`
- `destination_field_spec` / `juce_field_spec` — add optional `suffix` or per-OS key helpers.
- Destination row labels: **Windows**, **macOS**, **Linux** (not repeated "Destination folder" on each row — group header carries the name).

## Files to touch

| Area | Files |
|------|-------|
| UI | `app/pages/workspace.py` (new), `app/pages/project_info.py`, `app/pages/project.py`, `app/pages/preferences.py`, `app/pages/path_specs.py` |
| Core | `core/project_spec.py`, `core/preferences.py`, `core/project_reader.py`, `core/paths.py`, `core/project_form_state.py` |
| App | `app/main_window.py` (generate/open use `spec.host_destination_dir()`, `spec.host_juce_dir()`) |
| Generator | `core/project_generator.py`, `core/render_context.py` (if juce passed separately) |
| Tests | `tests/unit/test_path_specs.py`, `tests/unit/test_project_spec.py`, `tests/unit/test_preferences.py`, `tests/unit/test_project_reader.py`, `tests/integration/test_round_trip.py`, new `tests/unit/test_workspace_migration.py` |
| Docs | `docs/user-manual.md`, `docs/manuel-utilisateur.md` |
| Version | `app/version.py` → `1.0.0`, `REVISION_DATE` updated at release |

## Out of scope

- Collapsing non-host OS rows in the UI.
- Automatic detection of JUCE install paths per OS.
- JSON schema `version` field (deferred).
- QA checklist updates (separate pass after implementation).

## Test plan (dev)

1. **Migration:** load legacy `preferences.json` with `destination` + `juceDir` → host keys populated.
2. **Round-trip:** export/import six paths; Create New Project seeds all six.
3. **Open:** sidecar with three destinations; open on macOS → only `destinationDirMacos` updated.
4. **Generate:** Windows host uses `destinationDirWindows` / `juceDirWindows` in CMake output.
5. **Validation:** empty host destination blocks Generate; empty Linux destination on macOS host does not block.
6. **Choose…:** only host rows open native picker.
7. Full `pytest` green.

## Manual smoke

1. Preferences → Workspace → fill six paths (Choose… on host) → Export → Import on clean profile.
2. Create New Project → verify seed → Generate.
3. Git clone project on second OS → Open → host JUCE updated manually → Generate without re-entering other OS paths.

---

*Companion doc updates: `docs/user-manual.md` §7.5 Workspace, §8.1; `docs/manuel-utilisateur.md` §7.5, §8.1.*

## Dev Agent Record

### Implementation Plan

- Replaced single `destination`/`juceDir` keys with six per-OS workspace keys in `ProjectSpec` and `Preferences`.
- Added `migrate_workspace_keys()` in `core/paths.py` for legacy JSON migration on load/import.
- Host OS resolution via `host_workspace_field_key()` used by generation, open, and validation.
- New `WorkspaceSection` UI (mirrors `ArtefactsSection` Choose… pattern) on Project and Preferences tabs.

### Completion Notes

- All acceptance criteria implemented; 259 pytest tests pass (256 + 3 new path_specs tests).
- Legacy `preferences.json` / `.luthier.json` files migrate on load and re-save with new key shape.
- Open Project overwrites only the host destination row; other five workspace values preserved.
- Version bump to 1.0.0 deferred until epic 8 complete (per story scope).

## File List

- `app/main_window.py` (modified)
- `app/pages/path_specs.py` (modified)
- `app/pages/preferences.py` (modified)
- `app/pages/project.py` (modified)
- `app/pages/project_info.py` (modified)
- `app/pages/workspace.py` (new)
- `core/paths.py` (modified)
- `core/preferences.py` (modified)
- `core/project_generator.py` (modified)
- `core/project_reader.py` (modified)
- `core/project_spec.py` (modified)
- `core/render_context.py` (modified)
- `tests/conftest.py` (modified)
- `tests/integration/test_cmake_cross_platform.py` (modified)
- `tests/integration/test_frozen_bundle.py` (modified)
- `tests/integration/test_round_trip.py` (modified)
- `tests/unit/test_path_specs.py` (modified)
- `tests/unit/test_paths.py` (modified)
- `tests/unit/test_preferences.py` (modified)
- `tests/unit/test_preferences_decouple.py` (modified)
- `tests/unit/test_project_dirty_guard.py` (modified)
- `tests/unit/test_project_spec.py` (modified)
- `tests/unit/test_render_context.py` (modified)
- `tests/unit/test_workspace_migration.py` (new)

## Change Log

- 2026-07-01: Story 8.1 — per-OS workspace paths (destination + JUCE), migration, UI section, host resolution at generate/open.

### Review Findings

- [x] [Review][Patch] Preferences auto-save drops plugin/format/compilation changes — `_try_auto_save` builds full profile via `_collect_profile()` but calls `apply_form(identity, workspace, artefacts)` instead of `apply_profile(profile)`; plugin type, formats, and compilation keys are never written on auto-save (regression vs pre-8.1) [`app/pages/preferences.py:168`]
- [x] [Review][Patch] Redundant double migration in `_complete_profile` — calls `migrate_workspace_keys(normalize_path_dict_values(data))` but `normalize_path_dict_values` already invokes `migrate_workspace_keys` [`core/preferences.py:110`]
- [x] [Review][Patch] Whitespace-only legacy `destination` blocks `destinationDir` migration — `str(out.get("destination") or ...)` treats whitespace-only destination as truthy before strip, so a valid `destinationDir` is ignored [`core/paths.py:89`]
- [x] [Review][Patch] Dead legacy `destination_field_spec` / `juce_field_spec` still target removed keys `destinationDir` / `juceDir`; production UI uses `workspace_*_specs` only [`app/pages/path_specs.py`]
- [x] [Review][Patch] Orphan `folder_start_resolver` parameter on `ProjectInfoPage` — no `FolderField` remains after path fields moved to Workspace [`app/pages/project_info.py:55`]
- [x] [Review][Patch] Missing test: AC6 import of legacy export JSON (`destination`/`juceDir` only via `import_from_file` / `apply_profile`) [`tests/unit/test_workspace_migration.py`]
- [x] [Review][Patch] Missing test: AC7 export contains all six workspace keys [`tests/unit/test_preferences.py`]
- [x] [Review][Defer] `project-context.md` still documents single `destination`/`juceDir` keys — stale agent context [`_bmad-output/project-context.md`] — deferred, pre-existing doc drift
- [x] [Review][Defer] `host_workspace_field_key` lives in `core/paths.py` not `app/pages/path_specs.py` as spec suggested — works via re-export [`core/paths.py`] — deferred, cosmetic spec alignment
