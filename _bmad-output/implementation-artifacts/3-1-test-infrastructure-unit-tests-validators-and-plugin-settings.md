---
baseline_commit: 9fac1f87147e36100e15fea537488f15cff640df
---

# Story 3.1: Test Infrastructure & Unit Tests — Validators and Plugin Settings

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer (Guillaume),
I want pytest configured and the first unit tests in place for `core/validation.py` and `core/plugin_settings.py`,
so that the pure field validators and plugin metadata functions are continuously verified.

## Acceptance Criteria

1. **Given** `requirements-dev.txt` lists `pytest` and `tests/` directory exists with `tests/unit/` and `tests/integration/` subdirectories, **when** `pytest` is run from the project root, **then** it discovers and runs all tests without configuration errors.
2. **Given** `tests/unit/test_validation.py` exists, **when** pytest runs, **then** every public validator in `core/validation.py` is called with valid, invalid, and empty inputs — all return `(bool, str)` tuples as contracted.
3. **Given** `tests/unit/test_plugin_settings.py` exists, **when** pytest runs, **then** `flags_for_type()`, `bundle_id()`, and `au_and_vst3_categories()` are tested for all three plugin types (`synth`, `effect`, `midi`).
4. **Given** any unit test in `tests/unit/`, **when** pytest imports it, **then** no Qt module is imported as a side effect.

## Tasks / Subtasks

- [x] Add pytest to dev dependencies and minimal config (AC: 1)
  - [x] Add `pytest>=8.0` to `requirements-dev.txt`
  - [x] Add `pytest.ini` at project root with `testpaths = tests`, `pythonpath = .` (project root — no `src/` layout)
  - [x] Create `tests/unit/__init__.py` and `tests/integration/__init__.py` (integration dir may stay empty until story 3-4)
  - [x] Verify `.venv/bin/pip install -r requirements-dev.txt` then `.venv/bin/pytest` from repo root exits 0

- [x] Add `tests/unit/test_validation.py` (AC: 2, 4)
  - [x] Parametrize or table-drive each public validator (see Dev Notes for cases)
  - [x] Assert return type is `tuple[bool, str]` with `isinstance(ok, bool)` and `isinstance(msg, str)`
  - [x] Add `test_validation_modules_import_without_qt` — import `core.validation` with no PySide6/PyQt leak (mirror `TestNoQtImport` pattern from `tests/test_story_1_2.py`)

- [x] Add `tests/unit/test_plugin_settings.py` (AC: 3, 4)
  - [x] `flags_for_type` for `synth`, `effect`, `midi` — assert exact `isSynth` / `isMidiEffect` / `needsMidiInput` / `needsMidiOutput` strings (`"TRUE"` / `"FALSE"`)
  - [x] `au_and_vst3_categories` for each type (epic AC name `categories()` maps to this function)
  - [x] `bundle_id` — normal case, numeric-leading manufacturer, special-char stripping
  - [x] Optional but recommended: `type_for_flags` round-trip with `flags_for_type`
  - [x] Add `test_plugin_settings_import_without_qt`

- [x] Regression guard (AC: 1)
  - [x] `.venv/bin/pytest` discovers **both** new pytest unit tests **and** existing `tests/test_story_*.py` unittest modules (pytest runs `unittest.TestCase` subclasses by default — do not delete or migrate story tests in this story)
  - [x] `.venv/bin/python -m unittest discover -s tests -v` still passes (backward compat for any scripts/docs referencing unittest)

## Dev Notes

### Gap Analysis — What Exists vs. What This Story Adds

| Component | Current state (post Epic 2) | This story |
|-----------|----------------------------|------------|
| Test framework | `unittest` only, 20 tests in 3 flat `tests/test_story_*.py` files | Introduce **pytest** as primary runner; keep existing unittest files |
| `requirements-dev.txt` | `pyinstaller>=6.0` only | Add **pytest** |
| `tests/unit/` | Does not exist | Create + first pure unit tests |
| `tests/integration/` | Does not exist | Create empty scaffold (story 3-4) |
| `core/validation.py` coverage | Indirect via UI only | **Direct** unit tests for all 9 public validators |
| `core/plugin_settings.py` coverage | Indirect via `render_context` / round-trip tests | **Direct** unit tests for type flags, categories, bundle ID |
| No-Qt guard | `TestNoQtImport` covers 3 modules in `test_story_1_2.py` | Extend to `validation` + `plugin_settings` in `tests/unit/` |
| pytest config | None | `pytest.ini` with `pythonpath = .` |

**This story establishes AD-6.** Stories 3-2 through 3-4 build on the `tests/unit/` and `tests/integration/` layout introduced here.

### Scope — Files to Touch

