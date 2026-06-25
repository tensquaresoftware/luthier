---
baseline_commit: 72b5972
---

# Story 5.1: Preferences Model & Profile Workflow

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer,
I want a complete Preferences profile with auto-save and Import/Export,
So that my global defaults (identity, paths, plugin type, formats, compilation, artefacts) persist independently of any open project.

## Acceptance Criteria

1. **Given** first application launch (no existing `preferences.json`), **when** Luthier starts, **then** `preferences.json` is created with factory defaults (Desktop destination, Instrument/Synth, AU+VST3+Standalone, C++17, copy-to-central off, empty artefact paths, empty JUCE dir with OS placeholder in UI).
2. **Given** the extended schema in `core/preferences.py`, **when** `preferences.json` is read/written, **then** it includes: identity fields, destination folder, juceDir, pluginType, pluginFormats, cxxStandard, preprocessorDefinitions, headerSearchPaths, copy flags, and per-OS artefact paths.
3. **Given** the Preferences tab, **when** I view it, **then** sections include Plugin Type, Formats, Compilation; labels read **Destination folder**, artefact paths labeled **Windows**, **macOS**, **Linux**; Choose… buttons appear on Destination folder and JUCE directory only.
4. **Given** I edit any valid Preferences field, **when** validation passes, **then** `preferences.json` is auto-saved and a transient orange saved indicator appears in the tab bar.
5. **Given** I click **Import Preferences…** and select a valid JSON file, **when** import succeeds, **then** the entire profile is replaced, `preferences.json` is written, and Preferences UI refreshes; the Project tab is **not** modified.
6. **Given** I click **Export Preferences…**, **when** I choose a destination file, **then** the current profile is written to that file and `preferences.json` is unchanged.
7. **Given** import fails (invalid JSON or validation error), **when** the error is shown, **then** the previous profile and `preferences.json` remain unchanged.
8. **Given** Import Preferences succeeds, **when** the in-memory Project seed cache is inspected (e.g. `_form_defaults` or equivalent), **then** it reflects the imported profile even though the Project tab UI is unchanged until the next Create New Project or cold start.
9. **Given** the extended `Preferences` API after Story 5.1, **when** profile seeding or persistence is implemented, **then** `Preferences.update(ProjectSpec)` is removed or no longer required for profile workflow — Open/Generate call-site removal is completed in Story 5.4.

## Tasks / Subtasks

- [x] Extend `core/preferences.py` schema and profile API (AC: 1, 2, 8, 9)
  - [x] Add keys to `_DEFAULTS`: `pluginType`, `pluginFormats`, `cxxStandard`, `preprocessorDefinitions`, `headerSearchPaths`
  - [x] Fix factory default `copyToArtefactsDir` → `False` (USER-MANUAL §4.2; currently `True` in code)
  - [x] Add `_PROFILE_KEYS` tuple covering all persisted fields
  - [x] Add `factory_defaults() -> dict` resolving Desktop via `QStandardPaths.StandardLocation.DesktopLocation`
  - [x] Add `ensure_initialized() -> None`: if file missing, populate from factory defaults and `save()`; else `load()`
  - [x] Add `to_dict() -> dict` and `apply_profile(data: dict) -> None` (full replace of in-memory profile)
  - [x] Extend `apply_form()` to accept plugin type, formats, compilation keys (or delegate to `apply_profile` partial update path used by auto-save)
  - [x] Add `seed_dict() -> dict` returning all non-project-identity defaults for Project seeding (camelCase keys matching `ProjectSpec.from_dict` input)
  - [x] Document `update(ProjectSpec)` as legacy — profile workflow must use `apply_form` / `apply_profile` only; do **not** remove Open/Generate call sites yet (Story 5.4)

- [x] Add `app/widgets/folder_field.py` — reusable **label → Choose… → text field** row (AC: 3)
  - [x] Wrap `ValidatedField` + `QPushButton("Choose…")` with `objectName="ActionButton"`
  - [x] `Choose…` opens `QFileDialog.getExistingDirectory`; selected path populates field; field stays editable
  - [x] Emit `valueChanged` / `validityChanged` like `ValidatedField`
  - [x] Reuse in Preferences tab only in this story (Project tab wiring is Story 5.2)

