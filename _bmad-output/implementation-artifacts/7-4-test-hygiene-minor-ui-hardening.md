---
baseline_commit: 3299833
---

# Story 7.4: Test Hygiene & Minor UI Hardening

Status: done

<!-- Epic 7 — Release Hardening. Priority: NICE / defer. Order: last (after 7.1–7.3). Ultimate context engine analysis completed - comprehensive developer guide created. -->

## Story

As a contributor and daily user,
I want redundant legacy tests removed and minor UI rough edges polished,
So that the test suite stays maintainable and small UX gaps do not distract during manual QA.

## Acceptance Criteria

1. **Given** `tests/test_story_1_2.py`, `tests/test_story_2_1.py`, `tests/test_story_2_2.py`, **when** Epic 7.4 runs, **then** their coverage is merged into canonical `tests/unit/` or `tests/integration/` modules — no duplicate test classes remain; the three legacy files are deleted.
2. **Given** the Templates tab after **Load from file…**, **when** a file loads successfully, **then** the editor state label reflects the loaded external source (not override/default text); invalid file types are rejected with a clear message; unreadable files show an error instead of failing silently.
3. **Given** `null` JSON values in imported or loaded preferences for path (or string) fields, **when** the Preferences or Project UI renders, **then** fields show empty string — not the literal `"None"`.
4. **Given** Import Preferences with a profile that triggers a `ValueError` or `OSError` during apply/save, **when** import fails, **then** rollback restores the previous in-memory profile **and** the Preferences UI widgets match the restored profile.

**Optional (skip without blocking Epic 7 done):**

- Parametrize integration round-trip across all three `plugin_type` values (`instrument`, `audio-effect`, `midi-effect`).
- PyInstaller bundle smoke tests (timeout, encoding, `_internal` layout) — follow existing skip patterns in `test_frozen_bundle.py`.
- Preferences widget coupling refactor (internal attribute access).

## Tasks / Subtasks

- [x] Audit and migrate legacy tests (AC: 1)
  - [x] Build overlap matrix (see Dev Notes) — do **not** delete until unique cases are ported
  - [x] Create `tests/unit/test_project_writer.py` for writer-only cases
  - [x] Add any missing reader cases to `tests/unit/test_project_reader.py`
  - [x] Optionally add `tests/unit/test_core_imports.py` for AD-8 no-Qt guards
  - [x] Delete `tests/test_story_1_2.py`, `tests/test_story_2_1.py`, `tests/test_story_2_2.py`
  - [x] Run full `python3 -m pytest` — count ≥ 233 passed (deduplicated baseline), 2 skipped

- [x] Templates page hardening (AC: 2)
  - [x] Update `app/pages/templates.py` `load_from_file()`
  - [x] Add `_update_loaded_status(path)` distinct from `_update_status(name)` (override/default)
  - [x] Wrap `read_text` in try/except; surface errors via status label (and optionally `MainWindow` status bar if caller wires it — status label alone satisfies AC)
  - [x] Validate extension against selected template (`.h`/`.cpp` for source files; `.gitignore` basename or suffix for gitignore)

- [x] Null display normalization (AC: 3)
  - [x] Fix at display boundary **and** persistence boundary (prefer both for defense in depth)
  - [x] `core/preferences.py`: coerce `None` → `""` for string profile keys in `load()`, `_complete_profile()`, and/or `apply_profile()`
  - [x] `core/paths.py`: treat `null` in `normalize_path_dict_values()` as `""`
  - [x] App layer: replace bare `str(values[key])` with null-safe helper in `ValidatedForm`, `ArtefactsSection.load`, `CompilationSection.load`

- [x] Import rollback completeness (AC: 4)
  - [x] Fix `PreferencesPage.import_from_file()` except path to call `reload_from_prefs()` after `apply_profile(before)`
  - [x] Consider transactional `apply_profile` (validate all fields before mutating `_data`) to prevent partial in-memory state on `ValueError`
  - [x] If `save()` succeeded before a later failure, restore disk via `save()` after rollback (currently unlikely path — document if intentionally out of scope)

- [x] Update `deferred-work.md` — strike Infrastructure + Interface items when done

- [ ] **Optional:** `@pytest.mark.parametrize("plugin_type", [...])` on `tests/integration/test_round_trip.py` regenerate test
- [ ] **Optional:** expand `tests/integration/test_frozen_bundle.py`

