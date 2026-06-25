---
baseline_commit: 09470bb
---

# Story 5.4: Decouple Open/Generate from preferences.json

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer,
I want Open and Generate to leave my global Preferences untouched,
So that working on one project never overwrites my default profile.

## Acceptance Criteria

1. **Given** I open or generate a project successfully, **when** the operation completes, **then** `preferences.json` is **not** modified (no `prefs.update(spec)`, no `prefs.save()` in `_load_project` or `_run_generation`).
2. **Given** a successful Generate, **when** generation completes, **then** the last-used **parent** destination folder is remembered for subsequent Choose… and Open Project… starting directories.
3. **Given** the remembered parent path is missing or invalid, **when** Choose… or Open needs a default, **then** Desktop (via OS API) is used as fallback.
4. **Given** destination folder is empty or invalid before Generate on a new project, **when** I click Generate, **then** Luthier may prompt via Choose… or folder dialog before continuing.
5. **Given** AD-5 in ARCHITECTURE-SPINE.md, **when** Epic 5.4 is complete, **then** the revised AD-5 rule is satisfied and `project-context.md` reflects the new persistence model.
6. **Given** a known `preferences.json` snapshot before Open or Generate, **when** open project → generate completes successfully, **then** automated test or documented manual scenario confirms `preferences.json` mtime and content are unchanged.

## Tasks / Subtasks

- [x] Remove prefs sync from Open and Generate (AC: 1, 5, 6)
  - [x] In `app/main_window.py` `_load_project()`: delete `self._prefs.update(spec)` and the `try/except` block calling `self._prefs.save()` — keep `self._project_page.load(spec)` and status messaging only
  - [x] In `app/main_window.py` `_run_generation()`: delete `self._prefs.update(spec)` and `self._prefs.save()` after successful `generate()` — keep success/error `_set_status` only
  - [x] Remove `Preferences.update(self, spec: ProjectSpec)` from `core/preferences.py` (only callers were MainWindow; Story 5.1 AC9)
  - [x] Remove dead `generation_config()` from `core/preferences.py` if still unused (grep shows zero callers)
  - [x] Grep codebase: zero hits for `prefs.update(` or `Preferences.update` outside planning docs

- [x] Add last-used parent persistence separate from `preferences.json` (AC: 2, 3, 5)
  - [x] Create `core/app_state.py` — lightweight JSON persistence at `{AppConfigLocation}/Luthier/app_state.json` (same parent dir as `preferences.json`, **different file** per USER-MANUAL §9)
  - [x] Schema: `{"lastUsedParentDir": "<path>"}` — **not** part of `_PROFILE_KEYS`; never included in Import/Export profile
  - [x] `AppState.default_path()` → sibling of `Preferences.default_path()` with filename `app_state.json`
  - [x] `remember_parent(dir_path: str) -> None` — store `str(Path(dir_path).resolve())` when non-empty (destination folder **is** the parent per USER-MANUAL §11)
  - [x] `dialog_start_dir(field_value: str = "") -> str` — return order: valid existing `field_value` → valid `lastUsedParentDir` → Desktop via `QStandardPaths.StandardLocation.DesktopLocation` → `str(Path.home())` if Desktop empty (mirror `factory_defaults()` fallback)
  - [x] `_is_valid_dir(path: str) -> bool` — non-empty strip and `Path(path).is_dir()`
  - [x] `MainWindow.__init__`: `self._app_state = AppState(AppState.default_path())`; load existing file if present
  - [x] After successful `_run_generation()`: `self._app_state.remember_parent(spec.destination_dir)` then `self._app_state.save()`
  - [x] **Do not** call `remember_parent` on Open — only after successful Generate (USER-MANUAL §5.6, §9)

- [x] Wire dialog start directories to `AppState` (AC: 2, 3)
  - [x] `MainWindow._on_open()`: replace `self._prefs.get("destination")` with `self._app_state.dialog_start_dir()`
  - [x] `FolderField._choose_directory()`: accept optional `start_dir_resolver: Callable[[str], str] | None` — when provided, `start = resolver(self.value())` instead of `self.value() or Desktop`
  - [x] `ProjectInfoPage` / `PreferencesPage`: pass resolver `lambda v: app_state.dialog_start_dir(v)` into destination `FolderField` constructors (inject `AppState` or callable from `MainWindow` via constructor — prefer passing callable to avoid threading `AppState` through every page if a single lambda from MainWindow suffices)
  - [x] JUCE `FolderField` Choose… may use same resolver (consistent UX) or keep field-value-then-Desktop — either is acceptable; destination field is the AC-critical path

