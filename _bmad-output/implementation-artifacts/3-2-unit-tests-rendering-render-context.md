---
baseline_commit: c3e1309bd0bf85e8a662e0af267a82f3396ceabd
---

# Story 3.2: Unit Tests — Rendering & Render Context

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer (Guillaume),
I want unit tests for `core/rendering.py` and `core/render_context.py`,
so that the two-pass template system and context construction are verified for all project configurations.

## Acceptance Criteria

1. **Given** `tests/unit/test_rendering.py`, **when** pytest runs, **then** `render()` is tested with a valid str.format template (correct substitution), a template with a missing key (raises `KeyError`), and `render_tokens()` with `@KEY@` placeholders (correct substitution and no-op when key absent).
2. **Given** `tests/unit/test_render_context.py`, **when** `build_context(spec)` is called with a `ProjectSpec` having empty optional fields (preprocessor defs, header paths), **then** the returned context has `headerSearchPathsBlock == ""` and `extraDefinitionsBlock == ""` (empty CMake blocks — keys present, no injected CMake content).
3. **Given** `build_context(spec)` is called with all three plugin types (`synth`, `effect`, `midi`), **when** the context is inspected, **then** flag fields (`isSynth`, `isMidiEffect`, `needsMidiInput`, `needsMidiOutput`) and category fields (`auMainType`, `vst3Categories`) match the expected values per `plugin_settings.py`.
4. **Given** any unit test in `tests/unit/`, **when** pytest imports it, **then** no Qt module is imported as a side effect.

## Tasks / Subtasks

- [x] Add `tests/unit/test_rendering.py` (AC: 1, 4)
  - [x] `test_render_substitutes_valid_template` — e.g. `"Hello {name}"` + `{"name": "Foo"}` → `"Hello Foo"`
  - [x] `test_render_literal_braces` — `"${{VAR}}"` with minimal context → `"${VAR}"` (CMake brace-escape contract)
  - [x] `test_render_missing_key_raises_key_error` — `pytest.raises(KeyError)`
  - [x] `test_render_tokens_substitutes_placeholder` — `"@PROJECT_NAME@"` replaced
  - [x] `test_render_tokens_multiple_occurrences` — all `@KEY@` instances replaced
  - [x] `test_render_tokens_absent_key_noop` — placeholder left unchanged when key not in dict
  - [x] `test_rendering_import_without_qt`

- [x] Add `tests/unit/test_render_context.py` (AC: 2, 3, 4)
  - [x] Local `_make_spec(**kwargs)` helper (copy pattern from `tests/test_story_2_1.py` — do not import from story files)
  - [x] `test_build_context_empty_optional_cmake_blocks` — empty `preprocessor_definitions` + `header_search_paths` → both block keys are `""`
  - [x] `test_build_context_populated_cmake_blocks` — non-empty paths/defs produce blocks containing `target_include_directories` / `target_compile_definitions` and project name
  - [x] Parametrize `plugin_type` ∈ `synth`, `effect`, `midi` — assert flags + `auMainType` + `vst3Categories` (reuse expected values from `test_plugin_settings.py`)
  - [x] `test_build_context_value_keys_passthrough` — `_VALUE_KEYS` map from spec fields
  - [x] `test_build_context_juce_dir_empty` — `juceDirSetLine == ""` when `juce_dir=""` or whitespace (AD-7)
  - [x] `test_build_context_juce_dir_set` — non-empty path → `set(JUCE_DIR "...")\n`
  - [x] `test_build_tokens_returns_project_keys` — `PROJECT_NAME`, `PROJECT_DISPLAY_NAME` from spec
  - [x] `test_render_context_import_without_qt`

- [x] Regression guard (AC: 1)
  - [x] `.venv/bin/pytest` — full suite green (legacy unittest story tests + story 3-1 unit tests + new tests)
  - [x] `.venv/bin/python -m unittest discover -s tests -v` still passes

### Review Findings

