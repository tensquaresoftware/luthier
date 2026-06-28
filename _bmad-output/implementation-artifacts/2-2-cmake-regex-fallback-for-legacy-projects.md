---
baseline_commit: uncommitted-2-1
---

# Story 2.2: CMake Regex Fallback for Legacy Projects

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer with a project generated before `.luthier.json` was introduced,
I want Luthier to reload my project via CMake parsing as a fallback,
so that I don't lose access to projects created with an earlier version.

## Acceptance Criteria

1. **Given** a project directory without a `.luthier.json` sidecar, **when** `read_project()` is called, **then** it attempts `_parse_cmakelists()` via `_read_from_cmake()` as fallback.
2. **Given** the CMake file can be fully parsed (all required F1 fields present), **when** `_parse_cmakelists()` completes, **then** a complete `ProjectSpec` is returned.
3. **Given** the CMake file cannot yield a complete `ProjectSpec` (missing required fields or ambiguous values), **when** `_parse_cmakelists()` reaches the end, **then** `read_project()` returns `None` — never a partial `ProjectSpec`.
4. **Given** `read_project()` returns `None` from a failed regex fallback, **when** the error dialog is shown, **then** it indicates the project could not be parsed from CMake (distinguishing this from a sidecar read error) and lists which required fields could not be extracted.

## Tasks / Subtasks

- [x] Add completeness validation to CMake parse path in `core/project_reader.py` (AC: 2, 3)
  - [x] Define `_REQUIRED_CMAKE_KEYS` — keys that must be present **and** non-empty after `_parse_cmakelists()` (see Dev Notes for exact list)
  - [x] Add `_missing_required_fields(values: dict) -> list[str]` returning **human-readable** labels for any missing/empty required key
  - [x] Require `CMAKE_CXX_STANDARD` extraction to succeed (do not silently default to `C++17` when the line is absent — treat as missing `cxxStandard`)
  - [x] Require `juce_add_plugin` identity markers: at minimum `IS_SYNTH` must be matched (generated projects always emit it; absence means not a Luthier-style plugin block)
  - [x] Refactor `_parse_cmakelists()` to return `tuple[Optional[dict], list[str]]` — `(values, missing_labels)`; `None` dict when `project()` line missing
  - [x] Update `_read_from_cmake()`: wrap `cmake.read_text()` in `try/except OSError` → return failure; if `missing_labels` non-empty → return `None` (do not call `from_dict`)
  - [x] Add `ProjectReadResult` dataclass (`spec: Optional[ProjectSpec]`, `missing_fields: tuple[str, ...]`) and `read_project_result(project_dir) -> ProjectReadResult`
  - [x] Keep `read_project()` as thin wrapper: `return read_project_result(project_dir).spec` (preserves all existing callers/tests)

- [x] Improve CMake-failure UX in `app/main_window.py` (AC: 4)
  - [x] Replace `read_project(project_dir)` with `read_project_result(project_dir)` in `_load_project()`
  - [x] When `result.spec is None` and **no** `.luthier.json` exists: show dialog distinct from sidecar error, e.g.  
    `"Could not parse project configuration from CMakeLists.txt.\n\nMissing or unreadable fields:\n• {field1}\n• {field2}…"`
  - [x] When `CMakeLists.txt` is absent: keep concise message (`Not a JUCE plugin project: {path}`) with empty missing-fields list
  - [x] Do **not** change sidecar-failure message from story 2-1 (AC3 invariant preserved)
  - [x] Do **not** call `self._project_page.load()` on failure

- [x] Add focused tests in `tests/test_story_2_2.py` (AC: 1–4)
  - [x] `test_cmake_fallback_without_sidecar` — generate project, delete `.luthier.json`, `read_project_result()` → complete spec, all fields match
  - [x] `test_cmake_fallback_round_trip` — delete sidecar → read → regenerate → empty diff (same pattern as `test_story_2_1.test_round_trip_empty_diff`, `juce_dir=""`)
  - [x] `test_partial_cmake_returns_none_with_missing_fields` — valid `project()` but strip `COMPANY_NAME` line → `spec is None`, `missing_fields` contains `"Company Name"`
  - [x] `test_no_cmakelists_returns_none` — empty directory → `spec is None`
  - [x] `test_legacy_project_configuration_cmake` — optional: write copy-config only in `project-configuration.cmake` (pre-1.4 layout) with full `CMakeLists.txt` identity block → still loads (validates `_parse_build_settings` backward compat)
  - [x] Reuse `_make_spec()` / `_write_project()` helpers from `tests/test_story_2_1.py` (import or duplicate minimally)