- [x] Optional destination prompt before Generate (AC: 4)
  - [x] In `MainWindow._on_generate()` before `_confirm_overwrite`: if `spec.destination_dir` empty or not a valid directory, show `QFileDialog.getExistingDirectory` with title e.g. `"Choose destination folder"`, start dir from `self._app_state.dialog_start_dir()`
  - [x] If user picks a folder, update Project tab destination field (`ProjectInfoPage` destination `set_value`) and rebuild `spec` from `self._project_page.spec()` before overwrite confirm
  - [x] If user cancels dialog, abort generate (no status error required — silent cancel is fine)
  - [x] If destination already valid, no extra prompt (preserves one-click regenerate after Open per USER-MANUAL §5.6)

- [x] Update `project-context.md` (AC: 5)
  - [x] Revise **Preferences Persistence** section: AD-5 revised rule — writes only factory init, Preferences auto-save, Import; Open/Generate never touch `preferences.json`
  - [x] Add **App state** bullet: `app_state.json` holds `lastUsedParentDir`; written only after successful Generate
  - [x] Fix stale known issue #4 ("Preferences not saved on change") and #6 (JUCE dir) where contradicted by Epic 5 work
  - [x] Update data-flow diagram if it still implies prefs sync on generate/open

- [x] Unit tests (AC: 1, 2, 3, 6)
  - [x] Add `tests/unit/test_app_state.py`:
    - `test_remember_parent_persists_to_file`
    - `test_dialog_start_dir_prefers_field_value_when_valid`
    - `test_dialog_start_dir_uses_last_parent_when_field_empty`
    - `test_dialog_start_dir_falls_back_to_desktop_when_parent_invalid` (mock `QStandardPaths` + `Path.is_dir`)
    - `test_app_state_save_does_not_touch_preferences_json` (sibling files in `tmp_path`)
  - [x] Add `tests/unit/test_preferences_decouple.py` (or extend `test_preferences.py`):
    - `test_preferences_file_unchanged_after_simulated_open_generate_workflow` — create prefs file, snapshot content+mtime, run operations that **only** touch `AppState` + in-memory project load simulation; assert prefs file identical
  - [x] Optional integration: extend `tests/integration/test_round_trip.py` with `test_generate_does_not_modify_preferences_json` — tmp prefs path injected if feasible; otherwise document manual scenario in Dev Notes

- [x] Regression
  - [x] `.venv/bin/pytest` — full suite green
  - [x] Grep: no `prefs.update` / `prefs.save` in `_load_project` or `_run_generation`
  - [x] Manual smoke (document in completion notes): set distinct prefs destination vs project destination → Open → Generate → verify `preferences.json` unchanged; Choose… / Open start at last generated parent

## Dev Notes

### Scope — Decouple + UX Memory (Not Create New Project)

Story 5.4 owns **removing the prefs write path on Open/Generate** and **last-used parent folder memory**. Story 5.5 owns Create New Project full reset + dirty guard — do not implement dirty tracking here beyond what AC4 needs for destination prompt.

### Current State — Exact Code to Remove

`app/main_window.py` still syncs project state into global prefs after Open and Generate:

```235:242:app/main_window.py
        self._project_page.load(spec)
        self._prefs.update(spec)
        try:
            self._prefs.save()
        except OSError as error:
            self._set_status(f"Loaded {spec.project_name} — preferences not saved: {error}", ok=False)
            return
        self._set_status(f"Loaded {spec.project_name} from {project_dir}", ok=True)
```

```260:266:app/main_window.py
        self._prefs.update(spec)
        try:
            self._prefs.save()
        except OSError as error:
            self._set_status(f"Project generated at {project_dir} — preferences not saved: {error}", ok=False)
            return
        self._set_status(f"Project generated at {project_dir}", ok=True)
```

