---
baseline_commit: b75b96d
---

# Story 5.5: Create New Project (Full Reset + Dirty Guard)

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer,
I want Create New Project to reset the form from my current Preferences profile,
So that I can start a fresh plugin without affecting global settings or a previously opened project config.

## Acceptance Criteria

1. **Given** I click **Create New Project**, **when** the form is clean (no unsaved edits since last stable state), **then** project name and display name are cleared, version set to `1.0.0`, and all other fields re-seeded from `preferences.json`.
2. **Given** the Project form has unsaved edits (dirty), **when** I click **Create New Project**, **then** a confirmation dialog warns before discarding changes.
3. **Given** Create New Project completes, **when** I inspect `preferences.json`, **then** it is unchanged (read-only use of prefs for seeding).
4. **Given** dirty-state tracking, **when** I load a project, edit fields, or reset, **then** baseline updates appropriately so the dirty guard reflects real user edits.
5. **Given** a stable baseline event (cold-start seed from preferences, successful Open, or successful Create New Project), **when** the event completes, **then** the dirty baseline is updated so subsequent edits are detected relative to that stable state.

## Tasks / Subtasks

- [x] Fix full-form reset (AC: 1, 4, 5)
  - [x] Replace partial `ProjectPage.reset()` (currently only `_info.load()`) with the same full path as `_seed_new_project()` — call `load(ProjectSpec.from_dict(seed))` so type, formats, compilation, and artefacts re-seed from prefs
  - [x] Extract shared helper e.g. `_new_project_seed(defaults: dict) -> dict` used by both `_seed_new_project()` and `reset()` to avoid drift
  - [x] `reset(defaults)` must **not** write `preferences.json` — read-only via passed `defaults` (from `Preferences.seed_dict()`)

- [x] Implement dirty baseline tracking (AC: 2, 4, 5)
  - [x] Add `ProjectPage._baseline: dict` snapshot (from `spec().to_dict()` after normalization)
  - [x] Add `_capture_baseline() -> None` — store `self.spec().to_dict()` at end of every stable event
  - [x] Call `_capture_baseline()` at end of `load()` (covers cold start, Open, Create New Project reset)
  - [x] Add `is_dirty() -> bool` — compare current `spec().to_dict()` to `_baseline` with a pure equality helper (see Dev Notes)
  - [x] **Do not** update baseline on Generate — USER-MANUAL §5.6 and epic AC list only cold-start, Open, Create New Project as stable events
  - [x] **Do not** update baseline on Preferences import — Project tab unchanged until Create New Project (Story 5.1/5.2 behaviour preserved)

- [x] Wire Create New Project with confirmation (AC: 1, 2, 3)
  - [x] Replace inline lambda on Create New Project button with `MainWindow._on_create_new_project()`
  - [x] If `self._project_page.is_dirty()`: show `QMessageBox.question` (title e.g. `"Create New Project"`, message per USER-MANUAL §5.6 — discard unsaved changes); default button **No**; abort on No/Cancel
  - [x] On proceed: `self._project_page.reset(self._form_defaults())` — use live `seed_dict()`, not stale cache-only path
  - [x] Optional status: `"New project — defaults from Preferences."` (ok=True) — keep brief; no prefs write

- [x] Update baseline after successful Open (AC: 4, 5)
  - [x] Verify `_load_project()` calls `self._project_page.load(spec)` — baseline capture happens inside `load()`; no extra MainWindow hook needed if implemented there

- [x] Unit tests (AC: 1, 3, 4, 5 — AD-6, no Qt widgets)
  - [x] Add `tests/unit/test_project_dirty_guard.py` (or extend existing project tests):
    - `test_new_project_seed_clears_identity_preserves_profile_fields` — pure helper builds seed dict; assert empty names, version `1.0.0`, profile keys preserved
    - `test_form_snapshots_equal_detects_field_change` — equality helper returns False when one key differs
    - `test_form_snapshots_equal_ignores_display_name_fallback` — document/normalize rule if `ProjectInfoPage.values()` fills empty display name from project name (compare via `spec().to_dict()` semantics, not raw widget values)
    - `test_create_new_project_seed_does_not_mutate_preferences_file` — tmp_path prefs snapshot; simulate seed_dict read + seed merge only; assert prefs bytes unchanged
  - [x] Optional: extract pure helpers to `core/project_form_state.py` if keeping `ProjectPage` under 200 lines — only if needed for testability without Qt

