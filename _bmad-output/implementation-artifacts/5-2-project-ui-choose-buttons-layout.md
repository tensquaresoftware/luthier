---
baseline_commit: aec1e2e
---

# Story 5.2: Project UI, Choose Buttons & Layout

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer,
I want Choose… buttons and consistent labels on the Project tab,
So that I can pick local folders easily while keeping cross-OS artefact paths as typed text.

## Acceptance Criteria

1. **Given** the Project Info section, **when** I view it, **then** field order is: identity fields → Bundle ID → **Destination folder** * → **JUCE directory**; both path fields use **label → Choose… → text field** layout.
2. **Given** I click Choose… on Destination folder or JUCE directory, **when** I select a folder in the native dialog, **then** the text field is populated with an OS-valid path and remains editable.
3. **Given** artefact path fields on Project (when copy-to-central is enabled), **when** I view them, **then** labels are **Windows**, **macOS**, **Linux** with **no** Choose… buttons.
4. **Given** app startup or successful Preferences import, **when** Project is in "new project" state, **then** all seedable fields (except empty identity) reflect current `preferences.json` values including plugin type, formats, and compilation.
5. **Given** Story 5.3 is complete and the JUCE directory field is on the Project tab, **when** I edit the JUCE directory field, **then** `ProjectPage.spec()` includes the value in `ProjectSpec.juce_dir` (wired to sidecar field, not read from Preferences at generate time).

## Tasks / Subtasks

- [x] Rebuild `ProjectInfoPage` layout and path pickers (AC: 1, 2)
  - [x] Remove `destinationDir` from `_field_specs()` / `ValidatedForm` — destination moves out of the identity form stack
  - [x] Rename label **Destination *** → **Destination folder** * (asterisk retained for required field)
  - [x] After `_build_bundle_row()`, add two `FolderField` rows: destination + JUCE directory
  - [x] Reuse `FolderField` from `app/widgets/folder_field.py` — same pattern as `PreferencesPage` (`_destination_spec` / `_juce_spec` equivalents keyed for Project form)
  - [x] Dialog titles: `"Choose destination folder"`, `"Choose JUCE directory"`
  - [x] Validators: `validate_destination` (required), `validate_optional_path` (JUCE)
  - [x] JUCE placeholder via `_juce_dir_placeholder()` — extract to shared helper (e.g. `app/pages/path_specs.py`) or import from `preferences.py` to avoid duplication
  - [x] Extend `values()` to emit `destinationDir` and `juceDir`
  - [x] Extend `load()` to call `set_value()` on both `FolderField`s
  - [x] Extend `is_valid()` to require `_form.is_valid()` **and** both folder fields valid
  - [x] Wire `FolderField.validityChanged` → `ProjectInfoPage.validityChanged`

- [x] Wire full prefs seed at Project tab startup (AC: 4)
  - [x] At end of `ProjectPage.__init__`, call `_seed_new_project(defaults)`:
    ```python
    seed = {**defaults, "projectName": "", "projectDisplayName": "", "projectVersion": "1.0.0"}
    self.load(ProjectSpec.from_dict(seed))  # after 5.3 adds juce_dir; see Prerequisite below
    ```
  - [x] Ensure `load()` propagates to `_type`, `_formats`, `_compilation`, `_artefacts` (already does for spec fields)
  - [x] `ProjectInfoPage.load()` must set folder fields from `destinationDir` / `juceDir` keys
  - [x] Verify cold start: plugin type, formats, cxx standard, artefact flags match `preferences.json` — not hardcoded widget defaults
  - [x] After Preferences import, Project tab UI still unchanged (seed cache `_defaults` refresh only — already in `MainWindow._on_prefs_import`)

- [x] Verify artefact section unchanged (AC: 3)
  - [x] Confirm `ArtefactsSection` labels are **Windows** / **macOS** / **Linux** (done in 5.1) — no Choose… buttons
  - [x] No code changes expected unless regression found

- [x] JUCE field → `ProjectSpec` wiring (AC: 5 — **requires Story 5.3**)
  - [x] **If 5.3 not done:** implement minimal 5.3 slice first: add `juce_dir: str = ""` to `ProjectSpec`, `juceDir` in `to_dict`/`from_dict`, update `tests/unit/test_project_spec.py`
  - [x] `ProjectInfoPage.values()` already emits `juceDir` once UI exists; `ProjectPage.spec()` picks it up via `from_dict`
  - [x] **Do not** change `MainWindow._run_generation` `juce_dir=self._prefs.juce_dir` — full pipeline switch is Story 5.3
  - [x] Manual check: after minimal `ProjectSpec` change, `spec().juce_dir` reflects Project tab field value

