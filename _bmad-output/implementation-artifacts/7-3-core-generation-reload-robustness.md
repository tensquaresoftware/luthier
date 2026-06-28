---
baseline_commit: 782ca0c
---

# Story 7.3: Core Generation & Reload Robustness

Status: done

<!-- Epic 7 — Release Hardening. Priority: SHOULD. Order: third (after 7.1, 7.2). Ultimate context engine analysis completed - comprehensive developer guide created. -->

## Story

As a JUCE developer,
I want generation and project reload to handle edge-case inputs and legacy projects gracefully,
So that unusual paths, hand-edited sidecars, and legacy CMake projects fail with clear, actionable messages instead of silent corruption or raw exceptions.

## Acceptance Criteria

1. **Given** a `juce_dir` containing quotes, `$`, or spaces, **when** `CMakeLists.txt` is generated, **then** the `set(JUCE_DIR ...)` line is correctly quoted/escaped for CMake.
2. **Given** artefact JSON path fields with quotes or control characters, **when** presets are rendered, **then** output remains valid JSON.
3. **Given** a sidecar or dict with string booleans (`"ON"`, `"false"`, `"true"`, `"OFF"`), **when** `ProjectSpec.from_dict()` runs, **then** copy flags and similar bool fields coerce to proper `bool` values.
4. **Given** a hand-edited `.luthier.json` with wrong types or `null` for required fields, **when** `read_project()` loads the sidecar, **then** validation fails explicitly — no silent partial load.
5. **Given** an empty but syntactically valid `.luthier.json` (`{}`), **when** `read_project()` runs, **then** load fails with a warning/error distinguishing empty sidecar from parse failure.
6. **Given** CMake cache variables for bool plugin options in the template, **when** a project is regenerated, **then** `CACHE BOOL` entries use `FORCE` so cached values do not block updates.
7. **Given** an unknown `pluginType` string, **when** generation or context build runs, **then** a clear validation error is raised — not a raw `KeyError`.
8. **Given** `ProjectWriter.write()` when atomic rename fails after old directory removal, **when** the failure path executes, **then** behaviour is documented and tested for the rare case.
9. **Given** a legacy project without sidecar, **when** CMake fallback fails, **then** the error message distinguishes sidecar parse error, empty/invalid sidecar, and CMake parse failure — listing missing fields where applicable.
10. **Given** CMake with escaped quotes in parsed values, **when** regex fallback runs, **then** parsing handles escaped quotes or fails with a clear message.
11. **Given** unit/integration tests, **when** pytest runs, **then** new edge-case tests cover the above without Qt imports.

## Tasks / Subtasks

- [x] Add CMake/JSON escaping helpers (AC: 1, 2)
  - [x] New `_cmake_quoted(value: str) -> str` in `core/render_context.py` (or shared `core/paths.py` if reused by reader)
  - [x] Escape `\`, `"`, and `$` inside CMake double-quoted strings
  - [x] Wire into `_juce_dir_line()` and `Templates/CMakeLists.txt` artefact `set(ARTEFACTS_DIR_* "...")` context values
  - [x] Replace `_artefact_entry()` f-string with `json.dumps` fragment so quotes/control chars produce valid JSON

- [x] Bool coercion in `ProjectSpec.from_dict()` (AC: 3)
  - [x] Add `_coerce_bool(value, default: bool) -> bool` accepting `bool`, `"ON"`/`"OFF"`, `"true"`/`"false"`, `0`/`1`, `None` → default
  - [x] Apply to `copyToSystemFolders` and `copyToArtefactsDir`
  - [x] Reuse coercion logic aligned with `project_reader._bool()` (lines 220–222) — do not duplicate divergent rules

- [x] Sidecar validation + error taxonomy (AC: 4, 5, 9, 10)
  - [x] Extend `ProjectReadResult` with `error: str | None = None` (human-readable reason; core-only, no Qt)
  - [x] Define sidecar error constants or short codes: `MALFORMED_JSON`, `EMPTY_SIDECAR`, `INVALID_SIDECAR`
  - [x] Validate required sidecar keys before `from_dict`: `projectName` (non-empty str), `pluginFormats` (non-empty str), `pluginType` (valid enum)
  - [x] Reject `null` or wrong types for required keys with explicit `error` message listing the problem
  - [x] Reject `{}` as empty sidecar (AC5) — do not defer to UI "No plugin formats" check
  - [x] Fix `_quoted_fields()` to use `_SET_RE`-style escaped-quote parsing (or shared extractor)
  - [x] Populate `missing_fields` for CMake fallback path (already works); set `error` for sidecar failures

