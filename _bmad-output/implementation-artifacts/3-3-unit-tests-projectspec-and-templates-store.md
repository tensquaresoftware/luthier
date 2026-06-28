---
baseline_commit: d4ecf73
---

# Story 3.3: Unit Tests — ProjectSpec and Templates Store

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer (Guillaume),
I want unit tests for `core/project_spec.py` and `core/templates_store.py`,
so that the data model serialization and template override resolution are verified in isolation.

## Acceptance Criteria

1. **Given** `tests/unit/test_project_spec.py`, **when** `ProjectSpec.from_dict(spec.to_dict())` is called for any valid spec, **then** the result equals the original on all fields (full round-trip identity).
2. **Given** a `ProjectSpec` with optional fields set to empty strings or default booleans, **when** `to_dict()` is called, **then** the dict is JSON-serializable without error (`json.dumps` succeeds).
3. **Given** `tests/unit/test_templates_store.py` using `tmp_path`, **when** a template override is written then read back via `read_effective()`, **then** the content is identical to what was written.
4. **Given** a reset is performed via `templates_store.reset()`, **when** the override path is checked, **then** the override file no longer exists, `has_override()` is `False`, and the next `read_effective()` returns the bundled default (`read_default()`).
5. **Given** `tests/unit/test_project_spec.py`, **when** pytest imports it, **then** no Qt module is imported as a side effect.

## Tasks / Subtasks

- [x] Add `tests/unit/test_project_spec.py` (AC: 1, 2, 5)
  - [x] Local `_make_spec(**kwargs)` helper with full field defaults (mirror `tests/test_story_2_1.py` — do not import from story files)
  - [x] `test_to_dict_from_dict_round_trip_all_fields` — populate every field with non-default values; assert `from_dict(to_dict()) == original` field-by-field via `dataclasses.fields`
  - [x] `test_to_dict_from_dict_round_trip_defaults` — default `ProjectSpec()` round-trips unchanged
  - [x] `test_to_dict_json_serializable_empty_optionals` — empty strings on text optionals + default booleans; `json.dumps(spec.to_dict())` succeeds
  - [x] `test_to_dict_json_serializable_populated` — non-empty optional fields + both bool combinations for copy flags
  - [x] `test_from_dict_missing_keys_use_defaults` — partial dict (e.g. only `projectName`) → remaining fields match `ProjectSpec()` defaults
  - [x] `test_to_dict_camel_case_keys` — spot-check mapping: `project_name` ↔ `projectName`, `copy_to_artefacts_dir` ↔ `copyToArtefactsDir`, etc.
  - [x] `test_project_spec_import_without_qt`

- [x] Add `tests/unit/test_templates_store.py` (AC: 3, 4)
  - [x] `pytest` fixture or helper `_patch_config_root(tmp_path, monkeypatch)` — monkeypatch `QStandardPaths.writableLocation` to return `str(tmp_path)` so `templates_root()` resolves under `tmp_path / "templates"`
  - [x] `test_save_override_source_file_round_trip` — `save_override("PluginProcessor.h", custom)` → `read_effective` returns custom
  - [x] `test_save_override_gitignore_round_trip` — same for `GITIGNORE_FILE` (override at `templates_root() / ".gitignore"`, not under `Source/`)
  - [x] `test_reset_removes_override_returns_default` — save → `has_override` True → `reset` → file gone, `has_override` False, `read_effective() == read_default()`
  - [x] `test_has_override_false_before_save` — bundled default served when no override
  - [x] `test_overrides_dir_under_templates_root` — `overrides_dir() == templates_root() / "Source"`
  - [x] Optional: `test_read_default_matches_bundled_file` — `read_default("PluginProcessor.h")` equals `Templates/Source/PluginProcessor.h` on disk

- [x] Regression guard
  - [x] `.venv/bin/pytest` — full suite green (84 existing + new tests)
  - [x] `.venv/bin/python -m unittest discover -s tests -v` still passes

## Dev Notes

### Gap Analysis — What Exists vs. What This Story Adds