- [x] Regression
  - [x] `.venv/bin/pytest` — full suite green
  - [x] Manual smoke (document in completion notes):
    1. Cold start → Project matches prefs; Create New Project (no edits) → no dialog; form unchanged except identity still empty
    2. Open project → edit plugin type → Create New Project → dialog appears → No keeps edits → Yes re-seeds from prefs (not opened project values)
    3. Edit Project fields → Generate → Create New Project still warns (Generate is not a stable baseline)
    4. Import prefs with different plugin type → Project UI unchanged → Create New Project → new type/formats from imported prefs; `preferences.json` only changed by import, not by Create New Project click
    5. Confirm `preferences.json` mtime unchanged after Create New Project alone

## Dev Notes

### Scope — Full Reset + Dirty Guard (Final Epic 5 Story)

Story 5.5 closes Epic 5 workflow UX. It fixes the known **`reset()` only re-seeds Project Info** bug (deferred from 5-2 review) and adds dirty confirmation before discarding edits.

**In scope:** `ProjectPage.reset()` full re-seed, baseline snapshot, confirmation dialog, prefs read-only seeding, unit tests for pure helpers.

**Out of scope:** Visual “unsaved changes” indicator on Project tab; baseline update on Generate; re-seeding Project tab immediately on Preferences import (explicitly deferred to Create New Project / cold start per USER-MANUAL §6.2); `ARCHITECTURE-EXPLAINED.md` AD-5 sync (deferred from 5-4).

### Current State — Exact Gap

**Create New Project button today** (`app/main_window.py:144-145`):

```python
self._new_btn = _make_btn("Create New Project", "ActionButton",
                          lambda: self._project_page.reset(self._form_defaults()))
```

**Broken reset** (`app/pages/project.py:72-74`):

```python
def reset(self, defaults: dict) -> None:
    vals = {**defaults, "projectName": "", "projectDisplayName": "", "projectVersion": "1.0.0"}
    self._info.load(vals)  # BUG: type/formats/compilation/artefacts NOT reset
```

**Correct cold-start seed** (same file, lines 42-49) — this is the pattern `reset()` must reuse:

```python
def _seed_new_project(self, defaults: dict) -> None:
    seed = {**defaults, "projectName": "", "projectDisplayName": "", "projectVersion": "1.0.0"}
    self.load(ProjectSpec.from_dict(seed))
```

**No dirty tracking exists** — grep shows zero `is_dirty` / baseline in app code. Confirmation dialog never shown.

### Target Behaviour (USER-MANUAL §5.6)

| Action | Identity fields | All other Project fields | `preferences.json` |
|--------|-----------------|--------------------------|-------------------|
| Create New Project (clean) | Cleared / `1.0.0` | Re-seeded from current prefs profile | Unchanged (read-only) |
| Create New Project (dirty) | Same after confirm | Same after confirm | Unchanged |
| Preferences import | Unchanged on Project tab | Unchanged until next Create New Project | Updated by import |

Stable baseline events (reset dirty flag):

1. Cold-start `_seed_new_project()` after init
2. Successful **Open Project…** (`load(spec)` from disk)
3. Successful **Create New Project** (after confirm if needed)

**Not** stable: Generate Project, Preferences auto-save, Import (Project tab untouched).

### Implementation — Dirty Baseline

**Recommended approach:** snapshot dict comparison via existing `ProjectSpec` contract (AD-1).

```python
def _capture_baseline(self) -> None:
    self._baseline = self.spec().to_dict()

def is_dirty(self) -> bool:
    return not _form_snapshots_equal(self._baseline, self.spec().to_dict())
```

Call `_capture_baseline()` as the **last line** of `load()` so every stable load path updates baseline automatically.

**Comparison helper** — implement as a pure function (module-level in `project.py` or `core/project_form_state.py`):

- Compare all keys in `ProjectSpec.to_dict()` output
- Normalize strings: strip whitespace for path/text fields if needed; bools as-is
- **Display name rule:** `spec()` path uses `ProjectInfoPage.values()` which sets empty display name → project name. Always compare via `spec().to_dict()` on both sides so baseline and current use the same normalization (do not compare raw `_form.values()` vs baseline)

**Generate does not call `load()`** — baseline stays at last Open/reset/cold-start. User who edits then generates remains dirty until Create New Project or Open — matches epic AC5 wording.

### Implementation — Confirmation Dialog

Keep dialog in `MainWindow` (AD-8: Qt in app layer):

```python
def _on_create_new_project(self) -> None:
    if self._project_page.is_dirty():
        answer = QMessageBox.question(
            self,
            "Create New Project",
            "The project form has unsaved changes. Discard them and start a new project?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
    self._project_page.reset(self._form_defaults())
```

Use `_form_defaults()` → `self._prefs.seed_dict()` for **live** prefs (after import or auto-save on Preferences tab). Do not rely on `self._defaults` cache alone — though import refreshes cache, live read is safer and matches button intent (“current Preferences profile”).

### Architecture Compliance

**AD-1:** Baseline and dirty check use `ProjectSpec.to_dict()` — no raw cross-layer dict assembly.