After removal, `_load_project` success path is: load spec into Project tab → `_set_status` OK. `_run_generation` success path is: generate → remember parent in `AppState` → `_set_status` OK.

`Preferences.update()` at `core/preferences.py:221-237` maps a subset of `ProjectSpec` fields into profile keys — this was the mechanism that overwrote global defaults with per-project values. **Delete the method**; profile workflow uses `apply_form` / `apply_profile` only (Story 5.1).

### Why `app_state.json` Is Separate from `preferences.json`

USER-MANUAL §9 table lists two distinct persistence targets:

| Storage | Modified by |
|---------|-------------|
| `preferences.json` | Factory init, Preferences auto-save, Import |
| Last-used parent (config app) | Successful Generate only |

AC1 forbids modifying `preferences.json` on Open/Generate. Remembering last parent **after Generate** therefore **must** use a separate file. Do **not** add `lastUsedParentDir` to `_PROFILE_KEYS` or `preferences.json` — it would either violate AC1 or require splitting save logic awkwardly.

### Architecture Compliance

**AD-5 (this story implements it in code):** `preferences.json` written only by: (1) first-launch factory creation, (2) Preferences tab auto-save, (3) Import Preferences. `MainWindow` calls `prefs.save()` only after Preferences auto-save signal or successful import — **never** after Open or Generate. Open/Generate must not call `Preferences.update(ProjectSpec)`.

**AD-2:** Project and Preferences tabs show the same field set but **sources differ** — opened/generated project populates Project from disk/sidecar; new project seeds from `preferences.json`. Removing `update(spec)` enforces this boundary.

**AD-7 (already done in 5.3):** Generate reads `spec.juce_dir` only. Decoupling prefs does not reintroduce prefs injection at generate time.

**AD-8:** `AppState` lives in `core/`; may use `QStandardPaths` for Desktop fallback (same pattern as `Preferences.factory_defaults()`). Qt dialogs stay in `app/main_window.py` and `FolderField`.

**AD-6:** No Qt widget tests. Test `AppState` and prefs immutability with `tmp_path` + mocked `QStandardPaths`.

### Files to Touch

| File | Change |
|------|--------|
| `app/main_window.py` | Remove prefs sync; add `AppState`; wire Open/Generate/generate-prompt |
| `core/preferences.py` | Remove `update(spec)`; optional remove `generation_config()` |
| `core/app_state.py` | **New** — last-used parent persistence |
| `app/widgets/folder_field.py` | Optional `start_dir_resolver` for Choose… |
| `app/pages/project_info.py` | Pass resolver to destination `FolderField` (if not wired from MainWindow) |
| `app/pages/preferences.py` | Pass resolver to destination `FolderField` (optional but recommended) |
| `tests/unit/test_app_state.py` | **New** |
| `tests/unit/test_preferences_decouple.py` or `test_preferences.py` | Prefs immutability test |
| `_bmad-output/project-context.md` | AD-5 persistence model + app_state |

### Do NOT Touch in This Story

| File | Reason |
|------|--------|
| `core/project_spec.py`, `core/render_context.py`, `core/project_generator.py` | Pipeline complete in 5.3 |
| `app/pages/project.py` `reset()` dirty guard | Story 5.5 |
| `ARCHITECTURE-SPINE.md` | Already revised 2026-06-25; code catches up here |
| `Docs/USER-MANUAL.md` | Already documents target behaviour — optional typo sync only |
| Epic 1–3 story files | Historical; supersession note in epics.md |

### Implementation Details — `AppState`

Suggested minimal API:

```python
# core/app_state.py
class AppState:
    def __init__(self, path: Path): ...
    @staticmethod
    def default_path() -> Path:
        return Preferences.default_path().parent / "app_state.json"

    def load(self) -> None: ...
    def save(self) -> None: ...
    def remember_parent(self, dir_path: str) -> None: ...
    def dialog_start_dir(self, field_value: str = "") -> str: ...
```

`remember_parent` stores `spec.destination_dir` as-is — in Luthier, destination folder **is** the parent directory (project lands at `destination_dir / project_name`). Do not call `.parent` on it.

Validity check for dialog start: `Path(path).is_dir()` — same semantics as "missing or invalid" in AC3.