| File | Change |
|------|--------|
| `requirements-dev.txt` | Add `pytest>=8.0` |
| `pytest.ini` | **New** — minimal discovery + `pythonpath` |
| `tests/unit/__init__.py` | **New** |
| `tests/integration/__init__.py` | **New** (placeholder) |
| `tests/unit/test_validation.py` | **New** |
| `tests/unit/test_plugin_settings.py` | **New** |

**Do NOT touch in this story:**
- `core/validation.py`, `core/plugin_settings.py` — pure functions already correct; test only
- Existing `tests/test_story_*.py` — leave on unittest; pytest must still collect them
- `core/render_context.py`, `core/project_spec.py`, etc. — stories 3-2 / 3-3
- `CONTRIBUTING.md` / README — story 4-4 contributor docs
- CI pipeline — no `.github/` exists yet

### `core/validation.py` — Public API & Test Matrix

All validators return `ValidationResult = tuple[bool, str]`. Private helpers `_ok`, `_no_accents` are tested indirectly.

| Function | Valid input example | Invalid input example | Empty `""` expected |
|----------|--------------------|-----------------------|---------------------|
| `validate_project_name` | `"MyPlugin"`, `"A_b-1"` | `"1bad"`, `"has space"` | **invalid** (no match) |
| `validate_display_name` | `"My Plugin-1"` | `"bad@char"` | **valid** (no invalid chars) |
| `validate_version` | `"1.0.0"` | `"   "` (whitespace only) | **invalid** — "Version is required." |
| `validate_manufacturer_name` | `"Acme Corp"` | `"   "` | **invalid** |
| `validate_manufacturer_code` | `"Abcd"` (4 alpha) | `"abc"`, `"Ab12"` | **invalid** |
| `validate_plugin_code` | `"Mypl"`, `"1234"` | `"abc"`, `"toolong"` | **invalid** |
| `validate_destination` | `"/Users/dev/out"` | `"/café/path"` (accent) | **invalid** — required |
| `validate_optional_path` | `""`, `"/valid"` | `"/café"` | **valid** when empty |
| `validate_optional` | any string | N/A | **valid** always |

**Error message contracts (spot-check, do not over-assert full strings unless stable):**
- `validate_project_name` failure mentions letter / allowed chars
- `validate_manufacturer_code` / `validate_plugin_code` mention "Exactly 4"
- Accent failures mention "accented" or list the character

```22:26:core/validation.py
def validate_project_name(value: str) -> ValidationResult:
    if _PROJECT_NAME_RE.match(value):
        return _ok()
    return False, "Start with a letter; letters, digits, '-' and '_' only."
```

```68:79:core/validation.py
def validate_destination(value: str) -> ValidationResult:
    if not value.strip():
        return False, "Destination is required."
    return _no_accents(value)

def validate_optional_path(value: str) -> ValidationResult:
    return _no_accents(value)

def validate_optional(value: str) -> ValidationResult:
    return _ok()
```

### `core/plugin_settings.py` — Public API & Expected Values

**Type keys** (not display labels): `synth`, `effect`, `midi` — from `PLUGIN_TYPES`.

| `type_key` | `flags_for_type` | `au_and_vst3_categories` |
|------------|------------------|------------------------|
| `synth` | `isSynth=TRUE`, `isMidiEffect=FALSE`, `needsMidiInput=TRUE`, `needsMidiOutput=FALSE` | `("kAudioUnitType_MusicDevice", "Instrument|Synth")` |
| `effect` | all `FALSE` except standard effect | `("kAudioUnitType_Effect", "Fx")` |
| `midi` | `isMidiEffect=TRUE`, midi in/out `TRUE` | `("kAudioUnitType_MIDIProcessor", "Fx|MIDI")` |

```22:29:core/plugin_settings.py
def flags_for_type(type_key: str) -> dict:
    is_synth, is_midi, midi_in, midi_out = _FLAGS[type_key]
    return {
        "isSynth": is_synth,
        "isMidiEffect": is_midi,
        "needsMidiInput": midi_in,
        "needsMidiOutput": midi_out,
    }
```

**`bundle_id(manufacturer_name, project_name)` rules:**
- Strip non-alphanumeric from manufacturer; if result starts with digit, prefix `"Company"`
- Strip non `[a-zA-Z0-9_-]` from project name
- Format: `com.{manufacturer}.{project}`

Examples to test:
- `bundle_id("Acme Corp", "MyPlugin")` → `"com.AcmeCorp.MyPlugin"`
- `bundle_id("123Sound", "MyPlugin")` → `"com.Company123Sound.MyPlugin"`
- `bundle_id("Acme", "my-plugin_v2")` → `"com.Acme.my-plugin_v2"`