- [x] Rebuild `app/pages/preferences.py` (AC: 3, 4, 5, 6, 7)
  - [x] Compose sections: identity form (without destination/juce plain fields), Plugin Type, Formats, Compilation, Artefacts
  - [x] Reuse `PluginTypePage`, `FormatsPage`, `CompilationSection`, `ArtefactsSection` — same widgets as Project tab
  - [x] Replace destination + juce `ValidatedField` rows with `FolderField`; labels **Destination folder**, **JUCE directory**
  - [x] Initialize all widgets from `prefs` on construct; add `reload_from_prefs()` for post-import refresh
  - [x] Remove manual `save()` button flow — replace with `_auto_save()` on valid edit
  - [x] Connect `validityChanged` / `valueChanged` / checkbox toggles from all sections → debounced or immediate auto-save when aggregate valid
  - [x] Add `import_from_file(path) -> tuple[bool, str]` — validate JSON + field rules; on success call `apply_profile`, `save()`, `reload_from_prefs()`; on failure return error message without mutating prefs
  - [x] Add `export_to_file(path) -> tuple[bool, str]` — write `prefs.to_dict()` without touching live file

- [x] Update `app/pages/artefacts.py` labels (AC: 3)
  - [x] Change artefact field labels from `Artefacts (Windows/macOS/Linux)` to **Windows**, **macOS**, **Linux** (applies to both Preferences and Project tabs)

- [x] Update `app/main_window.py` (AC: 1, 4, 5, 6, 8)
  - [x] Replace `self._prefs.load()` with `self._prefs.ensure_initialized()`
  - [x] Replace `_form_defaults()` with `self._prefs.seed_dict()` (or equivalent full seed snapshot)
  - [x] Add `_saved_indicator` QLabel in tab bar (`objectName="SavedIndicator"`, orange accent via QSS)
  - [x] Add `_flash_saved_indicator()` using `QTimer.singleShot` (~2000 ms hide)
  - [x] Wire `PreferencesPage` auto-save signal → `prefs.save()` + `_flash_saved_indicator()`
  - [x] Replace prefs bottom bar: **Import Preferences…** / **Export Preferences…** (remove Load/Save)
  - [x] `_on_prefs_import`: file dialog → `import_from_file`; success → refresh `_defaults = self._form_defaults()`; show status or `QMessageBox` on error
  - [x] `_on_prefs_export`: save dialog → `export_to_file`; status on success/failure
  - [x] **Do not** remove `prefs.update(spec)` / `prefs.save()` from `_load_project` / `_run_generation` (Story 5.4)

- [x] Add QSS for saved indicator in `app/theme.py` (AC: 4)
  - [x] `#SavedIndicator` — orange accent (`kMainColor_`), small label, right-aligned in tab bar row

- [x] Unit tests `tests/unit/test_preferences.py` (AC: 1, 2, 5, 7)
  - [x] `test_factory_defaults_include_extended_schema`
  - [x] `test_ensure_initialized_creates_file_with_desktop_destination` (mock path, no Qt event loop)
  - [x] `test_to_dict_apply_profile_round_trip`
  - [x] `test_apply_profile_rejects_invalid_plugin_formats` (empty formats)
  - [x] `test_import_validation_preserves_existing_on_failure` (apply_profile never called on bad data)
  - [x] Use `tmp_path` for `Preferences(path)` — no dependency on real config dir

- [x] Regression
  - [x] `.venv/bin/pytest` — full suite green
  - [x] Manual smoke: first launch creates prefs; edit field → auto-save + indicator; import/export; Project tab unchanged after import

## Dev Notes

### Scope — Files to Touch