- [x] Template CACHE BOOL FORCE (AC: 6)
  - [x] Append `FORCE` to lines 64–65 in `templates/CMakeLists.txt`
  - [x] Update `tests/conftest.py` minimal CMake fixture if it mirrors those lines

- [x] Unknown plugin type guard (AC: 7)
  - [x] `flags_for_type()` raises `ValueError` listing valid keys from `PLUGIN_TYPES`
  - [x] Optionally validate in `from_dict` / sidecar validator for early load failure

- [x] ProjectWriter rename failure (AC: 8)
  - [x] Document data-loss window in `write()` docstring (after `rmtree`, before successful `rename`)
  - [x] Test: mock `Path.rename` to fail after successful write + `rmtree`; assert exception propagates

- [x] App-layer error propagation (AC: 9)
  - [x] `MainWindow._load_project`: use `result.error` for discriminated sidecar messages
  - [x] Keep existing CMake `missing_fields` bullet list for legacy path
  - [x] No Qt imports added to `core/`

- [x] Tests (AC: 11)
  - [x] New `tests/unit/test_project_reader.py` — sidecar validation, empty `{}`, malformed JSON, escaped quotes
  - [x] Extend `tests/unit/test_render_context.py` — special paths, invalid plugin type
  - [x] Extend `tests/unit/test_project_spec.py` — string bool coercion
  - [x] Extend `tests/test_story_1_2.py` or `tests/unit/test_project_writer.py` — rename failure
  - [x] Optional integration: assert rendered `CMakeUserPresets.json` parses via `json.loads`

- [x] Documentation + deferred-work (AC: 9)
  - [x] Strike generation/reload items in `deferred-work.md` when done
  - [x] No architecture AD change required unless error taxonomy becomes a new AD (prefer extending AD-3 note in module docstring only)

- [x] Regression
  - [x] Full suite: `.venv/bin/pytest` (221 tests collected baseline from 7.2 merge)

## Dev Notes

### Epic 7 context

Epic 7 is the post-MVP quality gate before manual QA (week of 2026-07-07). Stories 7.1 (CI) and 7.2 (atomic JSON persistence) are **done**. This story closes all open items under **Génération et rechargement (cas limites)** in `deferred-work.md`.

| Story | Scope | Status |
|-------|-------|--------|
| 7.1 | GitHub Actions pytest CI | **done** |
| 7.2 | Atomic prefs + app_state JSON; corrupt-file feedback | **done** |
| **7.3** | Generation/reload edge cases | **this story** |
| 7.4 | Test hygiene + minor UI hardening | backlog |

### Current implementation — gaps to close

#### 1. JUCE_DIR quoting (`core/render_context.py:32–36`)

```python
return {"juceDirSetLine": f'set(JUCE_DIR "{path}")\n'}
```

No escaping for embedded `"`, `$`, or `\`. Spaces work; special chars break CMake.

#### 2. Artefact preset JSON (`core/render_context.py:69–73`)

```python
return f',\n        "{key}": "{normalized}"'
```

Raw f-string — a path like `C:/out"bad` or newline produces invalid JSON in `CMakeUserPresets.json`.

#### 3. Bool coercion (`core/project_spec.py:76–77`)

```python
copy_to_system_folders=d.get("copyToSystemFolders", False),
copy_to_artefacts_dir=d.get("copyToArtefactsDir", True),
```

String `"OFF"` is truthy in Python; `"false"` string passes through. Downstream `_on_off()` and `_artefact_entry()` misbehave.

**Contrast:** `project_reader._bool()` already handles `"ON"`/`"OFF"` for CMake reads — align coercion rules.

#### 4. Sidecar loading (`core/project_reader.py:84–92`)

```python
def _read_sidecar(sidecar: Path, project_dir: Path) -> Optional[ProjectSpec]:
    ...
    return ProjectSpec.from_dict(data)
```

- No schema validation; `{}` succeeds → empty `project_name`, empty `plugin_formats`
- UI catches empty formats later (`main_window.py:435–438`) — AC5 requires failure at reader level
- Malformed JSON returns `None` with no discriminated `error`