### Review Findings

- [x] [Review][Decision] Pytest count gate — Resolved: baseline updated to ≥ 233 passed (deduplicated suite after legacy migration); current run 234 passed, 2 skipped.

- [x] [Review][Decision] Gitignore dotfile validation scope — Resolved: strict `.gitignore` only (basename or suffix); task wording aligned to Dev Notes extension table.

- [x] [Review][Patch] Import rollback omits accentColor [app/pages/preferences.py:129] — Fixed: snapshot `before_accent` and restore via `set_accent_color` on failure; `test_import_rollback_restores_accent_color` added.

- [x] [Review][Patch] Template load failure leaves stale editor content [app/pages/templates.py:84] — Fixed: `_abort_load()` restores effective template content before showing error status.

- [x] [Review][Defer] No automated `PreferencesPage.import_from_file` UI rollback test — AD-6 prohibits Qt widget tests; core rollback covered by `test_import_save_failure_restores_profile`; UI fix verified by manual QA.

- [x] [Review][Defer] Post-`save()` disk revert on import failure — Dev notes document as out of scope; atomic write makes failure-before-save the normal path (Story 7.2).

- [x] [Review][Defer] In-process no-Qt import guard vs subprocess — Story dev notes chose in-process pytest pattern; `test_core_imports.py` matches migration sketch; deferred-work updated accordingly.

- [x] [Review][Defer] MemoryError uncaught on template read [app/pages/templates.py:89] — `read_text` only catches `OSError` and `UnicodeDecodeError`; extremely large file could raise uncaught `MemoryError`.

## Dev Notes

### Epic 7 context

Epic 7 is the post-MVP quality gate before manual QA (week of 2026-07-07). Stories 7.1–7.3 are **done**. This story closes remaining **NICE** items from `deferred-work.md`: legacy test files, Templates editor polish, prefs `null` display, import rollback.

| Story | Scope | Status |
|-------|-------|--------|
| 7.1 | GitHub Actions pytest CI | **done** |
| 7.2 | Atomic prefs + app_state JSON | **done** |
| 7.3 | Generation/reload edge cases | **done** |
| **7.4** | Test hygiene + minor UI hardening | **this story** |

**Time-box (PO):** If schedule is tight before manual QA, **minimum deliverable** = merge/delete `test_story_*.py` (AC1). UI polish (AC2–4) is skippable without blocking Epic 7 closure.

### Legacy test migration matrix

**Baseline:** 242 passed, 2 skipped after Story 7.3 (`7-3-core-generation-reload-robustness.md`).

| Legacy test (unittest) | Canonical home | Action |
|------------------------|----------------|--------|
| `TestRenderContextAcceptsSpec` | `tests/unit/test_render_context.py` | **Drop** — superseded by parametrized context tests |
| `TestProjectGeneratorAcceptsSpec.test_generate_signature` | `tests/unit/test_project_generator.py` (new) or drop | **Optional** — weak signature smoke; drop unless team wants AD-1 guard |
| `TestProjectWriterAtomicWrite.test_write_creates_sidecar` | `tests/integration/test_round_trip.py::test_writer_output_contains_required_files` | **Drop** |
| `test_write_no_tmp_dir_leftover_on_success` | new `test_project_writer.py` | **Port** |
| `test_write_atomic_cleans_tmp_on_failure` | new `test_project_writer.py` | **Port** |
| `test_write_rename_failure_propagates_after_rmtree` | new `test_project_writer.py` | **Port** — only home for rename-failure mock |
| `TestProjectReaderReturnsSpec` | `test_round_trip.py` + `test_project_reader.py` | **Drop** |
| `TestNoQtImport` (×3 modules) | new `test_core_imports.py` | **Port** — preserves AD-8 guard; use pytest + `sys.modules` snapshot |
| `test_read_sidecar_returns_all_fields` | `test_round_trip.py::test_regenerate_produces_identical_tree` + `assert_spec_equal` | **Drop** |
| `test_malformed_sidecar_returns_none_no_cmake_fallback` | `test_project_reader.py::test_malformed_json_returns_error` | **Drop** — 7.3 uses `read_project_result` + `error` (stronger) |
| `test_sidecar_non_dict_returns_none` | `test_project_reader.py` | **Port** — payloads `'"hello"'`, `'[]'` not yet covered |
| `test_round_trip_empty_diff` | `test_regenerate_produces_identical_tree` | **Drop** |
| `test_cmake_fallback_without_sidecar` | `test_cmake_fallback_returns_complete_spec` | **Drop** |
| `test_cmake_fallback_round_trip` | `test_cmake_fallback_regenerate_identical_tree` | **Drop** |
| `test_partial_cmake_returns_none_with_missing_fields` | same name in `test_round_trip.py` | **Drop** |
| `test_no_cmakelists_returns_none` | same name in `test_round_trip.py` | **Drop** |
| `test_legacy_project_configuration_cmake` | `test_legacy_project_configuration_cmake_compat` + `conftest.install_legacy_project_configuration_cmake` | **Drop** |