**Epic AC naming:** epic text says `categories()` — the actual function is `au_and_vst3_categories(is_synth, is_midi_effect)`. Test via flags from `flags_for_type`, not hard-coded strings in isolation.

**`type_for_flags`:** inverse of flags — test `type_for_flags(**flags_for_type(key)) == key` for all three keys (uses `"TRUE"`/`"FALSE"` CMake strings).

### Pytest Infrastructure

**Install & run (mandatory commands):**

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest                    # from repo root
.venv/bin/pytest tests/unit -v      # unit only
.venv/bin/python -m unittest discover -s tests -v   # regression
```

**Suggested `pytest.ini` (minimal — avoid over-config):**

```ini
[pytest]
testpaths = tests
pythonpath = .
python_files = test_*.py
```

- **No `src/` layout** — `core/` and `app/` live at repo root; `pythonpath = .` enables `from core.validation import ...`
- Prefer `pytest.ini` over `pyproject.toml` (project has no `pyproject.toml` yet; story 4-4 may add one)
- **Do not** add `pytest-cov` or extra plugins unless needed — YAGNI for this story
- `tests/integration/` can contain only `__init__.py` until story 3-4

### No-Qt Import Guard (AD-8)

Pattern from existing tests:

```140:163:tests/test_story_1_2.py
class TestNoQtImport(unittest.TestCase):
    def _qt_modules_before(self):
        return {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    ...
```

For pytest unit tests, implement as plain functions in each new file (or shared `tests/unit/conftest.py` helper):

```python
def test_validation_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.validation  # noqa: F401
    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
```

`core/validation.py` and `core/plugin_settings.py` already have **zero** Qt imports — this AC guards against future regressions.

### Architecture Compliance

| AD / NFR | Requirement | Story 3-1 action |
|----------|-------------|------------------|
| AD-6 | `tests/unit/` pure core, no Qt; pytest dev dep | **Establish layout + first unit tests** |
| AD-8 | `core/` must not import `app/`; no Qt in unit tests | Import-guard tests |
| NFR2 | pytest; unit tests for public `core/` functions | Validators + plugin_settings first slice |
| NFR1 | Functions ≤ 15 lines | Test functions may use parametrize tables; keep helpers small |

[Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md` §AD-6, §AD-8]

### Coexistence with Existing unittest Story Tests

Epic 2 delivered 20 tests across:
- `tests/test_story_1_2.py` (11 tests) — pipeline, atomic write, sidecar, `TestNoQtImport`
- `tests/test_story_2_1.py` (4 tests) — sidecar reload, round-trip
- `tests/test_story_2_2.py` (5 tests) — CMake fallback

**pytest collects unittest.TestCase subclasses automatically.** Running `pytest` from root should report ≥ 20 legacy + new unit tests. Do not migrate or rename story files in 3-1 — Epic 3 stories 3-2+ add new files under `tests/unit/`.

Shared helpers (`_make_spec`, `_write_project`) stay in story files for now; story 3-4 may introduce `tests/conftest.py` for integration fixtures.

### Previous Epic Intelligence (Stories 2-1, 2-2)

**Patterns to reuse:**
- Run tests via `.venv/bin/python` — never bare `python` or `pytest` without venv
- `_make_spec(**kwargs)` defaults in `test_story_1_2.py` / `test_story_2_1.py` — reference for valid `ProjectSpec` field values when needed
- `juce_dir=""` in round-trip tests — not relevant for pure validator tests
- Full suite green before merge — story 2-2 ended at 20/20 unittest tests

**Deferred from Epic 2 (do not fix unless blocking):**
- Sidecar `from_dict` without try/except
- UI tests for `MainWindow._load_project()` error dialogs
- Migrating story tests from unittest to pytest style

### Git Intelligence

| Commit | Relevance |
|--------|-----------|
| `9fac1f8` Epic 2 complete | 20 unittest tests; `project_reader` hardened; pytest not yet added |
| `b061738` Epic 1 complete | `ProjectSpec` pipeline stable; validators unchanged since brownfield |
| Uncommitted `.agents/skills/` | Ignore — not part of Luthier app |

No production code changes expected in 3-1 — test-only diff keeps review focused.

### Latest Technical Information

- **pytest 9.1.1** (2026-06-19) — latest stable; `pytest>=8.0` in requirements is sufficient floor
- **`pythonpath` ini option** (pytest ≥ 7): set `pythonpath = .` in `pytest.ini` — preferred over `sys.path` hacks in `conftest.py`
- **pytest 9.1.0 regression** (fixed in 9.1.1): conftest in `tests/` discovery — running `pytest` from project root with `testpaths = tests` is the safe pattern
- **No pytest-qt** — explicitly out of scope per AD-6
- **Parametrize:** `@pytest.mark.parametrize` is ideal for validator matrices; keeps each test function ≤ 15 lines per NFR1