- [x] Regression
  - [x] `.venv/bin/pytest` — full suite green
  - [x] Manual smoke: cold start shows seeded type/formats/compilation; Choose… populates destination + JUCE; Open Project round-trip still works; Generate still works (JUCE from prefs until 5.3 completes pipeline)

## Dev Notes

### Prerequisite — Story 5.3 Ordering

Epic 5 recommended order: **5.1 → 5.3 → 5.2 → 5.4 → 5.5**.

| Approach | What to do |
|----------|------------|
| **Recommended** | Run `dev-story` for **5.3** first, then 5.2 — AC5 satisfied without scope creep |
| **5.2 standalone** | Add `juce_dir` to `ProjectSpec` + dict mapping only (minimal 5.3 slice); leave `render_context.build_context(spec, juce_dir=)` and `MainWindow` generate call unchanged until full 5.3 |

AC5 explicitly depends on `ProjectSpec.juce_dir`. The Project tab **UI** for JUCE directory is in scope for 5.2 regardless; pipeline reads from `spec.juce_dir` at generate time is 5.3.

### Scope — Files to Touch

| File | Change |
|------|--------|
| `app/pages/project_info.py` | Remove destination from form; add `FolderField` rows after Bundle ID; extend values/load/validity |
| `app/pages/project.py` | `_seed_new_project()` at end of `__init__`; optional `load()` tweak for dict-based seed before 5.3 |
| `app/pages/path_specs.py` (optional **new**) | Shared `_juce_dir_placeholder()`, `_destination_field_spec()`, `_juce_field_spec()` for Preferences + Project |
| `core/project_spec.py` | **Only if 5.3 not done:** add `juce_dir` field + dict keys |
| `tests/unit/test_project_spec.py` | **Only if 5.3 not done:** round-trip `juceDir` |

### Do NOT Touch in This Story

| File | Reason |
|------|--------|
| `app/widgets/folder_field.py` | Reuse as-is from 5.1 |
| `app/pages/artefacts.py` | Labels + no Choose… done in 5.1 — verify only |
| `core/render_context.py`, `core/project_generator.py` | Drop `juce_dir=` param — Story 5.3 |
| `app/main_window.py` `_load_project` / `_run_generation` prefs sync removal | Story 5.4 |
| `ProjectPage.reset()` full profile re-seed + dirty guard | Story 5.5 |
| `_bmad-output/project-context.md`, `ARCHITECTURE-SPINE.md` | Update after 5.4 when AD-5 lands in code |

### Current State — Gap Analysis

| Area | Today (post 5.1) | Target (5.2) |
|------|------------------|--------------|
| Destination on Project | `ValidatedField` "Destination *" inside `ValidatedForm`, before Bundle ID | `FolderField` "Destination folder *" **after** Bundle ID |
| JUCE on Project | **No field** | `FolderField` "JUCE directory" after destination |
| Project Info field order | form (incl. destination) → Bundle ID | form (identity only) → Bundle ID → destination → JUCE |
| Startup seed | `ProjectInfoPage` gets identity slice from `seed_dict()`; type/formats/compilation use **hardcoded widget defaults** | Full `seed_dict()` applied via `ProjectPage.load()` at init |
| `seed_dict()` legacy keys | `manufacturer`, `destination` aliases for `ProjectInfoPage` | Prefer `destinationDir` / `manufacturerName`; remove legacy reads in `_field_specs` once folder fields wired |
| `ProjectSpec.juce_dir` | **Missing** from dataclass | Required for AC5 — add in 5.3 or minimal slice |
| Artefact labels | Windows / macOS / Linux, text-only | No change (5.1) |

### Architecture Compliance

**AD-2:** `ProjectSpec` will carry `juce_dir` (5.3). This story adds the Project tab UI source for that field.

**AD-5 (revised, not fully implemented until 5.4):** Open/Generate still call `prefs.update()` + `save()` — **leave unchanged**.

**AD-7 (revised):** `Preferences.juce_dir` is default seed only. Project tab JUCE field is per-project; `seed_dict()` already includes `juceDir` for startup seed. Generate still reads `self._prefs.juce_dir` until 5.3 switches to `spec.juce_dir`.

**AD-6:** No Qt widget tests. Optional pure test for seed merge helper if extracted. Full pytest must stay green.

**AD-8:** Qt (`FolderField`, dialogs) stays in `app/`; no new Qt imports in `core/`.

### `ProjectInfoPage` Target Layout