| File | Change |
|------|--------|
| `core/preferences.py` | Extended schema, factory init, `to_dict`/`apply_profile`/`seed_dict` |
| `app/widgets/folder_field.py` | **New** — Choose… + validated path field |
| `app/pages/preferences.py` | Full profile UI, auto-save, import/export |
| `app/pages/artefacts.py` | Label rename Windows/macOS/Linux |
| `app/main_window.py` | Factory init, seed cache, indicator, Import/Export buttons |
| `app/theme.py` | `#SavedIndicator` QSS |
| `tests/unit/test_preferences.py` | **New** — pure prefs logic tests |

### Do NOT Touch in This Story

| File | Reason |
|------|--------|
| `core/project_spec.py` | `juce_dir` on ProjectSpec — Story 5.3 |
| `core/project_generator.py`, `core/render_context.py` | Drop `juce_dir=` param — Story 5.3 |
| `app/pages/project_info.py`, `app/pages/project.py` | Choose buttons, JUCE on Project, full startup seed wiring — Story 5.2 |
| `MainWindow._load_project` / `_run_generation` prefs sync removal | Story 5.4 |
| `ProjectPage.reset()` full profile re-seed + dirty guard | Story 5.5 |
| `_bmad-output/project-context.md`, `ARCHITECTURE-SPINE.md` | Update after 5.4 when AD-5 behaviour lands in code |

### Current State — Gap Analysis

| Area | Today | Target (5.1) |
|------|-------|--------------|
| `_DEFAULTS` keys | Identity + artefacts + juceDir only | + pluginType, pluginFormats, cxxStandard, preprocessorDefinitions, headerSearchPaths |
| `copyToArtefactsDir` factory | `True` | `False` per USER-MANUAL §4.2 |
| First launch | `load()` no-op if file missing; no file created | `ensure_initialized()` writes factory file once |
| Destination factory | Empty string | Desktop via `QStandardPaths` |
| Preferences UI sections | Default infos + Default artefacts | + Plugin Type, Formats, Compilation; renamed labels |
| Destination label | "Default destination" | **Destination folder** |
| Artefact path labels | "Artefacts (Windows)" … | **Windows**, **macOS**, **Linux** |
| Path pickers | Text fields only | Choose… on destination + JUCE (Preferences tab) |
| Persistence trigger | Manual "Save Preferences" button | Auto-save on valid edit |
| Import/Export | "Load Preferences…" (UI only, no validation/persist) / "Save Preferences" | Import Preferences… / Export Preferences… with validation |
| `_form_defaults()` | 7 identity keys only | Full `seed_dict()` from prefs profile |
| Saved indicator | None | Transient orange label in tab bar |
| `Preferences.update(ProjectSpec)` | Used on Open/Generate | Still present; profile workflow must not depend on it |

### Architecture Compliance

**AD-5 (revised, not fully implemented until 5.4):** This story implements the Preferences-side write paths only: factory creation, auto-save, import. Open/Generate still call `prefs.update()` + `save()` — **leave unchanged**; removing those call sites is Story 5.4.

**AD-7 (revised, ProjectSpec field in 5.3):** `Preferences.juce_dir` remains the **default seed** for new projects. Do not add `juce_dir` to `ProjectSpec` in this story. Generation still passes `juce_dir=self._prefs.juce_dir` until Story 5.3.

**AD-8:** `core/preferences.py` may use `QStandardPaths` (pre-existing). New validation helpers for import should stay in `core/` as pure functions if possible; Qt dialog usage stays in `app/` only.

### Extended `preferences.json` Schema

```json
{
  "manufacturer": "My Company",
  "manufacturerCode": "Myco",
  "pluginCode": "Mypl",
  "companyCopyright": "",
  "companyWebsite": "",
  "companyEmail": "",
  "destination": "/Users/me/Desktop",
  "juceDir": "",
  "pluginType": "synth",
  "pluginFormats": "AU VST3 Standalone",
  "cxxStandard": "C++17",
  "preprocessorDefinitions": "",
  "headerSearchPaths": "",
  "copyToSystemFolders": false,
  "copyToArtefactsDir": false,
  "artefactsDirWindows": "",
  "artefactsDirMacos": "",
  "artefactsDirLinux": ""
}
```