- [x] [Review][Defer] No-Qt import guard limited to re-import after top-level load [`tests/unit/test_rendering.py:36`, `tests/unit/test_render_context.py:140`] — deferred, pre-existing (pattern from story 3-1; conftest/subprocess guard deferred to 3-4)
- [x] [Review][Defer] `render()` / `render_tokens()` edge cases beyond AC [`tests/unit/test_rendering.py`] — deferred, pre-existing (malformed format, positional placeholders, multi-key tokens, nested substitutions — production behavior unchanged)
- [x] [Review][Defer] Whitespace-only preprocessor/header lines not tested [`tests/unit/test_render_context.py:77`] — deferred, pre-existing (`_non_empty_lines` filters them; optional hardening)
- [x] [Review][Defer] Unknown `plugin_type` KeyError not tested [`tests/unit/test_render_context.py:100`] — deferred, pre-existing (explicitly out of scope per story dev notes)
- [x] [Review][Defer] `copyToSystemFolders` / `copyToArtefactsDir` ON/OFF mapping not asserted [`tests/unit/test_render_context.py:111`] — deferred, pre-existing (not in epic AC; `_copy_config` wiring untested here)
- [x] [Review][Defer] Artefact entry generation not covered [`tests/unit/test_render_context.py:50`] — deferred, pre-existing (recommended in dev notes, not epic AC)
- [x] [Review][Defer] `bundleId` sanitization not re-tested [`tests/unit/test_render_context.py`] — deferred, pre-existing (covered in story 3-1 `test_plugin_settings.py`)
- [x] [Review][Defer] `cxxStandard` C++→numeric strip not asserted [`tests/unit/test_render_context.py:64`] — deferred, pre-existing (`_extra_fields` behavior; not in story AC)
- [x] [Review][Defer] `juce_dir` paths with quotes/backslashes not tested [`tests/unit/test_render_context.py:125`] — deferred, pre-existing (known deferred issue since story 1-6)
- [x] [Review][Defer] Empty `project_name` / `project_display_name` in `build_tokens` not tested [`tests/unit/test_render_context.py:131`] — deferred, pre-existing (edge case outside AC)
- [x] [Review][Defer] `KeyError` test does not assert missing key name [`tests/unit/test_rendering.py:18`] — deferred, pre-existing (stdlib behavior; minor assertion hardening)

## Dev Notes

### Gap Analysis — What Exists vs. What This Story Adds

| Component | Current state (post story 3-1) | This story |
|-----------|-------------------------------|------------|
| `core/rendering.py` coverage | **Zero** direct tests | Full unit coverage of `render()` + `render_tokens()` |
| `core/render_context.py` coverage | Smoke only in `tests/test_story_1_2.py` (`projectName` / `projectDisplayName`) | Direct tests for CMake blocks, plugin types, `juce_dir`, tokens |
| `tests/unit/test_rendering.py` | Does not exist | **New** |
| `tests/unit/test_render_context.py` | Does not exist | **New** |
| pytest infrastructure | Established in 3-1 (`pytest.ini`, `tests/unit/`) | Reuse as-is — no config changes |

**This story is test-only.** No changes to `core/rendering.py`, `core/render_context.py`, or production templates.

### Scope — Files to Touch

| File | Change |
|------|--------|
| `tests/unit/test_rendering.py` | **New** |
| `tests/unit/test_render_context.py` | **New** |

**Do NOT touch in this story:**
- `core/rendering.py`, `core/render_context.py` — test only; behavior is correct
- `core/plugin_settings.py` — already covered in story 3-1; `render_context` tests verify **wiring**, not re-test `bundle_id` exhaustively
- `tests/test_story_*.py` — keep unittest modules; pytest must still collect them
- `tests/conftest.py` — deferred to story 3-4
- `Templates/` — integration round-trip is story 3-4
- CI / `.github/` — still out of scope

### Epic AC Nuances (Read Before Implementing)