```
ValidatedForm (identity only):
  Project name *, Display name, Version *
  Manufacturer *, Copyright, Website, E-mail
  Manufacturer code *, Plugin code *
Bundle ID (read-only)
FolderField: Destination folder *
FolderField: JUCE directory
```

### Reuse `FolderField` Pattern from Preferences

Reference implementation in `app/pages/preferences.py`:

```python
# FieldSpec for Project form keys (not prefs keys):
FieldSpec("destinationDir", "Destination folder *", validate_destination, default=defaults.get("destinationDir", ""))
FieldSpec("juceDir", "JUCE directory", validate_optional_path, default=defaults.get("juceDir", ""), placeholder=_juce_dir_placeholder())
```

`FolderField` row order is already **label → Choose… → text field → mark** (`folder_field.py` lines 60–62).

### `ProjectPage` Startup Seed

`MainWindow` already passes full `seed_dict()`:

```python
self._defaults = self._prefs.seed_dict()
self._project_page = ProjectPage(self._defaults, plugin_settings.bundle_id, self._prefs)
```

Gap: `ProjectPage.__init__` never calls `load()` — only `ProjectInfoPage` ctor reads partial defaults. Fix:

```python
def __init__(self, defaults, bundle_id_fn, prefs):
    ...
    self._build_ui()
    self._connect_signals()
    self._seed_new_project(defaults)

def _seed_new_project(self, defaults: dict) -> None:
    seed = {**defaults, "projectName": "", "projectDisplayName": "", "projectVersion": "1.0.0"}
    self.load(ProjectSpec.from_dict(seed))
```

`load()` already sets type, formats, compilation, artefacts. Identity fields get empty names; everything else from prefs.

**Before `juce_dir` on ProjectSpec:** Either complete 5.3 first, or use interim `load_from_seed_dict(seed: dict)` that sets sections directly without `ProjectSpec.from_dict` for unknown keys — prefer adding `juce_dir` to avoid dual paths.

### `values()` / `spec()` / `load()` Contract

| Key | Source after 5.2 |
|-----|------------------|
| `destinationDir` | `ProjectInfoPage._destination.value()` |
| `juceDir` | `ProjectInfoPage._juce_dir.value()` |
| Identity keys | `ValidatedForm` unchanged |
| `pluginType`, `pluginFormats`, compilation, artefacts | Unchanged section widgets |

`ProjectPage.spec()` assembly unchanged except `juceDir` flows in once on `ProjectSpec`:

```python
d = dict(self._info.values())  # now includes destinationDir + juceDir
d["pluginType"] = ...
return ProjectSpec.from_dict(d)
```

`ProjectInfoPage.load(values)` must handle both `destinationDir` and legacy `destination` key during transition.

### Import Preferences Behaviour (AC: 4 partial)

`MainWindow._on_prefs_import` already refreshes `self._defaults = self._prefs.seed_dict()` without reloading Project UI. No change required. Next **Create New Project** (5.5) or cold start will use new seed — document for manual test.

### Testing Requirements

- **No new Qt tests** (AD-6)
- If `juce_dir` added to `ProjectSpec`: extend `tests/unit/test_project_spec.py` with `juceDir` round-trip
- Existing `test_seed_dict_maps_project_form_keys` in `test_preferences.py` already validates seed shape
- Full suite: `.venv/bin/pytest`
- Manual smoke checklist:
  1. Delete prefs / first launch → Project shows Desktop destination, synth, AU+VST3+Standalone, C++17
  2. Choose… on destination → path in field, editable
  3. Choose… on JUCE → path in field
  4. Artefacts: Windows/macOS/Linux labels, no Choose…
  5. Import prefs → Project tab unchanged; restart app → new seed visible
  6. Open existing project → destination recalculated from filesystem (unchanged behaviour)

### Cross-Story Dependencies

| Story | Relationship |
|-------|--------------|
| 5.1 | **Done** — `FolderField`, `seed_dict()`, artefact labels, Import/Export |
| 5.3 | **Prerequisite for AC5** — `ProjectSpec.juce_dir`, generate pipeline reads spec |
| 5.4 | Removes prefs sync on Open/Generate |
| 5.5 | `Create New Project` full reset from `seed_dict()` + dirty guard |

### Previous Story Intelligence (5.1)