- [x] Regression guard
  - [x] Run `.venv/bin/python -m unittest discover -s tests -v` — all existing tests including `test_story_2_1` must stay green

## Dev Notes

### Gap Analysis — What Exists vs. What This Story Adds

| Component | Current state (post story 2-1) | This story |
|-----------|--------------------------------|------------|
| Sidecar-first orchestration | ✅ `read_project()` → `_read_sidecar` or `_read_from_cmake` | No change to sidecar path |
| CMake fallback invoked when no sidecar | ✅ `_read_from_cmake()` called | No change to routing |
| **Completeness gate on CMake parse** | ❌ `_parse_cmakelists()` returns dict if `project()` matches — missing identity fields become empty strings via `from_dict` | **Add required-field validation; return `None` when incomplete** |
| **`_read_cxx` silent default** | ❌ Defaults to `"C++17"` when `CMAKE_CXX_STANDARD` absent | Treat absent line as missing field |
| **Missing-field diagnostics** | ❌ `MainWindow` shows generic `"Not a JUCE plugin project"` | Expose `missing_fields`; list them in dialog |
| **`read_project()` API** | Returns `Optional[ProjectSpec]` only | Add `read_project_result()`; keep `read_project()` wrapper |
| Sidecar corrupt → no fallback | ✅ Story 2-1 | **Do not regress** |

**This story completes AD-3.** Story 2-1 owns the sidecar path; story 2-2 hardens the regex fallback so partial CMake parses never produce a silently incomplete `ProjectSpec`.

### PRD vs. Architecture Note

PRD F4 mentions per-field default fallback with a warning. **AD-3 and epic AC take precedence:** a partial CMake parse returns `None` and the UI reports failure with missing-field names — never a partial load. Full failure is safer than regenerating a project with blank company identity fields.

### Scope — Files to Touch

| File | Change |
|------|--------|
| `core/project_reader.py` | Completeness validation, `ProjectReadResult`, `read_project_result()`, `_read_cxx` strictness |
| `app/main_window.py` | Use `read_project_result()`; CMake-specific error dialog with field list |
| `tests/test_story_2_2.py` | **New** — CMake fallback + partial-parse tests |

**Do NOT touch in this story:**
- `core/project_writer.py`, `core/project_spec.py` — no schema changes
- `core/project_generator.py`, `core/render_context.py`, `Templates/` — generation unchanged
- `_read_sidecar()` — story 2-1 behaviour is frozen (corrupt sidecar → `None`, no fallback)
- `app/pages/project.py` — `load(spec)` already works

### Required CMake Fields (`_REQUIRED_CMAKE_KEYS`)

These map to `ProjectSpec.to_dict()` keys. Each must be **present in the parsed values dict with a non-empty string** (booleans from build settings use their parsed values; empty artefact path strings are OK).

| Dict key | CMake source | Human label (for dialog) |
|----------|--------------|--------------------------|
| `projectName` | `project(NAME VERSION …)` | Project Name |
| `projectVersion` | same `project()` match | Project Version |
| `pluginFormats` | `set(PLUGIN_FORMATS_LIST …)` | Plugin Formats |
| `manufacturerName` | `COMPANY_NAME "…"` in `juce_add_plugin` | Company Name |
| `manufacturerCode` | `PLUGIN_MANUFACTURER_CODE` | Manufacturer Code |
| `pluginCode` | `PLUGIN_CODE` | Plugin Code |
| `projectDisplayName` | `PLUGIN_NAME` | Project Display Name |
| `companyCopyright` | `COMPANY_COPYRIGHT` | Company Copyright |
| `companyWebsite` | `COMPANY_WEBSITE` | Company Website |
| `companyEmail` | `COMPANY_EMAIL` | Company Email |
| `cxxStandard` | `set(CMAKE_CXX_STANDARD N)` — must match; value becomes `C++{N}` | C++ Standard |