**Optional CMake blocks (AC #2):** Epic text says "no entries for those optional CMake blocks." The implementation always includes keys `headerSearchPathsBlock` and `extraDefinitionsBlock` in the context dict; when inputs are empty, values are **empty strings** `""` — not absent keys. Templates inject these as `{headerSearchPathsBlock}` / `{extraDefinitionsBlock}`; empty string means no CMake block is added. Assert `== ""`, not `not in context`.

**Plugin type fields (AC #3):** Epic text mentions `pluginType` in context. **`pluginType` is NOT a context key** — it drives `flags_for_type()` internally but is not passed to templates. Test the **derived** fields instead: `isSynth`, `isMidiEffect`, `needsMidiInput`, `needsMidiOutput`, `auMainType`, `vst3Categories`.

**Valid `plugin_type` values:** Use `synth`, `effect`, `midi` (from `PLUGIN_TYPES` in `plugin_settings.py`). Do not use `ProjectSpec` default `"Instrument"` in plugin-type tests — that value would raise `KeyError` in `flags_for_type`.

### `core/rendering.py` — Public API & Test Matrix

```4:13:core/rendering.py
def render(content: str, context: dict) -> str:
    """Fill a str.format template (literal braces are written as {{ }})."""
    return content.format(**context)


def render_tokens(content: str, tokens: dict) -> str:
    """Replace @KEY@ placeholders so source files stay valid C++ when edited."""
    for key, value in tokens.items():
        content = content.replace(f"@{key}@", value)
    return content
```

| Function | Case | Expected |
|----------|------|----------|
| `render` | Valid `{key}` substitution | Correct string output |
| `render` | Literal CMake braces `${{VAR}}` | Renders as `${VAR}` |
| `render` | Missing context key | `KeyError` from `str.format` |
| `render_tokens` | Token present in dict | `@KEY@` → value |
| `render_tokens` | Multiple `@KEY@` in content | All replaced |
| `render_tokens` | Key absent from dict | `@KEY@` unchanged (no-op) |

**Production usage** (context only — not tested end-to-end here):

| Pass | Files | Function |
|------|-------|----------|
| str.format | `CMakeLists.txt`, `*.cmake`, `.vscode/*.json`, `README.md` | `render()` |
| Token replace | `Source/PluginProcessor.*`, `Source/PluginEditor.*` | `render_tokens()` |

Only two source tokens exist: `@PROJECT_NAME@`, `@PROJECT_DISPLAY_NAME@`.

### `core/render_context.py` — Public API & Context Inventory

```17:28:core/render_context.py
def build_context(spec: ProjectSpec, juce_dir: str = "") -> dict:
    d = spec.to_dict()
    flags = plugin_settings.flags_for_type(d["pluginType"])
    context = {key: d[key] for key in _VALUE_KEYS}
    context.update(flags)
    context.update(_categories(flags))
    context.update(_copy_config(d))
    context.update(_artefact_entries(d))
    context.update(_juce_dir_line(juce_dir))
    context["bundleId"] = plugin_settings.bundle_id(d["manufacturerName"], d["projectName"])
    context.update(_extra_fields(d))
    return context
```

**Full context key inventory:**

| Source | Keys |
|--------|------|
| `_VALUE_KEYS` | `projectName`, `projectDisplayName`, `projectVersion`, `manufacturerName`, `manufacturerCode`, `pluginCode`, `pluginFormats` |
| `flags_for_type` | `isSynth`, `isMidiEffect`, `needsMidiInput`, `needsMidiOutput` |
| `_categories` | `auMainType`, `vst3Categories` |
| `_copy_config` | `copyToSystemFolders`, `copyToArtefactsDir`, `artefactsDirWindows`, `artefactsDirMacos`, `artefactsDirLinux` |
| `_artefact_entries` | `macosArtefactEntry`, `windowsArtefactEntry`, `linuxArtefactEntry` |
| `_juce_dir_line` | `juceDirSetLine` |
| `bundle_id` | `bundleId` |
| `_extra_fields` | `cxxStandard`, `companyCopyright`, `companyWebsite`, `companyEmail`, `headerSearchPathsBlock`, `extraDefinitionsBlock` |

**Expected flag/category values** — copy from `tests/unit/test_plugin_settings.py`:

```15:40:tests/unit/test_plugin_settings.py
_EXPECTED_FLAGS = {
    "synth": {
        "isSynth": "TRUE",
        "isMidiEffect": "FALSE",
        "needsMidiInput": "TRUE",
        "needsMidiOutput": "FALSE",
    },
    ...
}
_EXPECTED_CATEGORIES = {
    "synth": ("kAudioUnitType_MusicDevice", "Instrument|Synth"),
    "effect": ("kAudioUnitType_Effect", "Fx"),
    "midi": ("kAudioUnitType_MIDIProcessor", "Fx|MIDI"),
}
```

In `test_render_context.py`, either duplicate these constants locally (preferred — no cross-file imports between test modules) or import from `plugin_settings` + re-derive. Do **not** import private constants from `test_plugin_settings.py`.

**`build_tokens` contract:**

```74:79:core/render_context.py
def build_tokens(spec: ProjectSpec) -> dict:
    return {
        "PROJECT_NAME": spec.project_name,
        "PROJECT_DISPLAY_NAME": spec.project_display_name,
    }
```

### `_make_spec` Helper Pattern

Use the richer helper from story 2-1 as the baseline — includes optional fields needed for CMake block tests:

```9:35:tests/test_story_2_1.py
def _make_spec(**kwargs):
    from core.project_spec import ProjectSpec
    defaults = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        ...
        plugin_type="synth",
        preprocessor_definitions="FOO=1",
        header_search_paths="/extra/include",
        ...
    )
    defaults.update(kwargs)
    return ProjectSpec(**defaults)
```

Define `_make_spec` **locally** in `test_render_context.py` — do not import from `test_story_*.py` (those are unittest modules, not a shared fixture package).

**Minimal spec for empty-block test:**

```python
_make_spec(
    plugin_type="synth",
    preprocessor_definitions="",
    header_search_paths="",
)
```

**Populated-block test** — use defaults from story 2-1 helper or explicit:

```python
_make_spec(
    preprocessor_definitions="FOO=1\nBAR=2",
    header_search_paths="/path/a\n/path/b",
)
```

Assert blocks contain `target_compile_definitions`, `target_include_directories`, and `MyPlugin` (default project name).

### `juce_dir` (AD-7)

`juce_dir` is **never** on `ProjectSpec`. Passed as second arg to `build_context(spec, juce_dir=...)`:

```31:35:core/render_context.py
def _juce_dir_line(juce_dir: str) -> dict:
    path = (juce_dir or "").strip()
    if not path:
        return {"juceDirSetLine": ""}
    return {"juceDirSetLine": f'set(JUCE_DIR "{path}")\n'}
```

Test cases:
- `build_context(spec)` → `juceDirSetLine == ""`
- `build_context(spec, juce_dir="   ")` → `""`
- `build_context(spec, juce_dir="/Applications/JUCE")` → `'set(JUCE_DIR "/Applications/JUCE")\n'`

### Artefact Entries (Recommended, Not Epic AC)

High-value additions beyond minimal AC:

| Condition | `*ArtefactEntry` keys |
|-----------|----------------------|
| `copy_to_artefacts_dir=False` | all `""` |
| `copy_to_artefacts_dir=True` but path empty | `""` |
| enabled + path set | JSON fragment with `ARTEFACTS_DIR_MACOS` etc. |

```68:71:core/render_context.py
def _artefact_entry(enabled: bool, key: str, path: str) -> str:
    if not enabled or not path:
        return ""
    return f',\n        "{key}": "{path}"'
```

**Deferred edge cases** (document, do not fix unless blocking):
- Unknown `plugin_type` → `KeyError` in `flags_for_type`
- Windows backslashes in artefact paths may break JSON fragments
- `RenderError` wrapper not implemented (architecture deferred)

### Pytest Infrastructure (Inherited from 3-1)

**Run commands:**

```bash
.venv/bin/pytest                    # full suite from repo root
.venv/bin/pytest tests/unit -v      # unit only
.venv/bin/python -m unittest discover -s tests -v   # regression
```

**Config** — no changes needed:

```1:4:pytest.ini
[pytest]
testpaths = tests
pythonpath = .
python_files = test_*.py
```

- Prefer `@pytest.mark.parametrize` for plugin-type matrix and rendering cases
- No `conftest.py` until story 3-4
- No `pytest-cov` — YAGNI
- Test functions ≤ 15 lines per NFR1 (parametrize tables keep functions short)

### No-Qt Import Guard (AD-8)

Pattern from story 3-1 — one guard per new test file:

```python
def test_rendering_import_without_qt():
    before = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    import core.rendering  # noqa: F401
    after = {k for k in sys.modules if "PySide6" in k or "PyQt" in k}
    assert before == after
```

`core/rendering.py` has zero imports. `core/render_context.py` imports only `plugin_settings` and `ProjectSpec` — no Qt.

### Architecture Compliance

| AD / NFR | Requirement | Story 3-2 action |
|----------|-------------|------------------|
| AD-6 | `tests/unit/` pure core, no Qt, no I/O | Add rendering + render_context unit tests |
| AD-7 | `juce_dir` Preferences-only, passed separately | Test `build_context(spec, juce_dir=...)` |
| AD-8 | `core/` must not import `app/`; no Qt in unit tests | Import-guard tests |
| NFR2 | Unit tests for public `core/` functions | Second slice after validators/plugin_settings |
| NFR1 | Functions ≤ 15 lines | Parametrize; keep helpers small |

[Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` §AD-6, §AD-7, §AD-8]

### Previous Story Intelligence (Story 3-1)

**Established patterns to reuse:**
- `pytest.ini` with `pythonpath = .` — enables `from core.rendering import ...`
- `tests/unit/` layout with `__init__.py`
- Parametrize tables in `test_validation.py` / `test_plugin_settings.py`
- No-Qt guard per module
- pytest collects legacy `test_story_*.py` unittest modules automatically

**From story 3-1 completion:**
- Full suite was 67 pytest + 20 unittest tests after 3-1
- `_assert_result` pattern for tuple validation — not needed here (no validators)
- Review deferred: shared `conftest.py`, edge cases for unknown `type_key`, CI workflow

**Existing indirect coverage to avoid duplicating:**
- `TestRenderContextAcceptsSpec` in `test_story_1_2.py` — basic `projectName` / token smoke; keep as regression, do not delete
- Round-trip tests in `test_story_2_1.py` / `test_story_2_2.py` — integration concerns; story 3-4 owns dedicated integration tests

### Git Intelligence

| Commit | Relevance |
|--------|-----------|
| `c3e1309` Story 3-1 done | pytest infrastructure; 58 new unit tests; `tests/unit/` established |
| `9fac1f8` Epic 2 complete | `render_context` used in all round-trip tests via `_make_spec` |
| `659520f` Story 1-6 | `juce_dir` wired through `build_context(spec, juce_dir=...)` |

No production code changes expected — test-only diff.

### Latest Technical Information

- **pytest 9.1.1** (2026-06) — `pytest>=8.0` floor from 3-1 is sufficient
- **`pythonpath` ini option** — already configured; no `sys.path` hacks
- **No pytest-qt** — explicitly out of scope per AD-6
- **`str.format` KeyError** — standard library behavior; no custom `RenderError` yet

### Project Structure Notes

```text
tests/
  test_story_1_2.py        # keep — includes TestRenderContextAcceptsSpec smoke
  test_story_2_1.py        # keep — _make_spec pattern reference
  test_story_2_2.py        # keep
  unit/
    test_validation.py     # story 3-1
    test_plugin_settings.py
    test_rendering.py      # NEW — story 3-2
    test_render_context.py # NEW — story 3-2
  integration/             # empty until 3-4
```

### Downstream Story Boundaries

| Story | Builds on 3-2 |
|-------|----------------|
| 3-3 | `test_project_spec.py`, `test_templates_store.py` (uses `tmp_path`) |
| 3-4 | `tests/integration/test_round_trip.py` — full template write/read; may introduce `tests/conftest.py` |

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` §Story 3.2]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` §AD-6, §AD-7, §AD-8]
- [Source: `_bmad-output/implementation-artifacts/3-1-test-infrastructure-unit-tests-validators-and-plugin-settings.md`]
- [Source: `_bmad-output/project-context.md` §Two-Pass Template Rendering, §Data Flow]
- [Source: `core/rendering.py`, `core/render_context.py`]
- [Source: `core/project_spec.py` — `to_dict()` field mapping]
- [Source: `tests/unit/test_plugin_settings.py` — expected flags/categories]
- [Source: `tests/test_story_2_1.py` — `_make_spec` defaults]

## Dev Agent Record

### Agent Model Used

Composer

### Debug Log References

- Implementation plan: test-only story; red-green-refactor applied per task — tests written first, all passed on first run (production code unchanged).
- `test_rendering.py`: 7 tests covering `render()` substitution, literal brace escape, KeyError on missing key, `render_tokens()` substitution/multiple/no-op, and no-Qt import guard.
- `test_render_context.py`: 9 tests covering empty/populated CMake blocks, parametrized plugin-type flags/categories, `_VALUE_KEYS` passthrough, `juce_dir` AD-7 cases, `build_tokens`, and no-Qt import guard.
- Regression: 84 pytest + 20 unittest tests, all green.

### Completion Notes List

- Ultimate context engine analysis completed — comprehensive developer guide created (2026-06-23).
- Story 3-2 implementation complete (2026-06-23): added 16 new unit tests across `test_rendering.py` (7) and `test_render_context.py` (9). Full suite 84 pytest + 20 unittest, zero regressions. No production code changes.
### File List

- tests/unit/test_rendering.py (new)
- tests/unit/test_render_context.py (new)

### Change Log

- 2026-06-23: Story 3-2 — unit tests for `core/rendering.py` and `core/render_context.py` (16 new tests, test-only diff).