**Use shared fixtures** from `tests/conftest.py`: `make_spec`, `write_project`, `generate_project`, `all_files`, `assert_spec_equal`, `assert_trees_equal`. Do **not** copy `_make_spec` helpers from legacy files.

**New file sketch — `tests/unit/test_project_writer.py`:**

```python
def test_write_leaves_no_tmp_dir_on_success(tmp_path):
    dest, spec = write_project(tmp_path, make_spec(tmp_path))
    assert not (dest.parent / (dest.name + ".tmp")).exists()

def test_write_cleans_tmp_on_failure(tmp_path):
    # ProjectWriter(Path("/nonexistent"), dest) → no dest, no .tmp

def test_write_rename_failure_propagates(tmp_path):
    # patch Path.rename after first successful write; second write raises OSError
```

**New file sketch — `test_core_imports.py`:**

```python
@pytest.mark.parametrize("module", [
    "core.project_generator",
    "core.project_writer",
    "core.project_reader",
])
def test_core_module_import_does_not_load_qt(module):
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    importlib.import_module(module)
    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
```

After migration, `pytest` must not collect anything under `tests/test_story_*.py`.

### Templates page — current gaps

File: `app/pages/templates.py` (not `templates_page.py`).

```79:88:app/pages/templates.py
    def load_from_file(self) -> None:
        name = self._selector.currentText()
        if name == templates_store.GITIGNORE_FILE:
            path = self._pick_gitignore_file()
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Load template file", "", "C++ source (*.h *.cpp);;All files (*)"
            )
        if path:
            self._editor.setPlainText(Path(path).read_text(encoding="utf-8"))
```

**Problems:**

1. **No status update after external load** — `_update_status(name)` only runs on combo change / save / reset. After Load File, label still shows "Override active" or "Showing the built-in default" even though editor holds unsaved external content.
2. **No error handling** — `read_text` raises `OSError` / `UnicodeDecodeError` uncaught.
3. **Weak type validation** — dialog filter is suggestive only; user can pick "All files" and load a binary. Reject extensions not matching template kind.

**Recommended fix:**

```python
def load_from_file(self) -> None:
    name = self._selector.currentText()
    path = self._pick_file_for_template(name)
    if not path:
        return
    if not self._is_valid_template_file(name, path):
        self._status.setText("Invalid file type for the selected template.")
        return
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        self._status.setText(f"Could not read file: {error}")
        return
    self._editor.setPlainText(content)
    self._status.setText(f"Loaded from {Path(path).name} — not saved until you click Save override.")
```

Extension rules:

| Selected template | Accept |
|-------------------|--------|
| `*.h` / `*.cpp` | suffix `.h` or `.cpp` (case-insensitive) |
| `.gitignore` | basename `.gitignore` OR suffix `.gitignore` |

Do **not** persist override on Load File (existing UX per Story 1.7 / user manual).

### Null → `"None"` display bug

**Root cause chain:**

1. JSON `null` loads into `Preferences._data` as Python `None` via `load()` → `self._data.update(raw)`.
2. `_complete_profile()` uses `data.get(key, default)` — key **present** with `null` keeps `None`.
3. UI reload uses `str(None)` in several places → literal `"None"` in QLineEdit.

**Affected code (must fix):**

```25:28:app/widgets/validated_form.py
    def set_values(self, values: dict) -> None:
        for key, field in self._fields.items():
            if key in values:
                field.set_value(str(values[key]))
```