**Plugin type** — not a separate required key; derived from `IS_SYNTH` / `IS_MIDI_EFFECT`. Require regex match for `IS_SYNTH` (if absent, add `"Plugin Type"` to missing list).

**Optional (empty allowed, do not gate on):**
- `preprocessorDefinitions`, `headerSearchPaths`
- `copyToSystemFolders`, `copyToArtefactsDir`, `artefactsDirWindows/Macos/Linux` — `_parse_build_settings()` defaults are acceptable when keys absent from CMake

**Not on `ProjectSpec`:** `bundleId` is generated at write time (`plugin_settings.bundle_id`); reader never extracts `BUNDLE_ID` from CMake — no change.

### Current `_parse_cmakelists` — The Bug This Story Fixes

```66:80:core/project_reader.py
def _parse_cmakelists(text: str) -> Optional[dict]:
    project = _PROJECT_RE.search(text)
    if not project:
        return None
    values = {
        "projectName": project.group(1),
        "projectVersion": project.group(2),
        "pluginFormats": _read_formats(text),
        "pluginType": _read_type(text),
        "cxxStandard": _read_cxx(text),
        ...
    }
    values.update(_quoted_fields(text))
    return values
```

`_quoted_fields()` only adds keys **when found** — missing `COMPANY_NAME` means `manufacturerName` never enters `values`, and `from_dict` silently uses `""`. **Story 2-2 must reject this before `from_dict`.**

### Suggested Implementation Shape

```python
@dataclass(frozen=True)
class ProjectReadResult:
    spec: Optional[ProjectSpec]
    missing_fields: tuple[str, ...] = ()

def read_project_result(project_dir: Path) -> ProjectReadResult:
    sidecar = project_dir / _SIDECAR
    if sidecar.exists():
        spec = _read_sidecar(sidecar, project_dir)
        return ProjectReadResult(spec=spec)
    return _read_from_cmake_result(project_dir)

def read_project(project_dir: Path) -> Optional[ProjectSpec]:
    return read_project_result(project_dir).spec
```

`_read_from_cmake_result` returns `ProjectReadResult(spec=None, missing_fields=(...))` on failure.

Keep functions ≤ 15 lines (extract `_collect_cmake_values`, `_validate_cmake_values` if needed). `read_project` is orchestration (≤ 3 lines).

### `_read_cxx` Change

Current behaviour defaults to `"C++17"`. For completeness checking:

```python
def _read_cxx(text: str) -> Optional[str]:
    match = _CXX_RE.search(text)
    return f"C++{match.group(1)}" if match else None
```

Caller adds `"C++ Standard"` to missing list when `None`.

### CMake Template Cross-Reference (Generated Output)

Identity fields live in `juce_add_plugin` block in `Templates/CMakeLists.txt`:

```138:157:Templates/CMakeLists.txt
juce_add_plugin({projectName}
    COMPANY_NAME "{manufacturerName}"
    ...
    PLUGIN_MANUFACTURER_CODE "{manufacturerCode}"
    PLUGIN_CODE "{pluginCode}"
    ...
    PLUGIN_NAME "{projectDisplayName}"
    IS_SYNTH {isSynth}
    ...
    IS_MIDI_EFFECT {isMidiEffect}
```

Copy/artefact settings are inline (story 1-4). `_parse_build_settings()` already falls back: `project-configuration.cmake` first, else `CMakeLists.txt` — **preserve this** for pre-1.4 legacy projects.

### `MainWindow._load_project()` — Required UX

Current (story 2-1):

```132:142:app/main_window.py
    def _load_project(self, project_dir: Path) -> None:
        spec = read_project(project_dir)
        if spec is None:
            sidecar = project_dir / ".luthier.json"
            if sidecar.exists():
                message = "Could not read project configuration (.luthier.json is invalid or unreadable)."
            else:
                message = f"Not a JUCE plugin project: {project_dir}"
```

**Required (story 2-2):**