| Component | Current state (post story 3-2) | This story |
|-----------|-------------------------------|------------|
| `core/project_spec.py` coverage | Indirect only in `test_story_1_2.py`, `test_story_2_1.py` (round-trip via writer/reader) | **Direct** unit tests for `to_dict` / `from_dict` / JSON serializability |
| `core/templates_store.py` coverage | **Zero** automated tests (deferred since story 1-7) | **Direct** tests with `tmp_path` + `QStandardPaths` monkeypatch |
| `tests/unit/test_project_spec.py` | Does not exist | **New** |
| `tests/unit/test_templates_store.py` | Does not exist | **New** |
| pytest infrastructure | 84 tests (58 unit + legacy story tests) | Reuse as-is — no config changes |

**This story is test-only.** No changes to `core/project_spec.py`, `core/templates_store.py`, or production templates.

### Scope — Files to Touch

| File | Change |
|------|--------|
| `tests/unit/test_project_spec.py` | **New** |
| `tests/unit/test_templates_store.py` | **New** |

**Do NOT touch in this story:**
- `core/project_spec.py`, `core/templates_store.py` — test only; behavior is correct
- `core/project_writer.py` — override resolution at write time is story 3-4 integration scope
- `app/pages/templates.py` — no Qt widget tests (AD-6)
- `tests/conftest.py` — deferred to story 3-4
- `Templates/` bundled content — read-only reference for `read_default` assertions
- CI / `.github/` — still out of scope

### Epic AC Nuances (Read Before Implementing)