#### 5. CACHE BOOL without FORCE (`templates/CMakeLists.txt:64–65`)

```cmake
set(COPY_TO_SYSTEM_FOLDERS ${USER_COPY_TO_SYSTEM_FOLDERS} CACHE BOOL "...")
set(COPY_TO_ARTEFACTS_DIR ${USER_COPY_TO_ARTEFACTS_DIR} CACHE BOOL "...")
```

`JUCE_DIR` cache already uses `FORCE` (line 93). Copy flags do not — regeneration may not update cached bools.

#### 6. Unknown pluginType (`core/plugin_settings.py:26–27`)

```python
is_synth, is_midi, midi_in, midi_out = _FLAGS[type_key]  # KeyError
```

No guard in `build_context()` or `ProjectGenerator.generate()`.

#### 7. ProjectWriter rename hazard (`core/project_writer.py:50–52`)

If `shutil.rmtree(self._project)` succeeds but `tmp.rename(self._project)` fails, both old project and `.tmp` are lost (except block cleans `.tmp`). Undocumented, untested.

#### 8. Escaped quotes in CMake identity fields (`core/project_reader.py:170–176`)

`_quoted_fields` uses `[^"]*` — breaks on `COMPANY_NAME "O\"Reilly"`. `_SET_RE` (line 22) already handles escaped quotes in `_parse_set_vars`.

#### 9. UI error messages (`app/main_window.py:417–431`)

Sidecar failure → generic "invalid or unreadable". CMake failure → good bullet list. Need to wire `result.error` for sidecar-specific messages.

### Recommended implementation

#### 1. Escaping helpers

```python
def _cmake_quoted(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    return f'"{escaped}"'

def _juce_dir_line(juce_dir: str) -> dict:
    path = normalize_portable_path((juce_dir or "").strip())
    if not path:
        return {"juceDirSetLine": ""}
    return {"juceDirSetLine": f"set(JUCE_DIR {_cmake_quoted(path)})\n"}
```

For preset entries, prefer:

```python
def _artefact_entry(enabled: bool, key: str, path: str) -> str:
    if not enabled or not path:
        return ""
    fragment = json.dumps({key: normalize_portable_path(path)}, ensure_ascii=False)
    inner = fragment[1:-1]  # drop outer {}
    return f",\n        {inner}"
```

Also pass `_cmake_quoted()` for `artefactsDirWindows/Macos/Linux` in `_copy_config()` if template uses quoted CMake sets.

#### 2. `_coerce_bool(value, default: bool) -> bool`

Accept: `bool`, `None` → default, int 0/1, str `"ON"`/`"OFF"`/`"true"`/`"false"`/`"1"`/`"0"` (case-insensitive). Unknown non-empty strings → default or raise in sidecar validator (prefer default for lenient `from_dict`, strict validation in reader).

#### 3. Extend `ProjectReadResult`

```python
@dataclass(frozen=True)
class ProjectReadResult:
    spec: Optional[ProjectSpec]
    missing_fields: tuple[str, ...] = ()
    error: str | None = None
```

Update `read_project_result`:

- Sidecar exists + JSON parse fail → `error="Sidecar file is not valid JSON."`
- Sidecar `{}` → `error="Sidecar file is empty — no project configuration found."`
- Sidecar validation fail → `error="Sidecar is missing required fields: …"` or field-specific type message
- CMake path unchanged — `missing_fields` populated, `error=None`

Change `_read_sidecar` to return `ProjectReadResult` (not bare `Optional[ProjectSpec]`) or have wrapper set `error`.

**Required sidecar fields** (minimum viable project):

| Key | Rule |
|-----|------|
| `projectName` | non-empty `str` |
| `pluginFormats` | non-empty `str` (space-separated) |
| `pluginType` | one of `instrument`, `audio-effect`, `midi-effect` |

Optional fields keep `from_dict` defaults. Reject `null` for required keys.

#### 4. `flags_for_type` guard

```python
def flags_for_type(type_key: str) -> dict:
    if type_key not in _FLAGS:
        valid = ", ".join(k for k, _ in PLUGIN_TYPES)
        raise ValueError(f"Unknown plugin type {type_key!r}. Expected one of: {valid}.")
    ...
```

#### 5. Template change