```python
result = read_project_result(project_dir)
if result.spec is None:
    sidecar = project_dir / ".luthier.json"
    if sidecar.exists():
        message = "Could not read project configuration (.luthier.json is invalid or unreadable)."
    elif result.missing_fields:
        bullets = "\n".join(f"• {name}" for name in result.missing_fields)
        message = f"Could not parse project configuration from CMakeLists.txt.\n\nMissing or unreadable fields:\n{bullets}"
    else:
        message = f"Not a JUCE plugin project: {project_dir}"
```

Keep `QMessageBox.critical(self, "Open Project", message)` + `_set_status`. Empty `plugin_formats` check on success path unchanged.

### Architecture Compliance

| AD | Requirement | Story 2-2 action |
|----|-------------|------------------|
| AD-1 | `read_project()` returns `Optional[ProjectSpec]` | Preserve via wrapper |
| AD-3 | Regex fallback when sidecar absent; partial → `None` | **Implement completeness gate** |
| AD-5 | `prefs.update` + `save` on open success | Unchanged |
| AD-7 | `juce_dir` not on `ProjectSpec` | CMake path does not read `JUCE_DIR` — unchanged |
| AD-8 | No Qt in `core/` | `ProjectReadResult` lives in `project_reader.py` |
| NFR3 | Missing field must not corrupt regen | Partial parse blocked at reader |

[Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` §AD-3]

### Clean Code Constraints (NFR1)

- New helpers ≤ 15 lines each; cyclomatic complexity < 5
- `ProjectReadResult` is a frozen dataclass (2 fields) — no behaviour
- No new third-party dependencies
- `_FIELD_LABELS` dict for key → human label mapping (pure data, complexity 1)

### Testing Requirements

Pattern: `unittest` (Epic 3 migrates to pytest). No Qt in tests.

Run: `.venv/bin/python -m unittest tests.test_story_2_2 -v`  
Full suite: `.venv/bin/python -m unittest discover -s tests -v`

**Round-trip test (AC2 via cmake path):** Delete `.luthier.json` after generate; `read_project_result` must return full spec; regenerate must match byte-for-byte (same caveats as 2-1: `juce_dir=""`, no template overrides).

**Partial parse test:** After generate, read `CMakeLists.txt`, remove one `COMPANY_NAME` line, write back, assert `missing_fields` contains `"Company Name"` and `spec is None`.

### Previous Story Intelligence (Story 2-1)

**Established patterns to reuse:**
- `_read_sidecar` / `_read_from_cmake` split — only refine `_read_from_cmake` + `_parse_cmakelists`
- `destinationDir = str(project_dir.parent)` override after deserialise — keep in cmake path
- `UnicodeDecodeError` caught in sidecar read — mirror `OSError` on cmake `read_text`
- `tests/test_story_2_1.py` helpers: `_make_spec()`, `_all_files()`, `_write_project()` pattern
- `MainWindow` dual feedback: `QMessageBox` + status label

**Review deferrals from 2-1 (do not fix unless blocking):**
- `from_dict` without try/except on sidecar — pre-existing
- Non-string values in sidecar JSON — writer always emits strings

**Story 2-1 explicitly deferred to 2-2:**
- CMake regex refinement + missing-field error messages
- Partial CMake parse returning `None` with distinguishable UI

### Git Intelligence

Story 2-1 changes are in working tree (not yet in `baseline_commit` on main). Recent committed history is Epic 1. Relevant for cmake reader:

| Commit / change | Relevance |
|-----------------|-----------|
| Story 2-1 (uncommitted) | Sidecar-first routing; cmake path untouched internally |
| `c58a341` CMakeLists consolidation (1-4) | Copy config inline; `_parse_build_settings` dual-source |
| `c3bb7bf` ProjectSpec end-to-end (1-3) | `_load_project()` uses `ProjectSpec` |
| `659520f` juce_dir in prefs (1-6) | Round-trip cmake path may diff on `JUCE_DIR` line if prefs differ — document, don't fix |

### Latest Technical Information

- **Python `re` module** (stdlib): current regexes in `project_reader.py` are sufficient; no library upgrade needed.
- **`dataclasses.dataclass(frozen=True)`** (stdlib): appropriate for `ProjectReadResult`.
- No web research required — no external API or framework version dependency for this story.

### Project Structure Notes

- `project_reader.py` remains the **sole** deserialiser of project config (sidecar + cmake)
- Tests at `tests/test_story_2_2.py` (flat layout, consistent with 2-1)
- Epic 3 story 3-4 will add integration test deleting sidecar — this story's unit tests front-run that AC

### Story 3.4 Boundary (Downstream)

Story 3-4 (`tests/integration/test_round_trip.py`) will formalise: delete `.luthier.json` → cmake fallback → complete spec or `None`. Implement correctness here; Epic 3 adds pytest infrastructure.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` §Story 2.2]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` §AD-3]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-explained.md` §Decision 3]
- [Source: `_bmad-output/implementation-artifacts/2-1-project-reload-via-luthier-json-sidecar.md` — sidecar path + 2-2 boundary]
- [Source: `_bmad-output/implementation-artifacts/1-4-cmakelists-txt-template-consolidation.md` — `_parse_build_settings` legacy compat]
- [Source: `_bmad-output/project-context.md` §Round-Trip, §Known Issues #2]
- [Source: `core/project_reader.py`, `app/main_window.py`, `Templates/CMakeLists.txt`]

## Dev Agent Record

### Agent Model Used

Claude (Cursor Agent)

### Debug Log References

### Completion Notes List

- Added `ProjectReadResult` and `read_project_result()`; `read_project()` is now a thin wrapper preserving AD-1.
- CMake parse path validates 11 required fields plus `IS_SYNTH`; partial parses return `None` with human-readable `missing_fields` (AD-3).
- `_read_cxx()` no longer defaults to `C++17` when `CMAKE_CXX_STANDARD` is absent.
- `MainWindow._load_project()` shows CMake-specific error dialog listing missing fields; sidecar error message unchanged.
- Five tests in `tests/test_story_2_2.py`; full suite 20/20 green.

### File List

- `core/project_reader.py` — modified
- `app/main_window.py` — modified
- `tests/test_story_2_2.py` — new

### Change Log

- 2026-06-23: Story 2-2 implemented — CMake completeness gate, `ProjectReadResult` API, UI missing-field diagnostics, tests.

### Review Findings

- [x] [Review][Patch] Message multiligne dans la barre de statut [`app/main_window.py:148`]

- [x] [Review][Defer] Échec sidecar sans raison structurée [`core/project_reader.py:74-75`] — deferred, pré-existant (story 2-1, hors périmètre 2-2)
- [x] [Review][Defer] Chemin sidecar sans gate de complétude [`core/project_reader.py:83-91`] — deferred, hors périmètre explicite de la story
- [x] [Review][Defer] Validation `pluginFormats` divergente sidecar vs CMake [`app/main_window.py:150-154`] — deferred, chemin sidecar = story 2-1
- [x] [Review][Defer] `project()` absent → diagnostics vides, message générique [`core/project_reader.py:116-117`] — deferred, gap UX mineur / test gap AC4
- [x] [Review][Defer] `OSError`/`UnicodeDecodeError` non capturés dans `_parse_build_settings` [`core/project_reader.py:199`] — deferred, pré-existant (review 1-4)
- [x] [Review][Defer] `OSError` sur lecture CMake classé « not a JUCE project » [`core/project_reader.py:104-105`] — deferred, cas limite rare
- [x] [Review][Defer] `UnicodeDecodeError` non capturé sur lecture CMake [`core/project_reader.py:103`] — deferred, durcissement optionnel
- [x] [Review][Defer] `ProjectReadResult` sans enum de type d'erreur [`core/project_reader.py:66-69`] — deferred, amélioration design hors scope
- [x] [Review][Defer] Regex `_quoted_fields` plus faible que `_SET_RE` [`core/project_reader.py:172`] — deferred, pré-existant
- [x] [Review][Defer] Tests manquants : `IS_SYNTH` absent, `CMAKE_CXX_STANDARD` absent [`tests/test_story_2_2.py`] — deferred, gap couverture non bloquant
- [x] [Review][Defer] Tests manquants : chemin UI `MainWindow._load_project()` [`tests/test_story_2_2.py`] — deferred, AC4 core-only testé
- [x] [Review][Defer] Tests manquants : échec multi-champs, chemin générique CMake malformé [`tests/test_story_2_2.py`] — deferred, gap couverture