**AD-2:** Create New Project seeds Project from `preferences.json` via `seed_dict()`; opened project values are discarded on reset. Reinforces Project vs Preferences source separation completed in 5.4.

**AD-5:** Create New Project must **never** call `prefs.save()`, `apply_form`, or `apply_profile`. Read-only `seed_dict()` only. Grep after implementation: no new prefs write paths from `_on_create_new_project` / `reset()`.

**AD-6:** No Qt widget tests. Unit-test pure seed builder and snapshot equality only. Manual smoke covers dialog UX.

**AD-8:** Dirty baseline state lives in `ProjectPage`; confirmation dialog in `MainWindow`. Do not import Qt in `core/`.

### Files to Touch

| File | Change |
|------|--------|
| `app/pages/project.py` | Fix `reset()`; extract `_new_project_seed()`; `_baseline`, `_capture_baseline()`, `is_dirty()`; call capture at end of `load()` |
| `app/main_window.py` | `_on_create_new_project()` with dirty guard; wire button |
| `core/project_form_state.py` (optional) | Pure `new_project_seed()`, `form_snapshots_equal()` if extracted for tests |
| `tests/unit/test_project_dirty_guard.py` | **New** — pure helper tests |
| `_bmad-output/project-context.md` | Optional one-line under Feature Goals / Known Issues: mark deferred `reset()` bug resolved |

### Do NOT Touch in This Story

| File | Reason |
|------|--------|
| `core/preferences.py` | `seed_dict()` complete since 5.1 — read-only use only |
| `core/app_state.py` | Last-used parent is Generate-only (5.4) |
| `core/project_generator.py`, `render_context.py` | Pipeline complete |
| `app/pages/preferences.py` | Import does not reseed Project (by design) |
| `app/main_window.py` `_load_project` / `_run_generation` | Prefs decouple done in 5.4 — do not reintroduce sync |
| Epic 4 stories | Out of scope |

### Seed Dict Keys (Reference)

`Preferences.seed_dict()` (`core/preferences.py:172-197`) returns all fields needed for full `ProjectPage.load()`:

- Identity (manufacturer*, codes, copyright, website, email) — preserved on reset
- `destinationDir`, `juceDir`
- `pluginType`, `pluginFormats`, `cxxStandard`, `preprocessorDefinitions`, `headerSearchPaths`
- Artefact flags + `artefactsDirWindows/Macos/Linux`
- Legacy aliases `manufacturer`, `destination` for `ProjectInfoPage` init — still present; full load uses camelCase keys from `ProjectSpec.from_dict`

Reset overlay (always applied):

```python
{"projectName": "", "projectDisplayName": "", "projectVersion": "1.0.0"}
```

### Cross-Story Dependencies

| Story | Relationship |
|-------|--------------|
| 5.1 ✅ | `seed_dict()` profile snapshot; import refreshes `_defaults` cache but not Project UI |
| 5.2 ✅ | Full `_seed_new_project()` via `load()` at startup; Choose… fields included in spec |
| 5.3 ✅ | `juceDir` in seed and sidecar — reset must re-seed JUCE from prefs |
| 5.4 ✅ | Open/Generate do not write prefs — Create New Project also read-only on prefs |
| Epic 5 complete | After 5.5 review → mark `epic-5` done when all stories done |

### Previous Story Intelligence

**5.4 (done, commit `b75b96d`):** Explicitly deferred dirty guard and full reset to 5.5. `Preferences.update()` removed. `_form_defaults()` returns live `seed_dict()`. `_load_project` only calls `load(spec)` — baseline hook belongs in `ProjectPage.load()`, not prefs sync.

**5.2 review deferrals (fix in this story):**

- `reset()` only `_info.load()` — **primary bug**
- Create New Project leaves plugin type/formats/compilation/artefacts from previous project

**5.1:** Import updates `_defaults` in MainWindow but not Project UI — Create New Project must read fresh prefs via `_form_defaults()` so imported profile applies.

**5.4 review deferrals (do not fix unless trivial):** AppState load/save patterns, ARCHITECTURE-EXPLAINED AD-5 stale doc.

### Git Intelligence

Recent Epic 5 commits:

- `b75b96d` — Story 5.4: decouple Open/Generate; AppState; **Create New Project still calls broken `reset()`**
- `09470bb` — Story 5.3: `juce_dir` on ProjectSpec
- `aec1e2e` / `93c0bc3` — Story 5.1: profile workflow

Minimal diff expected: ~40–80 lines in `project.py`, ~15 lines in `main_window.py`, new unit test file.

### Latest Tech Information

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- `QMessageBox.question(parent, title, text, buttons, defaultButton)` — standard Qt 6 API; use `QMessageBox.No` as default to prevent accidental discard
- No library upgrades required