### Implementation Details — Open Project Start Directory

**Today (wrong after 5.4):** `_on_open` uses `self._prefs.get("destination")` — reads global profile default, conflating domains.

**Target:** `self._app_state.dialog_start_dir()` — last generated parent, else Desktop.

Opening a project does **not** update last-used parent (USER-MANUAL §9). Only successful Generate does.

### Implementation Details — Generate Destination Prompt (AC4)

`ProjectPage.is_valid()` requires valid destination via `validate_destination` — empty destination disables Generate button today. AC4 "may prompt" applies when:

- Field has text but path is not an existing directory (typo, deleted folder, copied project path confusion), **or**
- Future validity rules change

Recommended guard in `_on_generate`:

```python
dest = spec.destination_dir.strip()
if not dest or not Path(dest).is_dir():
    chosen = QFileDialog.getExistingDirectory(
        self, "Choose destination folder",
        self._app_state.dialog_start_dir(dest),
    )
    if not chosen:
        return
    self._project_page._info._destination.set_value(chosen)  # prefer a small public setter on ProjectInfoPage
    spec = self._project_page.spec()
```

Add `ProjectInfoPage.set_destination(value: str)` if direct `_destination` access feels too brittle — one-liner delegating to `FolderField.set_value`.

### Implementation Details — Success Status Messages

Simplify messages after removing prefs save error paths:

- Open success: `Loaded {spec.project_name} from {project_dir}` (unchanged)
- Generate success: `Project generated at {project_dir}` (unchanged)
- Remove "preferences not saved" branches — they only existed because of `prefs.save()` after open/generate

### Testing Strategy

**Automated (required):**

1. `AppState` round-trip and fallback chain (mocked Desktop, mocked `is_dir`)
2. Writing `app_state.json` does not create or modify `preferences.json`
3. After story: grep/static assertion that `Preferences.update` is gone

**Manual scenario (AC6 — document in completion notes if not fully automated):**

1. Note `preferences.json` content and mtime (or checksum)
2. Set Preferences destination to `/tmp/prefs-dest`; set Project destination to a different valid path
3. Generate project successfully
4. Open another existing project
5. Generate again (regenerate or second project)
6. Assert `preferences.json` byte-identical to step 1 snapshot; `app_state.json` contains last generated parent

### Cross-Story Dependencies

| Story | Relationship |
|-------|--------------|
| 5.1 ✅ | Profile API (`apply_profile`, `seed_dict`, auto-save) — prefs writes stay on Preferences tab only |
| 5.2 ✅ | `FolderField` on Project destination + JUCE; Choose… layout exists |
| 5.3 ✅ | `generate(spec)` without prefs `juce_dir` injection — decouple must not re-add prefs reads at generate |
| 5.5 | Create New Project reads `seed_dict()` only; dirty guard separate from this story |

### Previous Story Intelligence

**5.3 (done, commit `09470bb`):** Explicitly left `prefs.update(spec)` + `save()` in `_run_generation` for Story 5.4. Generate already uses `spec.juce_dir` only. Do not revert pipeline changes.

**5.2 (done):** `ProjectInfoPage` has `FolderField` for destination and JUCE. `ProjectPage._seed_new_project()` seeds from prefs at startup. Open loads project into form without touching prefs after this story.

**5.1 (done):** `PreferencesPage` auto-save is the only routine prefs writer besides factory/import. `update()` documented as legacy — safe to delete once MainWindow call sites removed.

**5.3 review deferrals still open (do not fix in 5.4 unless trivial):** CMake-only open losing `juceDir` in UI — sidecar path handles normal flow.

### Git Intelligence

Recent Epic 5 commits:

- `09470bb` — Story 5.3: `juce_dir` on `ProjectSpec`; `generate(spec)` only; **prefs sync still present** on open/generate
- `aec1e2e` / `93c0bc3` — Story 5.1: profile workflow, import/export

Only `app/main_window.py` lines ~236-241 and ~260-265 need prefs removal for core AC1. New `AppState` module is the main addition.