```cmake
set(COPY_TO_SYSTEM_FOLDERS ${USER_COPY_TO_SYSTEM_FOLDERS} CACHE BOOL "..." FORCE)
set(COPY_TO_ARTEFACTS_DIR ${USER_COPY_TO_ARTEFACTS_DIR} CACHE BOOL "..." FORCE)
```

#### 6. `_quoted_fields` fix

Replace naive regex with extraction via `_SET_RE` or shared `_parse_quoted_set(name, text)` that unescapes `\"` like `_parse_set_vars` (lines 214–215).

#### 7. `MainWindow._load_project` wiring

```python
if spec is None:
    if result.error:
        message = result.error
    elif sidecar.exists():
        message = "Could not read project configuration (.luthier.json is invalid or unreadable)."
    elif result.missing_fields:
        ...
```

Prefer `result.error` first — sidecar path sets it explicitly.

#### 8. ProjectWriter docstring + test

Document: "If rename fails after removing the existing project directory, the previous project tree is lost; only manual recovery (VCS/backup) is possible."

Test with `unittest.mock.patch.object(Path, "rename", side_effect=OSError(...))` after successful `_write_all`.

### Architecture compliance

| AD | Requirement | This story |
|----|-------------|------------|
| AD-3 | Sidecar first; regex fallback; partial CMake → `None` | Extend with sidecar validation + `error` field; empty `{}` must not load |
| AD-4 | Atomic project write | Document rename failure edge case; no change to happy path |
| AD-6 | No MainWindow widget tests | Unit-test `core/` only; app wiring tested indirectly via reader result shape |
| AD-7 | `juce_dir` on ProjectSpec | Escaping applies to sidecar round-trip paths |
| AD-10 | Atomic JSON for app config | Out of scope — sidecar `.luthier.json` is project data, not app config |

**Out of scope:** Full JSON Schema framework, Qt widget tests, `templates_store` overrides, prefs `null` → `"None"` UI (Story 7.4), migrating `tests/test_story_*.py` (Story 7.4).

### File structure requirements

| File | Action |
|------|--------|
| `core/render_context.py` | **UPDATE** — escaping, `_artefact_entry`, plugin type surfaces `ValueError` |
| `core/project_spec.py` | **UPDATE** — `_coerce_bool`, apply to copy flags |
| `core/project_reader.py` | **UPDATE** — `ProjectReadResult.error`, sidecar validation, `_quoted_fields` fix |
| `core/plugin_settings.py` | **UPDATE** — `flags_for_type` guard |
| `core/project_writer.py` | **UPDATE** — docstring only (+ test) |
| `templates/CMakeLists.txt` | **UPDATE** — `CACHE BOOL ... FORCE` on copy flags |
| `app/main_window.py` | **UPDATE** — discriminated open errors via `result.error` |
| `tests/unit/test_project_reader.py` | **NEW** — primary sidecar/CMake edge-case tests |
| `tests/unit/test_render_context.py` | **UPDATE** — special paths, unknown type |
| `tests/unit/test_project_spec.py` | **UPDATE** — string bool coercion |
| `tests/test_story_1_2.py` or new writer test | **UPDATE** — rename failure |
| `tests/conftest.py` | **UPDATE** if minimal CMake fixture mirrors CACHE lines |
| `_bmad-output/implementation-artifacts/deferred-work.md` | **UPDATE** — strike items when done |

**Do not modify:** `core/json_files.py`, CI workflow, preferences atomic save (7.2), unrelated UI pages.

### Testing requirements

**Sidecar tests (`test_project_reader.py`):**

```python
def test_empty_sidecar_returns_error(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / ".luthier.json").write_text("{}", encoding="utf-8")
    result = read_project_result(project_dir)
    assert result.spec is None
    assert result.error  # mentions empty

def test_sidecar_string_bools_coerced(tmp_path):
    # write sidecar with "ON"/"false" → loaded spec has proper bools

def test_sidecar_null_project_name_fails(tmp_path):
    ...
```

**Render context tests:**

- Parametrize `juce_dir`: `'/Applications/My JUCE'`, `'C:/JUCE"bad'`, `'$ENV{HOME}/JUCE'`
- Assert `set(JUCE_DIR "...")` line survives CMake quoting rules
- `build_context` with `plugin_type="Instrument"` → `ValueError` with valid types listed