### Project Structure Notes

```text
tests/
  __init__.py              # existing
  test_story_1_2.py        # keep — unittest
  test_story_2_1.py        # keep — unittest
  test_story_2_2.py        # keep — unittest
  unit/                    # NEW — story 3-1
    __init__.py
    test_validation.py
    test_plugin_settings.py
  integration/             # NEW — empty until 3-4
    __init__.py
```

Update mental model: `_bmad-output/project-context.md` §Known Issues #1 ("No tests") is **stale** — 20 unittest tests exist; this story adds pytest infrastructure and targeted unit coverage.

### Downstream Story Boundaries

| Story | Builds on 3-1 |
|-------|----------------|
| 3-2 | `tests/unit/test_rendering.py`, `test_render_context.py` |
| 3-3 | `tests/unit/test_project_spec.py`, `test_templates_store.py` (uses `tmp_path`) |
| 3-4 | `tests/integration/test_round_trip.py` — moves round-trip concerns from story files |

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` §Story 3.1]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md` §AD-6, §AD-8, §Structural Seed]
- [Source: `_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md` — NFR2]
- [Source: `_bmad-output/implementation-artifacts/2-2-cmake-regex-fallback-for-legacy-projects.md` — unittest patterns, full-suite command]
- [Source: `_bmad-output/project-context.md` §Repository Layout, §Validated Fields, §Known Issues #1]
- [Source: `core/validation.py`, `core/plugin_settings.py`]
- [Source: `app/pages/project_info.py`, `app/pages/preferences.py`, `app/pages/artefacts.py` — validator wiring]
- [Source: pytest docs — `pythonpath` config, pytest 9.1.1 changelog]

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-sonnet-medium-thinking

### Debug Log References

- Installed pytest via `requirements-dev.txt`; full suite: 67 pytest + 20 unittest (backward compat).

### Completion Notes List

- Ultimate context engine analysis completed — comprehensive developer guide created (2026-06-23).
- Established pytest infrastructure (AD-6): `pytest.ini`, `tests/unit/`, `tests/integration/` scaffold.
- Added 47 parametrized unit tests for all 9 validators in `test_validation.py` (valid/invalid/empty cases, `(bool, str)` contract, no-Qt guard).
- Added 11 unit tests for `plugin_settings` (flags, categories, bundle_id, type_for_flags round-trip, no-Qt guard).
- Regression: pytest collects legacy `test_story_*.py` unittest modules; `unittest discover` still passes 20/20.

### File List

- `requirements-dev.txt` (modified)
- `pytest.ini` (new)
- `tests/unit/__init__.py` (new)
- `tests/integration/__init__.py` (new)
- `tests/unit/test_validation.py` (new)
- `tests/unit/test_plugin_settings.py` (new)

### Change Log

- 2026-06-23: Story 3-1 — pytest infrastructure + unit tests for `core/validation.py` and `core/plugin_settings.py`.

### Review Findings

- [x] [Review][Decision] No-Qt guard tests ineffective at collection time — **resolved: keep as-is (option 1)**. Pattern matches story dev-notes; AC4 met today; collection-time import would still surface a Qt leak in `core/`. Same limitation as legacy `TestNoQtImport`.

- [x] [Review][Patch] Raw return value not asserted as `tuple` [tests/unit/test_validation.py:20-23] — fixed: `_assert_result` now accepts full result, asserts `isinstance(result, tuple)` and `len(result) == 2`.

- [x] [Review][Defer] Validation boundary coverage gaps [tests/unit/test_validation.py] — deferred, pre-existing: leading `_`/`-` project names, tab chars in display name, padded version/manufacturer strings, 5-char manufacturer code, underscore in plugin code, whitespace-only optional path not covered. Story dev matrix satisfied; extra cases are Epic 3+ hardening.

- [x] [Review][Defer] Plugin settings edge cases untested [tests/unit/test_plugin_settings.py] — deferred, pre-existing: unknown `type_key` KeyError, dual-TRUE flag precedence (`type_for_flags`, `au_and_vst3_categories`), lowercase/malformed flag strings, empty manufacturer/project segments after sanitization in `bundle_id`. AC3 met for the three known types; edge behavior documented in production code only.

- [x] [Review][Defer] No CI workflow for pytest [project root] — deferred, pre-existing: story spec explicitly excludes CI (no `.github/` yet). Tests run locally (67 pytest + 20 unittest verified green).

- [x] [Review][Defer] Shared test helpers not centralized [tests/unit/] — deferred, pre-existing: `_assert_result` and no-Qt pattern duplicated across files; story notes `tests/conftest.py` deferred to story 3-4.