### Latest Tech Information

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- `QStandardPaths.StandardLocation.DesktopLocation` — same API used in `factory_defaults()` and `FolderField`
- `QFileDialog.getExistingDirectory(parent, title, start_dir)` — unchanged Qt API
- No library upgrades required

### Project Structure Notes

- New file `core/app_state.py` follows `core/preferences.py` JSON persistence pattern
- `app_state.json` colocated with `preferences.json` under OS AppConfigLocation/Luthier/
- Run tests: `.venv/bin/pytest`
- Run app: `.venv/bin/python main.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.4]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-06-25.md#Story-5.4]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md#AD-5]
- [Source: docs/USER-MANUAL.md#§5.6, §9, §11]
- [Source: _bmad-output/implementation-artifacts/5-3-jucedir-on-projectspec-generation-pipeline.md — explicit deferral of prefs removal]
- [Source: _bmad-output/implementation-artifacts/5-1-preferences-model-profile-workflow.md — AC9 update() removal deferred to 5.4]
- [Source: app/main_window.py — `_load_project`, `_run_generation`, `_on_open`]
- [Source: core/preferences.py — `update()` to remove]
- [Source: app/widgets/folder_field.py — Choose… start directory]

## Dev Agent Record

### Agent Model Used

claude-4.6-sonnet-medium-thinking

### Debug Log References

### Completion Notes List

- Removed `prefs.update(spec)` / `prefs.save()` from `_load_project` and `_run_generation`; deleted `Preferences.update()` and unused `generation_config()`.
- Added `core/app_state.py` with `lastUsedParentDir` persistence in sibling `app_state.json`; `remember_parent` called only after successful Generate.
- Wired `dialog_start_dir` resolver through `MainWindow` → `ProjectPage` / `PreferencesPage` → `FolderField` Choose…; Open Project uses `app_state` not prefs destination.
- Added destination folder prompt in `_on_generate` when path empty or invalid; `ProjectPage.set_destination()` delegates to `ProjectInfoPage`.
- Updated `_bmad-output/project-context.md`: AD-5 revised rule, App State section, data-flow diagram, known issues #4/#6.
- Tests: 7 `test_app_state.py` + 2 `test_preferences_decouple.py`; full suite 137 passed.
- Manual smoke (AC6): set Preferences destination distinct from Project destination → Generate → confirm `preferences.json` unchanged; `app_state.json` holds last generated parent; Open/Choose… start at remembered parent.

### File List

- app/main_window.py
- core/app_state.py (new)
- core/preferences.py
- app/widgets/folder_field.py
- app/pages/project_info.py
- app/pages/project.py
- app/pages/preferences.py
- tests/unit/test_app_state.py (new)
- tests/unit/test_preferences_decouple.py (new)
- _bmad-output/project-context.md

### Change Log

- 2026-06-25: Story 5.4 — decouple Open/Generate from preferences.json; add AppState last-used parent persistence; AD-5 implemented in code.

### Review Findings

- [x] [Review][Patch] `AppState.save()` OSError non géré après génération réussie [`app/main_window.py:272`] — corrigé : try/except avec message de statut.
- [x] [Review][Patch] Génération sans re-validation après prompt destination [`app/main_window.py:214`] — corrigé : `is_valid()` après `set_destination`.
- [x] [Review][Defer] Tests AC6 simulés, pas de parcours MainWindow e2e [`tests/unit/test_preferences_decouple.py`] — deferred, pré-existant pattern AD-6 (pas de tests widget Qt)
- [x] [Review][Defer] Prompt destination AC4 non couvert par tests automatisés [`app/main_window.py:206`] — deferred, gap de couverture hors scope patch code
- [x] [Review][Defer] `AppState.load()` avale JSON/OSError silencieusement [`core/app_state.py:36`] — deferred, pré-existant (même pattern que `Preferences._read()`)
- [x] [Review][Defer] Écriture JSON non-atomique [`core/app_state.py:48`] — deferred, pré-existant (même pattern que `Preferences.save()`)
- [x] [Review][Defer] Pas de champ version dans `app_state.json` [`core/app_state.py`] — deferred, même dette que `preferences.json` (revue 5-1)
- [x] [Review][Defer] `ARCHITECTURE-EXPLAINED.md` AD-5 obsolète — deferred, hors File List story 5.4