**Preset JSON test:**

- Build context with path containing `"` and `\n`; render `CMakeUserPresets.json`; `json.loads` entire file succeeds

**Writer rename test:**

```python
with patch.object(Path, "rename", side_effect=OSError("simulated")):
    with pytest.raises(OSError):
        writer.write(...)
```

**Regression guards:**

- `tests/integration/test_round_trip.py` — all existing round-trips still pass
- `test_partial_cmake_returns_none_with_missing_fields` — CMake path unchanged
- `test_juce_dir_sidecar_round_trip` — still passes with escaping (paths without special chars)

Run: `.venv/bin/pytest tests/unit/test_project_reader.py tests/unit/test_render_context.py tests/unit/test_project_spec.py` then full suite.

### Previous story intelligence

**From 7.2 (`7-2-atomic-json-persistence-corrupt-file-feedback.md`):**

- `core/json_files.atomic_write_text()` exists — do not reuse for sidecar (sidecar written inside ProjectWriter temp dir, not atomic JSON module scope)
- `load_warning` pattern for corrupt app config — analogous `ProjectReadResult.error` for project sidecar
- Review pattern: wrap `save()` in try/except for startup safety — not applicable here
- Baseline after 7.2: **214 passed, 2 skipped**; current collection **221 tests**
- `_initialized` guard pattern in Preferences — not needed for reader

**From 7.1 (`7-1-github-actions-ci-for-pytest.md`):**

- CI runs on `ubuntu-latest` with Qt offscreen — new unit tests must pass without GUI
- Use forward slashes in path assertions (`normalize_portable_path`)
- No new CI deps required for pure `core/` tests

**From 2.2 (CMake fallback — already implemented):**

- `ProjectReadResult.missing_fields` with `_FIELD_LABELS` — extend, do not replace
- `test_partial_cmake_returns_none_with_missing_fields` in `tests/test_story_2_2.py` — keep green

### Git intelligence

Recent commits on `main`:

```
782ca0c Add atomic JSON persistence and corrupt-file feedback for Story 7.2.
bdc7612 Normalize architecture-spine path references across BMad artifacts.
02dd1af Add Epic 7 release hardening stories and sprint change proposal.
```

7.2 merged atomic JSON work into `core/json_files.py`, `preferences.py`, `app_state.py`, `main_window.py`. No generation/reload changes yet — greenfield on `render_context`, `project_reader`, `project_spec`.

### Latest technical information

- **CMake quoted strings:** Backslash-escape `\`, `"`, and `$` inside double-quoted arguments. Semicolons in paths are rare — out of scope unless encountered in tests.
- **JSON embedding:** `json.dumps` for preset fragments is safer than manual escaping; `ensure_ascii=False` preserves Unicode paths.
- **Python 3.14 / cp310-abi3:** No new dependencies; stdlib `json`, `re`, `pathlib` only.
- **pytest:** `unittest.mock.patch` for rename failure; `tmp_path` for sidecar fixtures.

### Project context reference

From `_bmad-output/project-context.md`:

- Function ≤15 lines — extract `_coerce_bool`, `_cmake_quoted`, `_validate_sidecar` rather than bloating existing functions
- All file I/O: `encoding="utf-8"`
- No type annotations beyond existing project style
- No comments referencing story numbers
- Git commits: English only
- `read_project()` is sole sidecar deserialiser (AD-3)
- Two-pass rendering: str.format for CMake/JSON; token replace for Source — escaping applies to str.format pass only

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 7, Story 7.3]
- [Source: `_bmad-output/implementation-artifacts/deferred-work.md` — Génération et rechargement section]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` — AD-3, AD-4, AD-7]
- [Source: `docs/architecture.md` — project_reader, render_context module contracts]
- [Source: `_bmad-output/implementation-artifacts/7-2-atomic-json-persistence-corrupt-file-feedback.md`]
- [Source: `_bmad-output/implementation-artifacts/7-1-github-actions-ci-for-pytest.md`]
- [Source: `core/project_reader.py` — sidecar + CMake fallback]
- [Source: `core/render_context.py` — `_juce_dir_line`, `_artefact_entry`]
- [Source: `app/main_window.py` — `_load_project` error handling]

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-sonnet-medium-thinking (Cursor)

### Debug Log References

- `_quoted_fields` initially used only `_parse_set_vars`; `COMPANY_NAME` lives in `juce_add_plugin` args, not `set()`. Added `_parse_quoted_field` with escaped-quote regex.

### Completion Notes List

- Added `_cmake_quoted`, JSON-safe `_artefact_entry`, and CMake-quoted artefact path context values; updated `CMakeLists.txt` template for unquoted `{artefactsDir*}` placeholders.
- Shared `_coerce_bool` in `project_spec.py`; `project_reader._bool` reuses it.
- `ProjectReadResult.error` with sidecar validation (`projectName`, `pluginFormats`, `pluginType`); empty `{}` and malformed JSON fail at reader level.
- `flags_for_type` raises `ValueError` with valid type list; sidecar validator catches unknown types at load.
- `CACHE BOOL ... FORCE` on copy flags; `ProjectWriter.write` docstring documents rename failure hazard.
- `MainWindow._load_project` prefers `result.error` for sidecar failures.
- 21 new tests; full suite **242 passed, 2 skipped**.

### File List

- `core/render_context.py`
- `core/project_spec.py`
- `core/project_reader.py`
- `core/plugin_settings.py`
- `core/project_writer.py`
- `templates/CMakeLists.txt`
- `app/main_window.py`
- `tests/unit/test_project_reader.py` (new)
- `tests/unit/test_render_context.py`
- `tests/unit/test_project_spec.py`
- `tests/unit/test_plugin_settings.py`
- `tests/test_story_1_2.py`
- `tests/conftest.py`
- `tests/test_story_2_2.py`
- `_bmad-output/implementation-artifacts/deferred-work.md`

### Change Log

- 2026-06-28: Story 7.3 — generation/reload edge-case hardening (escaping, sidecar validation, bool coercion, CACHE FORCE, error taxonomy, tests).

### Review Findings

- [x] [Review][Patch] Remove unused sidecar error constants — `ERROR_MALFORMED_JSON`, `ERROR_EMPTY_SIDECAR`, and `ERROR_INVALID_SIDECAR` are defined but never referenced; `ProjectReadResult.error` uses free-form English only [`core/project_reader.py:20-22`]
- [x] [Review][Patch] Distinguish absent vs null required sidecar keys — missing keys report `"must not be null"` via `data.get()` when the key is absent [`core/project_reader.py:122-126`]
- [x] [Review][Patch] Separate I/O failures from JSON parse errors — `OSError` and `UnicodeDecodeError` return the same message as malformed JSON [`core/project_reader.py:97-101`]
- [x] [Review][Patch] Distinguish non-dict JSON from syntax errors — valid JSON arrays/strings share the malformed-JSON message [`core/project_reader.py:104-107`]
- [x] [Review][Patch] Reject whitespace-only artefact paths — `_artefact_entry` treats `"   "` as truthy and emits empty preset entries [`core/render_context.py:83-85`]
- [x] [Review][Patch] Prefer non-empty `juce_add_plugin` values over empty `set()` vars — `_quoted_fields` stops at empty `vars_map[name]` and skips `_parse_quoted_field` [`core/project_reader.py:224-227`]
- [x] [Review][Patch] Remove unreachable generic sidecar error branch — every sidecar failure now sets `result.error`; `elif sidecar.exists()` generic message is dead code [`app/main_window.py:422-424`]
- [x] [Review][Patch] Add wrong-type required field test — `_validate_sidecar` rejects non-string types but no test covers e.g. `"projectName": 123` [`tests/unit/test_project_reader.py`]

- [x] [Review][Defer] `read_project()` still returns only `.spec` without `error` — pre-existing API; app layer uses `read_project_result()` [`core/project_reader.py:91-92`] — deferred, pre-existing
- [x] [Review][Defer] Module docstring not extended with error taxonomy — spec suggested AD-3 note in docstring only [`core/project_reader.py:1-6`] — deferred, pre-existing
- [x] [Review][Defer] Conflicting `set()` vs `juce_add_plugin` identity values — `_quoted_fields` prefers `set()` when both differ [`core/project_reader.py:224-231`] — deferred, pre-existing
- [x] [Review][Defer] `_cmake_quoted` does not escape CMake control characters (newline/tab) — AC1 covers quotes/`$`/spaces only [`core/render_context.py:34-36`] — deferred, pre-existing