```67:73:app/pages/artefacts.py
    def load(self, values: dict) -> None:
        ...
                field.set_value(str(values[key]))
```

```42:45:app/pages/compilation.py
    def load(self, values: dict) -> None:
        self._cxx.set_value(values.get("cxxStandard", _DEFAULT_CXX))
        self._defs.set_value(values.get("preprocessorDefinitions", ""))
        self._headers.set_value(values.get("headerSearchPaths", ""))
```

Note: `values.get("cxxStandard", _DEFAULT_CXX)` returns `None` when key exists with `null` — `.get` default is ignored.

**Already correct:**

```57:59:app/pages/preferences.py
def _pref_text(prefs: Preferences, key: str) -> str:
    value = prefs.get(key)
    return "" if value is None else str(value)
```

```48:52:app/pages/project_info.py
def _default_path(defaults: dict, primary: str, legacy: str = "") -> str:
    value = defaults.get(primary, "")
    ...
    return value or ""  # None is falsy → ""
```

**Recommended approach (minimal, layered):**

1. Add `core/display.py` or reuse pattern in `core/paths.py`:

```python
def display_str(value) -> str:
    return "" if value is None else str(value)
```

2. Use in all app `load`/`set_values` paths listed above.
3. In `core/preferences.py`, normalize on ingest:

```python
def _normalize_null_strings(data: dict) -> dict:
    return {k: ("" if v is None else v) for k, v in data.items()}
```

Apply in `load()` after parsing JSON and in `_complete_profile()`.

4. Extend `normalize_path_dict_values()`:

```python
if key in out:
    if out[key] is None:
        out[key] = ""
    elif out[key]:
        out[key] = normalize_portable_path(str(out[key]))
```

**Unit test (no Qt):** `tests/unit/test_preferences.py` — load JSON with `"juceDir": null`, `"artefactsDirWindows": null`; assert `prefs.get("juceDir") == ""` and `to_dict()` returns empty strings.

**Manual QA:** Import profile JSON with null path fields; Preferences + Project artefact path fields must be blank.

### Import rollback bug

```119:138:app/pages/preferences.py
    def import_from_file(self, path: str) -> tuple[bool, str]:
        ...
        before = self._prefs.to_dict()
        try:
            self._prefs.apply_profile(data)
            self._prefs.save()
            self.reload_from_prefs()
            self.saved.emit()
            return True, ""
        except (ValueError, OSError) as error:
            self._prefs.apply_profile(before)
            return False, str(error)
```

**Bug:** except block restores `_prefs` memory but **does not** call `reload_from_prefs()`. Widgets keep showing the failed import values while `_prefs` holds the old profile — violates AC4.

**Fix:**

```python
except (ValueError, OSError) as error:
    self._prefs.apply_profile(before)
    self.reload_from_prefs()
    return False, str(error)
```

**Secondary hardening — transactional `apply_profile`:**

```235:246:core/preferences.py
    def apply_profile(self, data: dict) -> None:
        profile = _complete_profile(normalize_path_dict_values(data))
        ok, message = validate_profile(profile)
        if not ok:
            raise ValueError(message)
        for key in _PROFILE_KEYS:
            self._data[key] = profile[key]
        if "accentColor" in data:
            ok, message = validate_accent_color(data["accentColor"])
            if not ok:
                raise ValueError(message)
            self.set_accent_color(data["accentColor"])
```

Accent validation runs **after** mutating `_data`. `import_from_file` pre-validates with `validate_profile(data)` so this path is mostly safe today, but `apply_form()` and future callers may hit partial state. Refactor to validate accent **before** the assignment loop, or snapshot/restore `_data` inside `apply_profile`.

**Test (no Qt):** In `tests/unit/test_preferences.py`, simulate failure by patching `save` to raise `OSError` after `apply_profile` would succeed; assert `to_dict()` matches `before` after import handler rollback. For UI rollback, manual QA suffices (AD-6).

### Architecture compliance

| AD | Requirement | This story |
|----|-------------|------------|
| AD-6 | pytest two tiers; no Qt widget tests | Port legacy tests to pytest; no `MainWindow` widget tests |
| AD-8 | `core/` never imports `app/` | New tests import `core/` only; import guard tests stay in unit tier |
| AD-10 | Atomic JSON persistence | Out of scope — do not change `json_files.py` unless rollback fix requires reverting disk (unlikely) |