**Round-trip identity (AC #1):** Use dataclass `==` (default field-wise equality). Assert every `dataclasses.fields(ProjectSpec)` name — same pattern as `test_story_2_1.py:test_read_sidecar_returns_all_fields`. Test at least one spec with **all fields non-default** and one with **factory defaults**.

**JSON serializable (AC #2):** Epic text mentions `None`; **`ProjectSpec` has no `None` fields** — all are `str` or `bool` with string/bool defaults. Test empty strings on optional text fields (`preprocessor_definitions`, `header_search_paths`, artefact paths, company fields) and both boolean copy-flag combinations. Call `json.dumps(spec.to_dict())` — no custom encoder needed.

**templates_store and Qt (AC #3–#4 vs AD-6/AD-8):** `templates_store.py` imports `PySide6.QtCore.QStandardPaths` at module level (path resolution only — no widgets, no `QApplication`). This is a **pre-existing AD-8 tension** (core module that imports Qt). Do **not** refactor to remove Qt in this story. Tests must:
- Monkeypatch `core.templates_store.QStandardPaths.writableLocation` (or pass-through lambda) to redirect config root to `tmp_path`
- Use real repo `Templates/` for bundled defaults via `templates_dir()` (no Qt, no patch needed)
- **Do not** add a no-Qt import guard on `test_templates_store.py` — importing the module loads PySide6 by design; document as accepted exception until a future path-injection refactor

**Override path layout (AC #3–#4):** Two layouts by design (story 1-7):

| File | Override path (under `templates_root()`) |
|------|------------------------------------------|
| `PluginProcessor.h` (and other `SOURCE_FILES`) | `Source/PluginProcessor.h` |
| `.gitignore` (`GITIGNORE_FILE`) | `.gitignore` (sibling of `Source/`, not inside it) |

Test **both** layouts — gitignore-only testing would miss `overrides_dir()` routing.

**Reset contract (AC #4):** `reset()` calls `unlink(missing_ok=True)` on the override path only. After reset, `read_effective()` must fall through to `read_default()` which reads bundled `Templates/`.

### `core/project_spec.py` — Public API & Field Inventory

```4:74:core/project_spec.py
@dataclass
class ProjectSpec:
    project_name: str = ""
    project_display_name: str = ""
    project_version: str = "1.0.0"
    ...
    artefacts_dir_linux: str = ""

    def to_dict(self):
        return {
            "projectName": self.project_name,
            ...
            "artefactsDirLinux": self.artefacts_dir_linux,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            project_name=d.get("projectName", ""),
            ...
            artefacts_dir_linux=d.get("artefactsDirLinux", ""),
        )
```

**Complete field ↔ dict key mapping (21 fields):**

| Python (`snake_case`) | Dict key (`camelCase`) | Default |
|----------------------|------------------------|---------|
| `project_name` | `projectName` | `""` |
| `project_display_name` | `projectDisplayName` | `""` |
| `project_version` | `projectVersion` | `"1.0.0"` |
| `manufacturer_name` | `manufacturerName` | `""` |
| `manufacturer_code` | `manufacturerCode` | `""` |
| `plugin_code` | `pluginCode` | `""` |
| `company_copyright` | `companyCopyright` | `""` |
| `company_website` | `companyWebsite` | `""` |
| `company_email` | `companyEmail` | `""` |
| `destination_dir` | `destinationDir` | `""` |
| `plugin_type` | `pluginType` | `"Instrument"` |
| `plugin_formats` | `pluginFormats` | `""` |
| `cxx_standard` | `cxxStandard` | `"C++17"` |
| `preprocessor_definitions` | `preprocessorDefinitions` | `""` |
| `header_search_paths` | `headerSearchPaths` | `""` |
| `copy_to_system_folders` | `copyToSystemFolders` | `False` |
| `copy_to_artefacts_dir` | `copyToArtefactsDir` | `True` |
| `artefacts_dir_windows` | `artefactsDirWindows` | `""` |
| `artefacts_dir_macos` | `artefactsDirMacos` | `""` |
| `artefacts_dir_linux` | `artefactsDirLinux` | `""` |

**Not on ProjectSpec (AD-7):** `juce_dir` — never test it here; belongs in `render_context` tests (story 3-2).

**Recommended `_make_spec` defaults** (non-default values for round-trip test):

```python
def _make_spec(**kwargs):
    from core.project_spec import ProjectSpec
    defaults = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        project_version="2.1.0",
        manufacturer_name="Acme",
        manufacturer_code="Acme",
        plugin_code="Mypl",
        company_copyright="Copyright 2026",
        company_website="https://acme.example",
        company_email="dev@acme.example",
        destination_dir="/tmp/out",
        plugin_type="synth",
        plugin_formats="VST3 AU",
        cxx_standard="C++20",
        preprocessor_definitions="FOO=1",
        header_search_paths="/extra/include",
        copy_to_system_folders=True,
        copy_to_artefacts_dir=False,
        artefacts_dir_windows="C:\\out",
        artefacts_dir_macos="/out/mac",
        artefacts_dir_linux="/out/linux",
    )
    defaults.update(kwargs)
    return ProjectSpec(**defaults)
```

Define locally in `test_project_spec.py` — do not import from `test_story_*.py`.

**Sidecar JSON contract (context only — integration tested in 3-4):** `ProjectWriter` writes `spec.to_dict()` to `.luthier.json`; `project_reader` calls `ProjectSpec.from_dict()`. These unit tests validate that contract at the dataclass layer without I/O.

### `core/templates_store.py` — Public API & Test Matrix

```13:67:core/templates_store.py
SOURCE_FILES = ("PluginProcessor.h", "PluginProcessor.cpp", "PluginEditor.h", "PluginEditor.cpp")
GITIGNORE_FILE = ".gitignore"
EDITABLE_FILES = SOURCE_FILES + (GITIGNORE_FILE,)

def templates_root() -> Path: ...
def overrides_dir() -> Path: ...
def has_override(name: str) -> bool: ...
def read_default(name: str) -> str: ...
def read_effective(name: str) -> str: ...
def save_override(name: str, content: str) -> None: ...
def reset(name: str) -> None: ...
```

| Function | Test case | Expected |
|----------|-----------|----------|
| `save_override` + `read_effective` | Source file name | Content round-trip |
| `save_override` + `read_effective` | `.gitignore` | Content round-trip at `templates_root()/.gitignore` |
| `has_override` | Before save | `False` |
| `has_override` | After save | `True` |
| `reset` | After save | Override file deleted |
| `read_effective` | After reset | Same as `read_default(name)` |
| `read_default` | Any editable file | Matches bundled `Templates/` content |
| `overrides_dir` | Path check | `templates_root() / "Source"` |

**Monkeypatch helper pattern:**

```python
def _patch_config_root(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "core.templates_store.QStandardPaths.writableLocation",
        lambda _location: str(tmp_path),
    )
```

After patch: `templates_root()` → `tmp_path / "templates"`, override for `PluginProcessor.h` → `tmp_path / "templates" / "Source" / "PluginProcessor.h"`.

**Constants to import in tests:** `GITIGNORE_FILE`, `SOURCE_FILES` (or pick one representative source file).

**Deferred edge cases** (document, do not fix unless blocking):
- `save_override` accepts arbitrary `name` without allowlist — internal callers only
- `read_default` raises `FileNotFoundError` if bundled asset missing
- `EDITABLE_FILES` / UI combo not tested here
- `ProjectWriter._override_for()` wiring — story 3-4 integration

### Pytest Infrastructure (Inherited from 3-1 / 3-2)

**Run commands:**

```bash
.venv/bin/pytest                    # full suite from repo root
.venv/bin/pytest tests/unit -v      # unit only
.venv/bin/python -m unittest discover -s tests -v   # regression
```

**Config** — no changes needed (`pytest.ini` already has `pythonpath = .`).

- Use `tmp_path` fixture for templates_store (filesystem isolation)
- Use `monkeypatch` for `QStandardPaths.writableLocation`
- Prefer `@pytest.mark.parametrize` for bool combinations / multiple source file names if it keeps functions ≤ 15 lines
- No `pytest-cov` — YAGNI
- Test functions ≤ 15 lines per NFR1

### No-Qt Import Guard (AD-8)

**`test_project_spec.py` only** — same pattern as stories 3-1 / 3-2:

```python
def test_project_spec_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.project_spec  # noqa: F401
    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
```

`core/project_spec.py` has zero imports beyond `dataclasses`.

**`test_templates_store.py`:** No no-Qt guard — module imports PySide6 for `QStandardPaths`. Subprocess-based isolation deferred to story 3-4 (`conftest.py`).

### Architecture Compliance

| AD / NFR | Requirement | Story 3-3 action |
|----------|-------------|------------------|
| AD-1 | `ProjectSpec` cross-layer contract; `to_dict`/`from_dict` | Direct serialization round-trip tests |
| AD-2 | Single data model (identity + artefact fields) | All 21 fields in round-trip test |
| AD-3 | Sidecar uses `to_dict`/`from_dict` | Validates JSON layer of sidecar contract |
| AD-6 | `tests/unit/` for core functions | Third slice; templates_store uses I/O + Qt path API |
| AD-7 | No `juce_dir` on `ProjectSpec` | Do not add `juce_dir` tests here |
| AD-8 | `core/` import discipline | `project_spec` no-Qt guard; `templates_store` documented exception |
| AD-9 | Overrides not on `ProjectSpec` | Test `templates_store` only — not `ProjectWriter` |
| NFR2 | Unit coverage toward ≥ 90% core/ | Covers `project_spec` + `templates_store` public API |
| NFR1 | Functions ≤ 15 lines | Parametrize; extract `_patch_config_root` helper |

[Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` §AD-1, §AD-6, §AD-8, §AD-9]

### Previous Story Intelligence (Story 3-2)

**Established patterns to reuse:**
- `tests/unit/` layout, `pytest.ini`, parametrize tables
- `_make_spec` pattern (richer version in `test_story_2_1.py`)
- No-Qt guard per **pure** module
- Field-by-field assertion via `dataclasses.fields`
- Full suite: 84 pytest + 20 unittest after 3-2

**From story 3-2 completion:**
- 16 new unit tests; test-only diff; zero production changes
- Review deferred: shared `conftest.py`, subprocess Qt guard, edge cases — carry forward to 3-4

**Existing indirect coverage to avoid duplicating:**
- `test_story_2_1.py:test_read_sidecar_returns_all_fields` — integration-level ProjectSpec equality via writer/reader; keep as regression, do not delete
- `test_story_1_2.py` — sidecar JSON smoke; not a substitute for `to_dict`/`from_dict` unit tests

### Git Intelligence

| Commit | Relevance |
|--------|-----------|
| `d4ecf73` Story 3-2 done | 84 pytest tests; rendering + render_context unit coverage |
| `c3e1309` Story 3-1 done | pytest infrastructure; `tests/unit/` established |
| Story 1-7 (in epic 1) | `templates_store` gitignore paths; zero tests until this story |

No production code changes expected — test-only diff.

### Latest Technical Information

- **pytest 9.x** — `tmp_path` and `monkeypatch` are built-in; no extra plugins
- **`json.dumps`** on `to_dict()` output — all values are `str` or `bool`; JSON-native
- **PySide6 `QStandardPaths.writableLocation`** — monkeypatch at `core.templates_store.QStandardPaths.writableLocation` (patch where used, not at import site of Qt)
- No web research required for library versions — stdlib + existing pytest floor (`>=8.0`)

### Project Structure Notes

```text
tests/
  test_story_1_2.py        # keep — ProjectSpec smoke via generation
  test_story_2_1.py        # keep — _make_spec + field equality reference
  unit/
    test_validation.py     # story 3-1
    test_plugin_settings.py
    test_rendering.py        # story 3-2
    test_render_context.py
    test_project_spec.py     # NEW — story 3-3
    test_templates_store.py  # NEW — story 3-3
  integration/             # empty until 3-4
```

### Downstream Story Boundaries

| Story | Builds on 3-3 |
|-------|----------------|
| 3-4 | `tests/integration/test_round_trip.py` — full `ProjectWriter` + `project_reader` cycle; may add `tests/conftest.py` with shared `_make_spec` and Qt subprocess guard |

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` §Story 3.3]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` §AD-1, §AD-6, §AD-8, §AD-9]
- [Source: `_bmad-output/implementation-artifacts/3-2-unit-tests-rendering-render-context.md`]
- [Source: `_bmad-output/implementation-artifacts/1-7-gitignore-as-a-customizable-template.md` §templates_store path layout]
- [Source: `_bmad-output/project-context.md` §Template Overrides]
- [Source: `core/project_spec.py`, `core/templates_store.py`]
- [Source: `tests/test_story_2_1.py` — `_make_spec` and field equality pattern]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed — comprehensive developer guide created (2026-06-23).
- Added 10 `test_project_spec.py` tests: round-trip (all fields + defaults), JSON serializability (empty + 4 bool combos), partial `from_dict`, camelCase key mapping, no-Qt import guard.
- Added 6 `test_templates_store.py` tests: source + gitignore override round-trips, reset contract, `has_override` before save, `overrides_dir` layout, bundled default match — all via `QStandardPaths` monkeypatch to `tmp_path`.
- Full suite: 100 pytest + 20 unittest — all green. Test-only diff; zero production changes.

### File List

- tests/unit/test_project_spec.py (new)
- tests/unit/test_templates_store.py (new)

### Change Log

- 2026-06-23: Story 3-3 — unit tests for `ProjectSpec` serialization and `templates_store` override resolution (16 new tests).

### Review Findings

- [x] [Review][Defer] JSON string round-trip untested [`tests/unit/test_project_spec.py:56-70`] — deferred, pre-existing
- [x] [Review][Defer] GITIGNORE reset contract untested [`tests/unit/test_templates_store.py:39-45`] — deferred, pre-existing
- [x] [Review][Defer] `read_default` GITIGNORE bundled path untested [`tests/unit/test_templates_store.py:59-61`] — deferred, pre-existing
- [x] [Review][Defer] `from_dict` type/null/empty-string edge cases [`tests/unit/test_project_spec.py:73-80`] — deferred, pre-existing
- [x] [Review][Defer] Empty override and idempotent `reset()` semantics [`tests/unit/test_templates_store.py:25-45`] — deferred, pre-existing
