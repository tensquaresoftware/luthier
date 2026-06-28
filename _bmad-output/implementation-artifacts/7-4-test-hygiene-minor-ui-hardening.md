# Story 7.4: Test Hygiene & Minor UI Hardening

Status: backlog

<!-- Epic 7 — Release Hardening. Priority: NICE / defer. Order: last. -->

## Story

As a contributor and daily user,
I want redundant legacy tests removed and minor UI rough edges polished,
So that the test suite stays maintainable and small UX gaps do not distract during manual QA.

## Acceptance Criteria

1. **Given** `tests/test_story_1_2.py`, `tests/test_story_2_1.py`, `tests/test_story_2_2.py`, **when** Epic 7.4 runs, **then** coverage is merged into canonical pytest modules — no duplicate test classes remain.
2. **Given** Templates tab after **Load from file…**, **when** a file loads, **then** state label reflects source; invalid types rejected; read errors shown.
3. **Given** `null` in imported prefs path fields, **when** UI renders, **then** empty string — not `"None"`.
4. **Given** Import Preferences `ValueError` paths, **when** import fails, **then** full rollback of in-memory profile.

**Optional (skip without blocking Epic 7 done):**

- Parametrize integration round-trip across all `plugin_type` values
- PyInstaller bundle smoke tests (timeout, encoding, `_internal` layout)
- Preferences widget coupling refactor

## Tasks / Subtasks

- [ ] Audit `tests/test_story_*.py` vs canonical suite (AC: 1)
  - [ ] Map cases to `tests/unit/` or `tests/integration/`
  - [ ] Delete legacy files after merge
  - [ ] Confirm pytest count stable or increased

- [ ] Templates page (`app/pages/templates_page.py`) (AC: 2)
  - [ ] Fix Load File state label
  - [ ] Validate file type before load
  - [ ] Handle read errors with user-visible message

- [ ] Prefs null display (AC: 3)
  - [ ] Trace `null` → `"None"` in path fields; normalize on load or display

- [ ] Import rollback (AC: 4)
  - [ ] Audit `PreferencesPage` / import handler for partial state on `ValueError`

- [ ] Optional: plugin_type parametrization in `tests/integration/test_round_trip.py`
- [ ] Optional: expand `tests/integration/test_frozen_bundle.py`
- [ ] Update `deferred-work.md`

## Dev Notes

### Legacy test files

| File | Likely target |
|------|----------------|
| `tests/test_story_1_2.py` | `tests/unit/` (generation, no-Qt) |
| `tests/test_story_2_1.py` | `tests/integration/` (sidecar) |
| `tests/test_story_2_2.py` | `tests/integration/` (CMake fallback) |

Use fixtures from `tests/conftest.py` where possible.

### UI files

- `app/pages/templates_page.py` — Templates editor
- `app/pages/preferences_page.py` — import + null display
- `app/main_window.py` — `_on_prefs_import`

### Out of scope

- Qt widget tests for `MainWindow` (AD-6)
- Preferences widget signal refactor (optional defer)

### Time-box

If schedule is tight before manual QA week: **minimum** = merge `test_story_*.py`; UI polish skippable per PO.