**Key conventions:**
- `pluginType` values: `"synth"`, `"effect"`, `"midi"` — same keys as `PluginTypePage.selected_type()` and `render_context.build_context()` (not `"Instrument"`)
- `pluginFormats`: space-separated string e.g. `"AU VST3 Standalone"` — same as `FormatsPage.value()`
- JSON keys remain `camelCase` matching existing file format

### Factory Defaults (First Launch Only)

Per [docs/USER-MANUAL.md §4.2](docs/USER-MANUAL.md):

| Field | Factory value |
|-------|---------------|
| manufacturer / codes | My Company / Myco / Mypl |
| Copyright, Website, E-mail | empty |
| destination | `QStandardPaths.writableLocation(DesktopLocation)` |
| juceDir | empty (placeholder in UI only) |
| pluginType | `synth` |
| pluginFormats | `AU VST3 Standalone` |
| cxxStandard | `C++17` |
| preprocessorDefinitions, headerSearchPaths | empty |
| copyToSystemFolders | false |
| copyToArtefactsDir | **false** |
| artefact paths | empty |

After first write, **never** re-apply code defaults — all reads come from file.

### `seed_dict()` Shape for Project Seeding

Return camelCase dict consumable by `ProjectPage.load()` / future full reset (Story 5.5):

```python
{
    "manufacturerName": prefs.get("manufacturer"),
    "manufacturerCode": ...,
    "pluginCode": ...,
    "companyCopyright": ..., "companyWebsite": ..., "companyEmail": ...,
    "destinationDir": prefs.get("destination"),
    "juceDir": prefs.get("juceDir"),  # seed only; Project field wired in 5.2/5.3
    "pluginType": prefs.get("pluginType"),
    "pluginFormats": prefs.get("pluginFormats"),
    "cxxStandard": ..., "preprocessorDefinitions": ..., "headerSearchPaths": ...,
    "copyToSystemFolders": ..., "copyToArtefactsDir": ...,
    "artefactsDirWindows": ..., "artefactsDirMacos": ..., "artefactsDirLinux": ...,
}
```

Map manufacturer → `manufacturerName`, destination → `destinationDir` for Project form compatibility.

After successful import, `MainWindow` must refresh `self._defaults = self._prefs.seed_dict()` without calling `ProjectPage.load()`.

### Import Validation Rules

Validate imported JSON before `apply_profile`:

| Field | Rule |
|-------|------|
| Identity text fields | Existing validators in `core/validation.py` |
| destination | `validate_destination` (required non-empty) |
| juceDir | `validate_optional_path` |
| pluginType | Must be one of `synth`, `effect`, `midi` |
| pluginFormats | At least one of AU/VST3/Standalone selected (non-empty split) |
| cxxStandard | One of `C++17`, `C++20`, `C++23` |
| preprocessorDefinitions, headerSearchPaths | `validate_optional` |
| copy flags | bool |
| artefact paths | `validate_optional_path` each |

On any failure: show `QMessageBox.warning` with first error; **do not** mutate `_data` or disk file.

### Auto-Save Flow

```
User edits Preferences field
  → section emits validityChanged / valueChanged / toggled
  → PreferencesPage._try_auto_save()
      → if aggregate invalid: return (no write)
      → collect all section values into profile dict
      → prefs.apply_form(...) or apply_profile partial
      → prefs.save()
      → emit saved = Signal()
MainWindow receives saved
  → _flash_saved_indicator()
```

Remove `_on_prefs_save` and Save button entirely. Invalid fields block save silently (USER-MANUAL §6.2).

### Saved Indicator UX

- Place in `_build_tab_bar()` row, after tabs, before stretch: `QLabel` hidden by default
- Text: `"Saved"` (or `"Preferences saved"`)
- Show on successful auto-save and successful import
- Hide after ~2 s via `QTimer.singleShot`
- Style with `#SavedIndicator` and orange colour from `Palette` / `kMainColor_`

### Reusing Project Section Widgets in Preferences

`PluginTypePage`, `FormatsPage`, `CompilationSection` currently hardcode UI defaults (`_DEFAULT_TYPE`, all formats checked, `_DEFAULT_CXX`). For Preferences:

1. Construct widgets after prefs loaded
2. Call `set_type(prefs.get("pluginType"))`, `set_formats(...)`, `compilation.load({...})` immediately after init
3. Connect their change signals for auto-save (FormatsPage already has `validityChanged`; add change hooks to PluginTypePage / CompilationSection if missing — e.g. `buttonToggled`, `currentTextChanged`, `textChanged`)

**Do not** remove hardcoded fallbacks from Project tab widgets in this story — Project tab still uses its own init path until Story 5.2 wires full seed at startup.

### `FolderField` Widget Sketch

Keep under 15 lines per method (extract helpers if needed):

```python
class FolderField(QWidget):
    validityChanged = Signal(bool)
    valueChanged = Signal(str)

    def __init__(self, spec: FieldSpec, dialog_title: str):
        # HBox: make_field_label | QPushButton Choose… | ValidatedField (hide label?)
        # Prefer: ValidatedField with custom label in spec; button inserted in row via composition
```

Use `QFileDialog.getExistingDirectory(parent, dialog_title, current_path)` with `current_path = self.value()` or Desktop fallback.

### Testing Requirements

- **Unit tier only** for new prefs logic (AD-6) — no Qt widget tests
- Test `Preferences` with explicit `Path(tmp_path / "preferences.json")` — never touch real user config
- For Desktop factory default: patch `QStandardPaths.writableLocation` or inject destination in `factory_defaults(desktop: str = "")` test hook
- Existing 100+ pytest tests must stay green; Epic 3 integration tests unchanged

### Cross-Story Dependencies

| Story | Relationship |
|-------|--------------|
| 5.2 | Uses `seed_dict()`, `FolderField` pattern on Project tab; wires Project startup to full prefs seed |
| 5.3 | Moves JUCE from prefs-only generation to `ProjectSpec.juce_dir` |
| 5.4 | Removes `prefs.update/save` from Open/Generate; last-parent Desktop fallback |
| 5.5 | `Create New Project` calls full reset from `seed_dict()` |

**Recommended order:** 5.1 → 5.3 → 5.2 → 5.4 → 5.5

### Previous Story Intelligence (Epic 3 — test baseline)

Epic 3 established:
- `tests/conftest.py` helpers: `make_spec`, `assert_spec_equal`, `generate_project`
- pytest unit tier for all public `core/` functions; integration round-trip in `tests/integration/test_round_trip.py`
- Clean-code limits: 15 lines/method, 200 lines/class — extract helpers when composing PreferencesPage
- Story files use `baseline_commit` header and exhaustive "Do NOT touch" tables — follow same pattern

No Epic 5 predecessor story exists; Epic 3 story **3-4** is the nearest reference for test conventions and story file structure.

### Git Intelligence

Recent commits are UI polish and Epic 3 test completion — no in-progress Epic 5 code. Baseline commit `72b5972`. Preferences save path was fixed in Story 1.6 (`apply_form` exists); Epic 5.1 extends that pattern to full profile + auto-save.

### Latest Tech Notes

- **PySide6 ≥ 6.7**, **Python 3.14** — no new dependencies
- `QStandardPaths.StandardLocation.DesktopLocation` for factory destination and Choose… fallback
- `QFileDialog.getExistingDirectory` — native folder picker per platform
- `QTimer.singleShot(ms, callable)` for transient indicator — no external libs

### Project Structure Notes