**Explicitly out of scope:**

- Qt widget tests for Templates or Preferences pages
- Preferences widget coupling refactor (optional defer)
- Full JSON Schema for preferences
- CI workflow changes (7.1 done)

### File structure requirements

| File | Action |
|------|--------|
| `tests/test_story_1_2.py` | **DELETE** after migration |
| `tests/test_story_2_1.py` | **DELETE** after migration |
| `tests/test_story_2_2.py` | **DELETE** after migration |
| `tests/unit/test_project_writer.py` | **NEW** — atomic write + rename failure |
| `tests/unit/test_project_reader.py` | **UPDATE** — add non-dict sidecar cases |
| `tests/unit/test_core_imports.py` | **NEW** (optional) — AD-8 import guards |
| `tests/integration/test_round_trip.py` | **UPDATE** (optional) — plugin_type parametrization |
| `tests/integration/test_frozen_bundle.py` | **UPDATE** (optional) — smoke expansion |
| `tests/unit/test_preferences.py` | **UPDATE** — null coercion + import rollback |
| `app/pages/templates.py` | **UPDATE** — Load File UX |
| `app/pages/preferences.py` | **UPDATE** — import rollback UI refresh |
| `app/widgets/validated_form.py` | **UPDATE** — null-safe display |
| `app/pages/artefacts.py` | **UPDATE** — null-safe display |
| `app/pages/compilation.py` | **UPDATE** — null-safe display |
| `core/preferences.py` | **UPDATE** — null normalization; transactional apply_profile |
| `core/paths.py` | **UPDATE** — null in path dict normalization |
| `core/display.py` | **NEW** — `display_str` helper |
| `_bmad-output/implementation-artifacts/deferred-work.md` | **UPDATE** — strike completed items |

**Do not modify:** generation pipeline (`render_context`, `project_reader` logic beyond tests), CI workflow, CMake templates.

### Testing requirements

**Must pass before story done:**

```bash
.venv/bin/pytest
```

Expected: ≥ 233 passed, 2 skipped (deduplicated baseline after legacy migration; same or higher after porting unique cases).

**CI:** Ubuntu runner has no Qt display — all new tests must be pure `core/` or integration with `tmp_path` only.

**Regression guards after deleting legacy files:**

- `tests/integration/test_round_trip.py` — full round-trip suite stays green
- `tests/unit/test_project_reader.py` — sidecar validation from 7.3 untouched
- `tests/unit/test_preferences.py` — existing atomic save / corrupt load tests stay green

### Previous story intelligence

**From 7.3 (`7-3-core-generation-reload-robustness.md`):**

- `tests/unit/test_project_reader.py` is the canonical sidecar test module — extend, do not duplicate 7.3 cases
- `tests/test_story_1_2.py` gained `test_write_rename_failure_propagates_after_rmtree` during 7.3 — **must port** before deleting file
- `tests/conftest.py` already has `write_project`, `install_legacy_project_configuration_cmake` — legacy `test_story_2_2` helpers are redundant
- Full suite baseline: **242 passed, 2 skipped**
- Review pattern: address `[Review][Patch]` before close; optional `[Review][Defer]` items stay in `deferred-work.md`

**From 7.2 (`7-2-atomic-json-persistence-corrupt-file-feedback.md`):**

- `Preferences.save()` uses `atomic_write_text` — import rollback rarely needs disk revert if failure happens before `save()`
- `load_warning` pattern for corrupt files — separate from null display (null is valid JSON, not corrupt)

**From 7.1 (`7-1-github-actions-ci-for-pytest.md`):**

- CI collects `tests/unit/` and `tests/integration/` only — deleting `test_story_*.py` removes unittest-style duplicates from CI collection
- Story 7.1 noted: "`tests/test_story_*.py` still collected until Story 7.4" — this story completes that cleanup

**From Epic 3 / integration suite:**

- `tests/integration/test_round_trip.py` already covers CMake fallback, partial CMake, legacy `project-configuration.cmake`, template overrides, `juce_dir` — do not re-copy from `test_story_2_2.py`

### Git intelligence

Recent commits on `main`:

```
3299833 Harden generation and reload edge cases for Story 7.3.
782ca0c Add atomic JSON persistence and corrupt-file feedback for Story 7.2.
02dd1af Add Epic 7 release hardening stories and sprint change proposal.
```

7.3 touched `tests/test_story_1_2.py` (rename failure) and `tests/test_story_2_2.py` — both are migration sources, not long-term homes. Uncommitted workspace may contain additional test edits — re-run pytest on current tree before and after migration.

### Latest technical information

- **pytest + unittest coexistence:** Legacy files use `unittest.TestCase`; canonical suite uses pytest. Port to pytest functions for consistency with `conftest.py` fixtures.
- **PySide6 file dialogs:** `QFileDialog.getOpenFileName` filter is not enforcement — always validate suffix in code.
- **Python 3.14 / cp310-abi3:** No new dependencies.
- **Optional parametrization:** `PLUGIN_TYPES` keys in `core/plugin_settings.py` — use all three for round-trip regenerate test.

### Project context reference

From `_bmad-output/project-context.md`:

- Function ≤ 15 lines — extract `_is_valid_template_file`, `_pick_file_for_template`, `display_str` rather than bloating methods
- No type annotations beyond existing project style
- No comments referencing story numbers
- Git commits: English only
- AD-6: no Qt widget tests — test null coercion and `apply_profile` in `core/` unit tests; UI fixes validated manually during QA week
- Template Load File does not persist until Save override (user manual §8)

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 7, Story 7.4]
- [Source: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-06-28.md` § Story 7.4]
- [Source: `_bmad-output/implementation-artifacts/deferred-work.md` — Infrastructure, Interface, Tests sections]
- [Source: `_bmad-output/implementation-artifacts/7-3-core-generation-reload-robustness.md`]
- [Source: `_bmad-output/implementation-artifacts/7-1-github-actions-ci-for-pytest.md` — legacy test note]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` — AD-6, AD-8]
- [Source: `app/pages/templates.py` — Load File]
- [Source: `app/pages/preferences.py` — import_from_file]
- [Source: `tests/conftest.py` — shared fixtures]
- [Source: `tests/integration/test_round_trip.py` — canonical integration coverage]

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-sonnet-medium-thinking

### Debug Log References

- pytest via `python3 -m pytest`: 234 passed, 2 skipped (deduplicated baseline ≥ 233 after legacy migration; +1 accent rollback test from code review)
- `.venv/bin/pytest` shebang points to stale path; use `python3 -m pytest`

### Completion Notes List

- Migrated unique legacy tests to `test_project_writer.py`, `test_project_reader.py` (non-dict sidecar), and `test_core_imports.py`; deleted all three `test_story_*.py` files
- Hardened Templates Load File: extension validation, read error handling, distinct loaded-from status label
- Added `core/display.py` with `display_str`; normalized null strings in `preferences.py` and `paths.py`; updated ValidatedForm, ArtefactsSection, CompilationSection
- Fixed import rollback: `reload_from_prefs()` on failure; transactional `apply_profile` validates accent before mutating `_data`
- Disk revert on import failure intentionally out of scope — failure occurs before `save()` in normal path (Story 7.2 atomic write)
- Struck completed items in `deferred-work.md` (Infrastructure, Interface, no-Qt guard)

### File List

- `tests/unit/test_project_writer.py` (new)
- `tests/unit/test_core_imports.py` (new)
- `tests/unit/test_project_reader.py` (modified)
- `tests/unit/test_preferences.py` (modified)
- `tests/test_story_1_2.py` (deleted)
- `tests/test_story_2_1.py` (deleted)
- `tests/test_story_2_2.py` (deleted)
- `core/display.py` (new)
- `core/preferences.py` (modified)
- `core/paths.py` (modified)
- `app/pages/templates.py` (modified)
- `app/pages/preferences.py` (modified)
- `app/widgets/validated_form.py` (modified)
- `app/pages/artefacts.py` (modified)
- `app/pages/compilation.py` (modified)
- `_bmad-output/implementation-artifacts/deferred-work.md` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)
- `_bmad-output/implementation-artifacts/7-4-test-hygiene-minor-ui-hardening.md` (modified)

### Change Log

- 2026-06-29: Code review — accentColor import rollback, Templates `_abort_load`, pytest gate → 233 baseline