Story 5.1 delivered:
- `app/widgets/folder_field.py` — reuse verbatim on Project tab
- `Preferences.seed_dict()` with `destinationDir`, `juceDir`, plugin type, formats, compilation, artefacts
- `reload_from_prefs()` pattern for section widgets — mirror in `ProjectPage.load()`
- Review fixes: `FolderField.set_value` calls `_on_text_changed`; artefact validation skips paths when copy flag off
- Legacy `manufacturer`/`destination` keys in `seed_dict()` — clean up in `_field_specs` when using `destinationDir` consistently
- Export blocks when form invalid; import full-replaces profile

**Do not regress:** Preferences auto-save, saved indicator, import/export, factory init.

### Git Intelligence

Recent commits (baseline `aec1e2e`):
- `aec1e2e` — Export live preferences profile only when form is valid (5.1 review fix)
- `93c0bc3` — Preferences profile workflow with auto-save and import/export (5.1)
- No Epic 5.2 code yet; `project_info.py` still has plain destination field inside form

### Latest Tech Notes

- **PySide6 ≥ 6.7**, **Python 3.14** — no new dependencies
- `QFileDialog.getExistingDirectory` — already used in `FolderField`
- `QStandardPaths.DesktopLocation` — Choose… fallback when field empty
- Clean-code: extract `_seed_new_project` if `__init__` grows; share path spec helpers if duplication exceeds DRY threshold

### Project Structure Notes

- Primary edits: `app/pages/project_info.py`, `app/pages/project.py`
- Optional shared helper: `app/pages/path_specs.py`
- Run app: `.venv/bin/python main.py`
- Run tests: `.venv/bin/pytest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.2]
- [Source: docs/USER-MANUAL.md §5.1, §5.5, §6.1.1, §12]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md#AD-2, #AD-7]
- [Source: _bmad-output/implementation-artifacts/5-1-preferences-model-profile-workflow.md]
- [Source: app/pages/project_info.py — current layout gap]
- [Source: app/pages/preferences.py — FolderField reference]
- [Source: app/widgets/folder_field.py]
- [Source: core/preferences.py — seed_dict()]

## Dev Agent Record

### Agent Model Used

claude-4.6-sonnet-medium-thinking

### Debug Log References

### Completion Notes List

- Rebuilt `ProjectInfoPage`: identity-only `ValidatedForm`, Bundle ID, then `FolderField` rows for destination and JUCE directory (label → Choose… → text field).
- Extracted shared path specs to `app/pages/path_specs.py`; `PreferencesPage` now imports `destination_field_spec` / `juce_field_spec`.
- Added `ProjectPage._seed_new_project()` so cold start applies full `seed_dict()` via `ProjectSpec.from_dict` (type, formats, compilation, artefacts, paths).
- `ProjectInfoPage.values()` emits `destinationDir` and `juceDir`; `ProjectPage.spec()` picks up `juce_dir` via existing 5.3 `ProjectSpec` field.
- Verified `ArtefactsSection` unchanged (Windows/macOS/Linux labels, no Choose…).
- Tests: 128 passed (added `test_path_specs.py`, `test_seed_dict_round_trips_through_project_spec`).

### File List

- app/pages/path_specs.py (new)
- app/pages/project_info.py (modified)
- app/pages/project.py (modified)
- app/pages/preferences.py (modified)
- tests/unit/test_path_specs.py (new)
- tests/unit/test_preferences.py (modified)

### Change Log

- 2026-06-25: Story 5.2 — Project tab FolderField layout for destination/JUCE; full prefs seed at startup; shared path_specs helpers.

### Review Findings

- [x] [Review][Decision] AC4 — reseed Project tab après import prefs ? — **Résolu (option 2)** : UI Project inchangée après import ; `_defaults` rafraîchi seulement. Reseed complet au cold start (`_seed_new_project`) et via Create New Project (5.5). AC4 wording à clarifier en doc si besoin.
- [x] [Review][Patch] `juceDir` null dans `ProjectInfoPage.load()` [app/pages/project_info.py:91]
- [x] [Review][Defer] `reset()` ne reseed que `ProjectInfoPage` [app/pages/project.py:64-66] — deferred, pre-existing (Story 5.5)
- [x] [Review][Defer] `prefs.get()` peut propager `None` vers `FolderField` [app/pages/preferences.py:46-59] — deferred, pre-existing
- [x] [Review][Defer] `reset()` incomplet si appelé après changement type/formats [app/pages/project.py:64-66] — deferred, pre-existing (Story 5.5)
- [x] [Review][Defer] Rollback `import_from_file` sans garde sur `ValueError` [app/pages/preferences.py:107-109] — deferred, pre-existing
- [x] [Review][Defer] Accès attributs privés `_artefacts._checks` [app/pages/preferences.py:169-172] — deferred, pre-existing