### Testing Strategy

**Automated (required):**

1. Pure `new_project_seed()` / snapshot equality functions
2. Prefs file immutability when only seed logic runs (no `save()`)
3. Full pytest suite green

**Manual (required for AC2 dialog):**

1. Dirty → Create New Project → dialog → No → form unchanged
2. Dirty → Yes → full re-seed including plugin type/formats
3. Clean → no dialog
4. Open → edit → Create New Project → warns
5. Prefs mtime unchanged after reset

### Project Structure Notes

- Prefer keeping dirty helpers in `app/pages/project.py` if under class line limits; extract to `core/project_form_state.py` only if needed for AD-6 testing without importing Qt pages
- Run tests: `.venv/bin/pytest`
- Run app: `.venv/bin/python main.py`
- Clean-code limits: if `load()` + baseline capture exceeds 15 lines, extract `_capture_baseline()` as one-liner call at end of `load()`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.5]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-06-25.md#Story-5.5]
- [Source: docs/USER-MANUAL.md#§5.6 Create New Project]
- [Source: docs/USER-MANUAL.md#§12 Create New Project checklist]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md#AD-2, AD-5]
- [Source: _bmad-output/implementation-artifacts/5-4-decouple-open-generate-from-preferences-json.md — explicit 5.5 deferral]
- [Source: _bmad-output/implementation-artifacts/5-2-project-ui-choose-buttons-layout.md — reset() deferral]
- [Source: _bmad-output/implementation-artifacts/deferred-work.md — reset() bug tracked]
- [Source: app/pages/project.py — `_seed_new_project`, broken `reset()`]
- [Source: app/main_window.py — Create New Project button, `_form_defaults()`]
- [Source: core/preferences.py — `seed_dict()`]

## Dev Agent Record

### Agent Model Used

Composer (Cursor)

### Debug Log References

- Fixed `reset()` to use full `load()` path via shared `new_project_seed()` helper
- Baseline captured at end of `load()` — covers cold start, Open, Create New Project
- Generate does not call `load()` — dirty state preserved after generate (by design)

### Completion Notes List

- `core/project_form_state.py`: pure `new_project_seed()` and `form_snapshots_equal()` with display-name fallback normalization
- `ProjectPage.reset()` now re-seeds all sections (type, formats, compilation, artefacts) from prefs profile
- Dirty guard: `_baseline` snapshot + `is_dirty()` via `form_snapshots_equal`
- `MainWindow._on_create_new_project()`: confirmation dialog (default No) when dirty; live `seed_dict()`; status message on success
- No `preferences.json` writes on Create New Project path (grep verified)
- Tests: 4 new unit tests in `test_project_dirty_guard.py`; full suite 141 passed
- Manual smoke (2026-06-25, `Dist/Luthier.app`, rapport `5-5-manual-smoke-test-report.md`) : scénarios 1/2/3/5 PASS ; scénario 4 FAIL (import prefs ne semble pas changer le plugin type dans Preferences — à investiguer) ; retour UX status bar + bouton No dialog + persistance géométrie fenêtre

### File List

- `core/project_form_state.py` (new)
- `app/pages/project.py` (modified)
- `app/main_window.py` (modified)
- `tests/unit/test_project_dirty_guard.py` (new)

### Change Log

- 2026-06-25: Story 5.5 — full Create New Project reset, dirty baseline tracking, confirmation dialog, unit tests

### Review Findings (2026-06-25)

- [x] [Review][Defer] Manual smoke AC2 dialog not verified — defer until UI smoke before merge (5 scenarios in Tasks/Subtasks); completion notes already flag this; code path in `_on_create_new_project()` matches spec

### Manual Smoke Results (2026-06-25)

| # | Scénario | Résultat |
|---|----------|----------|
| 1 | Cold start, formulaire propre | PASS |
| 2 | Open + dialog No/Yes | PASS |
| 3 | Generate puis dirty guard | PASS |
| 4 | Import prefs puis Create New | FAIL |
| 5 | mtime `preferences.json` | PASS |

**Sign-off :** re-test après fix (Guillaume). Rapport : `5-5-manual-smoke-test-report.md`.

- [ ] [Smoke][Investigate] Scénario 4 — import ne met pas à jour le plugin type dans Preferences ; vérifier clé `"pluginType": "effect"` (pas le libellé UI « Synthesizer ») dans le JSON importé
- [ ] [Smoke][UX] Barre de messages dédiée au-dessus des boutons (ton #262F34, texte orange/rouge, centré) ; libellé « New project created — defaults from Preferences. »
- [ ] [Smoke][UX] Bouton No du dialog dirty guard visuellement distinct (ex. orange = action par défaut)
- [ ] [Smoke][Defer] Persistance taille/position fenêtre au lancement (hors scope 5.5)