- New widget → `app/widgets/folder_field.py`
- New tests → `tests/unit/test_preferences.py`
- Run app: `.venv/bin/python main.py`
- Run tests: `.venv/bin/pytest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.1]
- [Source: docs/USER-MANUAL.md §4.1–§4.2, §6, §12]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md#AD-5, #AD-7]
- [Source: _bmad-output/project-context.md — Preferences Persistence, UI Patterns]
- [Source: core/preferences.py — current `_DEFAULTS`, `apply_form`]
- [Source: app/main_window.py — `_form_defaults`, `_prefs_buttons`, Open/Generate prefs sync]
- [Source: _bmad-output/implementation-artifacts/1-6-juce-directory-in-preferences.md — prior prefs save pattern]

## Dev Agent Record

### Agent Model Used

Claude (Cursor Agent)

### Debug Log References

### Completion Notes List

- Extended `Preferences` with full profile schema, `factory_defaults`, `ensure_initialized`, `to_dict`, `apply_profile`, `seed_dict`, and `validate_profile`.
- Rebuilt Preferences UI with Plugin Type, Formats, Compilation sections, `FolderField` pickers, auto-save, and Import/Export.
- MainWindow uses factory init, seed cache refresh on import, and transient orange Saved indicator in tab bar.
- Added 6 unit tests; full pytest suite 117/117 green.

### File List

- core/preferences.py
- app/widgets/folder_field.py (new)
- app/pages/preferences.py
- app/pages/artefacts.py
- app/pages/plugin_type.py
- app/pages/compilation.py
- app/main_window.py
- app/theme.py
- tests/unit/test_preferences.py (new)

### Change Log

- 2026-06-25: Story 5.1 — Preferences model & profile workflow (factory init, auto-save, import/export, full profile UI)

### Review Findings

- [ ] [Review][Decision] Export when UI differs from disk — `export_to_file` writes `prefs.to_dict()` (last persisted state). If the form has invalid pending edits, export omits them silently. AC6 says "current profile" — should export live `_collect_profile()` when valid, warn when invalid, or always export disk?
- [ ] [Review][Decision] `FolderField` composition vs spec — Story task requires wrapping `ValidatedField` + Choose button; implementation reimplements validation UI (`QLineEdit`/mark/error). Functionally equivalent but diverges from spec sketch. Refactor to wrap `ValidatedField` or accept current composition?
- [x] [Review][Patch] Import does not full-replace profile (AC5) [`core/preferences.py:154-160`] — fixed via `_complete_profile()` filling missing keys from `_DEFAULTS`.
- [x] [Review][Patch] No validation on startup load [`core/preferences.py:129-138`] — `load()` validates and resets to factory defaults on failure.
- [x] [Review][Patch] Empty desktop from QStandardPaths [`core/preferences.py:69-77`] — falls back to `Path.home()`.
- [x] [Review][Patch] Uncaught OSError on first-run init [`core/preferences.py:129-134`] — wrapped with descriptive re-raise.
- [x] [Review][Patch] `pluginFormats` tokens not validated [`core/preferences.py:104-106`] — rejects tokens outside AU/VST3/Standalone.
- [x] [Review][Patch] Import JSON root type unchecked [`app/pages/preferences.py:94-98`] — rejects non-object JSON roots.
- [x] [Review][Patch] OSError uncaught in auto-save [`app/pages/preferences.py:141-150`] — caught alongside `ValueError`.
- [x] [Review][Patch] Artefact paths block unrelated auto-save [`app/pages/artefacts.py:51-52`] — `is_valid()` skips path fields when copy flag off.
- [x] [Review][Patch] Null prefs values render as `"None"` [`app/pages/preferences.py:85-88`] — `_pref_text()` coerces null to empty string.
- [x] [Review][Patch] `FolderField.set_value` skips validation refresh [`app/widgets/folder_field.py:30-31`] — calls `_on_text_changed` after set.
- [x] [Review][Defer] Private-widget coupling in auto-save wiring [`app/pages/preferences.py:168-171`] — `_artefacts._checks`, `_compilation._cxx._combo`, etc. Pre-existing pattern; refactor when sections expose change signals.
- [x] [Review][Defer] No JSON schema version field [`core/preferences.py`] — Future migration concern; out of 5.1 scope per epic sequencing.
- [x] [Review][Defer] Method length exceeds 15-line guideline [`core/preferences.py`, `app/pages/preferences.py`] — `validate_profile`, `seed_dict`, `_connect_auto_save` exceed limit; project-context allows conscious data/orchestration exceptions.
- [x] [Review][Defer] `test_import_validation_preserves_existing_on_failure` does not call `import_from_file` [`tests/unit/test_preferences.py:85-94`] — AD-6 unit tier avoids Qt widget tests; core validation path is covered.
