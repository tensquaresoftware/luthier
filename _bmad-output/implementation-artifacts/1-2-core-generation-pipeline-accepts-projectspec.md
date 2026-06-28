---
baseline_commit: 2e80b69
---

# Story 1.2: Core Generation Pipeline Accepts ProjectSpec

Status: done

## Change Log

- 2026-06-23: Implemented story 1-2 — `generate(spec)`, `build_context(spec)`, `build_tokens(spec)`, `read_project() → Optional[ProjectSpec]`; atomic write + `.luthier.json` sidecar in `ProjectWriter`; 11 tests added

## Story

As a JUCE developer,
I want the generation engine to accept a typed `ProjectSpec`,
so that project data flows through the system without silent key errors or missing fields.

## Acceptance Criteria

1. `ProjectGenerator.generate(spec)` accepts a `ProjectSpec` directly; `render_context.build_context(spec)` receives the spec — no raw dict is assembled by the caller.
2. `ProjectWriter.write()` writes all files to a sibling temp directory (`<dest>.tmp/`) first, then atomically renames it to `dest`, replacing any existing directory.
3. If generation fails mid-write (exception raised), the temp directory is cleaned up and the original `dest` is left untouched.
4. On successful generation, a `.luthier.json` file is present at the root of `dest`, containing the full `ProjectSpec` serialized as UTF-8 JSON (`json.dumps(spec.to_dict(), indent=2, ensure_ascii=False)`).
5. `project_reader.read_project()` returns `Optional[ProjectSpec]` (not `Optional[dict]`); when all required fields are extracted from `CMakeLists.txt`, it wraps the result in `ProjectSpec.from_dict()`.
6. Importing `core/project_generator.py`, `core/project_writer.py`, and `core/project_reader.py` in a test triggers no Qt module import (AD-8).

## Tasks / Subtasks

- [x] Update `core/render_context.py` to accept `ProjectSpec` (AC: 1, 6)
  - [x] Add `from core.project_spec import ProjectSpec`
  - [x] Change `build_context(values: dict, config: dict)` → `build_context(spec: ProjectSpec) -> dict`; add `d = spec.to_dict()` as first line; pass `d` to all internal helpers (no other changes)
  - [x] Change `build_tokens(values: dict)` → `build_tokens(spec: ProjectSpec) -> dict`; access `spec.project_name` and `spec.project_display_name` directly
- [x] Update `core/project_generator.py` to pass `ProjectSpec` through (AC: 1, 6)
  - [x] Add `from core.project_spec import ProjectSpec`
  - [x] Change `generate(self, values: dict, config: dict)` → `generate(self, spec: ProjectSpec) -> Path`
  - [x] Replace `Path(values["destinationDir"]) / values["projectName"]` with `Path(spec.destination_dir) / spec.project_name`
  - [x] Replace `render_context.build_context(values, config)` with `render_context.build_context(spec)`
  - [x] Replace `render_context.build_tokens(values)` with `render_context.build_tokens(spec)`
  - [x] Change `ProjectWriter(...).write(context, tokens)` → `.write(context, tokens, spec)`
- [x] Update `core/project_writer.py` — atomic write + sidecar (AC: 2, 3, 4, 6)
  - [x] Add `import json` to imports
  - [x] Add `from core.project_spec import ProjectSpec`
  - [x] Change `write(self, context: dict, tokens: dict)` → `write(self, context: dict, tokens: dict, spec: ProjectSpec) -> None`
  - [x] Implement atomic write in `write()`: compute `tmp = self._project.parent / (self._project.name + ".tmp")`, rmtree tmp if exists, wrap `_write_all` + `_write_sidecar` in try/except (rmtree tmp on failure, re-raise), rmtree `self._project` if exists, rename tmp → `self._project`
  - [x] Extract `_write_all(self, dest: Path, context: dict, tokens: dict) -> None`: three loops (RENDERED, TOKENIZED, VERBATIM) calling `_write_file(dest, relative, content)`
  - [x] Add `_write_sidecar(self, dest: Path, spec: ProjectSpec) -> None`: write `.luthier.json` to dest
  - [x] Rename `_write(self, relative, content)` → `_write_file(self, root: Path, relative: str, content: str) -> None`; replace `self._project` with `root`
  - [x] Remove `_reset_project_dir()` entirely
- [x] Update `core/project_reader.py` to return `Optional[ProjectSpec]` (AC: 5, 6)
  - [x] Add `from core.project_spec import ProjectSpec`
  - [x] Change `read_project(project_dir: Path) -> Optional[dict]` → `-> Optional[ProjectSpec]`
  - [x] Replace `return values` with `return ProjectSpec.from_dict(values)` (last line of `read_project`)
  - [x] Do NOT change any internal parsing logic (`_parse_cmakelists`, `_parse_build_settings`, etc.)

### Review Findings

- [x] [Review][Patch] `rmtree` in cleanup `except` can raise and replace original exception [core/project_writer.py:55-56]
- [x] [Review][Defer] Existing project deleted before rename; if `tmp.rename()` fails, project is permanently lost [core/project_writer.py:52-53] — deferred, low-risk (sibling design ensures same filesystem)
- [x] [Review][Defer] `TestNoQtImport` ordering dependency — prior imports in same process mask Qt leaks [tests/test_story_1_2.py] — deferred, low-risk given test structure
- [x] [Review][Defer] `KeyboardInterrupt`/`SystemExit` not caught by `except Exception`; `.tmp` left on disk [core/project_writer.py:44-57] — deferred, mitigated by upfront cleanup on next write
- [x] [Review][Defer] Unknown `plugin_type` crashes with `KeyError` in `flags_for_type` [core/render_context.py] — deferred, pre-existing
- [x] [Review][Defer] Unguarded file reads in `read_project` raise instead of returning `None` [core/project_reader.py:34-43] — deferred, pre-existing, unchanged
- [x] [Review][Defer] Bool coercion in `ProjectSpec.from_dict` accepts non-bool values silently [core/project_spec.py] — deferred, pre-existing from story 1.1

## Dev Notes

### What This Story Changes and What It Does Not

**Story scope — 4 core files only:**

| File | Change |
|------|--------|
| `core/render_context.py` | Signature change: `build_context(spec)`, `build_tokens(spec)` |
| `core/project_generator.py` | Signature change: `generate(spec)` |
| `core/project_writer.py` | Atomic write + `.luthier.json` sidecar + rename `_write` → `_write_file` |
| `core/project_reader.py` | Return type `Optional[dict]` → `Optional[ProjectSpec]` |

**Do NOT touch in this story:**
- `app/main_window.py` — still calls `generate(values, config)` and uses reader result as dict (story 1.3)
- `app/pages/project.py` — still exposes `values()` + `config()` separately (story 1.3)
- `core/project_spec.py` — done in story 1.1, no changes
- `core/rendering.py`, `core/plugin_settings.py`, `core/preferences.py`, `core/templates_store.py` — untouched
- `Templates/` — untouched; `project-configuration.cmake` template is NOT removed here (story 1.4)

**Intentional temporary regression:** After this story, clicking "Generate Project" or "Open Project…" in the app will fail at runtime because `main_window.py` still calls `generate(values, config)` (wrong signature) and treats `read_project()` result as a dict. This is expected — story 1.3 fixes the app layer. Do not add compatibility shims.

### Current State of Files Being Modified

**`core/render_context.py`** — `build_context(values: dict, config: dict)` extracts from two separate dicts. `_copy_config(config)` accesses `config["copyToSystemFolders"]`, etc. `_extra_fields(values)` accesses `values.get("cxxStandard", ...)`, etc. All internal helpers take `dict` with camelCase keys. **Key insight:** `spec.to_dict()` produces a single camelCase dict containing every key both `values` and `config` had — pass this dict `d` to all internal helpers unchanged.

**`core/project_generator.py`** — `generate(values, config)` builds project_dir from dict keys, calls `build_context(values, config)`, `build_tokens(values)`, then `writer.write(context, tokens)`. 44 lines total.

**`core/project_writer.py`** — `write(context, tokens)` calls `_reset_project_dir()` (shutil.rmtree + nothing), then iterates three tuples writing files. `_write(relative, content)` computes `self._project / relative`. No error handling on write failure.

**`core/project_reader.py`** — `read_project()` returns `Optional[dict]` built from regex parse + build settings. The dict has the same camelCase keys as `ProjectSpec.to_dict()` so `ProjectSpec.from_dict(values)` will work directly.

### `render_context.py` — Exact Change Pattern

```python
# BEFORE
def build_context(values: dict, config: dict) -> dict:
    flags = plugin_settings.flags_for_type(values["pluginType"])
    context = {key: values[key] for key in _VALUE_KEYS}
    ...
    context.update(_copy_config(config))
    context["bundleId"] = plugin_settings.bundle_id(values["manufacturerName"], values["projectName"])
    context.update(_extra_fields(values))
    return context

def build_tokens(values: dict) -> dict:
    return {"PROJECT_NAME": values["projectName"], "PROJECT_DISPLAY_NAME": values["projectDisplayName"]}

# AFTER
def build_context(spec: ProjectSpec) -> dict:
    d = spec.to_dict()
    flags = plugin_settings.flags_for_type(d["pluginType"])
    context = {key: d[key] for key in _VALUE_KEYS}
    ...
    context.update(_copy_config(d))    # was config, now same camelCase dict
    context["bundleId"] = plugin_settings.bundle_id(d["manufacturerName"], d["projectName"])
    context.update(_extra_fields(d))   # internal helpers unchanged
    return context

def build_tokens(spec: ProjectSpec) -> dict:
    return {"PROJECT_NAME": spec.project_name, "PROJECT_DISPLAY_NAME": spec.project_display_name}
```

Internal helpers `_categories`, `_copy_config`, `_extra_fields`, `_include_block`, `_definitions_block`, `_cmake_block`, `_non_empty_lines` — **all unchanged**.

### `project_writer.py` — Full New Structure

```python
import json
import shutil
from pathlib import Path
from typing import Optional

from core import rendering
from core.project_spec import ProjectSpec

# _RENDERED, _TOKENIZED, _VERBATIM tuples unchanged

class ProjectWriter:
    def __init__(self, templates_dir: Path, project_dir: Path, overrides: Optional[Path] = None):
        # unchanged

    def write(self, context: dict, tokens: dict, spec: ProjectSpec) -> None:
        tmp = self._project.parent / (self._project.name + ".tmp")
        if tmp.exists():
            shutil.rmtree(tmp)
        try:
            self._write_all(tmp, context, tokens)
            self._write_sidecar(tmp, spec)
            if self._project.exists():
                shutil.rmtree(self._project)
            tmp.rename(self._project)
        except Exception:
            if tmp.exists():
                shutil.rmtree(tmp)
            raise

    def _write_all(self, dest: Path, context: dict, tokens: dict) -> None:
        for relative in _RENDERED:
            self._write_file(dest, relative, rendering.render(self._read(relative), context))
        for relative in _TOKENIZED:
            self._write_file(dest, relative, rendering.render_tokens(self._read(relative), tokens))
        for relative in _VERBATIM:
            self._write_file(dest, relative, self._read(relative))

    def _write_sidecar(self, dest: Path, spec: ProjectSpec) -> None:
        (dest / ".luthier.json").write_text(
            json.dumps(spec.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _read(self, relative: str) -> str:  # unchanged
        source = self._override_for(relative) or self._templates / relative
        return source.read_text(encoding="utf-8")

    def _override_for(self, relative: str) -> Optional[Path]:  # unchanged
        if not self._overrides or relative not in _TOKENIZED:
            return None
        candidate = self._overrides / Path(relative).name
        return candidate if candidate.exists() else None

    def _write_file(self, root: Path, relative: str, content: str) -> None:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
```

**Clean code metrics check (mandatory):**
- `write()`: 14 lines (within 15-line limit), complexity ≈ 4 (within < 5), indentation ≤ 2
- `_write_all()`: 7 lines, complexity 1, indentation 2
- `_write_sidecar()`: 4 lines, complexity 1, indentation 1
- All methods: ≤ 3 non-self parameters (at the 3-param limit)
- Class total: ~65 lines (within 200)

### `project_reader.py` — Only One Line Changes

```python
# Add import at top:
from core.project_spec import ProjectSpec

# Change function signature:
def read_project(project_dir: Path) -> Optional[ProjectSpec]:

# Change last line of read_project (was: return values):
    return ProjectSpec.from_dict(values)
```

All other code in `project_reader.py` is unchanged. `_parse_cmakelists()`, `_parse_build_settings()`, and all helpers remain returning `dict` — these are private, no layer boundary crossed.

### `project_reader.py` — Field Coverage Verification

`ProjectSpec.from_dict()` uses `.get(key, default)` for every field, so partial dicts never raise. The merged `values` dict from `read_project()` covers all 20 ProjectSpec fields via camelCase keys:

| ProjectSpec field | Source in reader |
|---|---|
| `projectName`, `projectVersion` | `_PROJECT_RE` |
| `projectDisplayName`, `manufacturerName`, `manufacturerCode`, `pluginCode`, `companyCopyright`, `companyWebsite`, `companyEmail` | `_quoted_fields()` |
| `pluginFormats` | `_read_formats()` |
| `pluginType` | `_read_type()` |
| `cxxStandard` | `_read_cxx()` |
| `headerSearchPaths` | `_read_header_paths()` |
| `preprocessorDefinitions` | `_read_preproc()` |
| `destinationDir` | `str(project_dir.parent)` |
| `copyToSystemFolders`, `copyToArtefactsDir`, `artefactsDirWindows/Macos/Linux` | `_parse_build_settings()` |

### Atomic Write Semantics (AD-4)

- Temp dir name: `<project_name>.tmp` as sibling of the project dir (same filesystem → rename is atomic on POSIX)
- If a previous `.tmp` exists (leftover from a crashed run), it is removed before starting
- Failure path: exception propagates to `MainWindow` (the single catch boundary per architecture)
- The existing `MainWindow._confirm_overwrite()` guard is unaffected — it runs before `generate()` is called
- `project-configuration.cmake` is still in `_RENDERED` and still written — story 1.4 removes it

### Architecture Rules Enforced

| Rule | How enforced here |
|------|------------------|
| AD-1: no raw dict across layer boundary | `generate(spec)`, `build_context(spec)`, `read_project() → ProjectSpec` |
| AD-3: writer writes `.luthier.json` | `_write_sidecar()` in `ProjectWriter` |
| AD-4: atomic write | temp dir + rename in `write()` |
| AD-8: no Qt in core | All 4 files import only stdlib + `core.*` |
| AD-9: overrides at write time | `_override_for()` logic unchanged |

### Previous Story Intelligence (1.1)

- `ProjectSpec` is in `core/project_spec.py`, 72 lines, `@dataclass` with 20 fields
- `to_dict()` → camelCase keys (matches existing template placeholder names)
- `from_dict(d)` → uses `.get(key, default)` for every field — safe with partial dicts
- Review finding from 1.1: bool coercion in `from_dict` is permissive (deferred); `_parse_build_settings()._bool()` already returns proper Python bools → no issue here
- No `__post_init__` validation in `ProjectSpec` — it's a pure container

### Git Context (Last 5 Commits)

- `2e80b69` — Add ProjectSpec dataclass (story 1-1, done): created `core/project_spec.py`, established camelCase ↔ snake_case convention, confirmed zero Qt deps
- `7d24b75` — Add project documentation artifacts: BMad planning documents
- `087ea5d` — Fix processBlock parameter rename: `render_context._extra_fields` was changed; confirms this file was recently edited and has the current function names

### Project Structure Notes

- New imports in core files: `from core.project_spec import ProjectSpec` — absolute import, works when running from project root
- No new files created in this story
- `_RENDERED` tuple still includes `"project-configuration.cmake"` — do NOT remove (story 1.4)
- `.luthier.json` is a generated file (not a template), written directly by `_write_sidecar()` — no corresponding entry in `Templates/`

### References

- AD-1, AD-2, AD-3, AD-4, AD-8, AD-9: [_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md)
- Story 1.2 AC source: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md) §Story 1.2
- Clean code limits: [_bmad-output/project-context.md](_bmad-output/project-context.md) §Critical Implementation Rules
- `ProjectSpec.to_dict()` / `from_dict()` contract: [core/project_spec.py](core/project_spec.py)
- Files being modified: [core/project_generator.py](core/project_generator.py), [core/project_writer.py](core/project_writer.py), [core/render_context.py](core/render_context.py), [core/project_reader.py](core/project_reader.py)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented all 4 signature changes: `build_context(spec)`, `build_tokens(spec)`, `generate(spec)`, `read_project() → Optional[ProjectSpec]`
- `ProjectWriter.write()` now performs atomic write via `.tmp` sibling dir + rename; cleans up on failure
- `_write_sidecar()` writes `.luthier.json` (full spec as UTF-8 JSON) into the temp dir before rename
- `_reset_project_dir()` removed; `_write()` renamed to `_write_file(root, relative, content)`
- All internal helpers in `render_context.py` and `project_reader.py` unchanged (private, no boundary crossed)
- 11 tests added in `tests/test_story_1_2.py` covering all 6 ACs; all pass
- Intentional temporary regression: `main_window.py` still calls old signature — will be fixed in story 1.3
- Discovered: `ProjectSpec.plugin_type` default is `"Instrument"` but valid runtime values are `"synth"/"effect"/"midi"` — noted for story 1.3

### File List

- `core/render_context.py`
- `core/project_generator.py`
- `core/project_writer.py`
- `core/project_reader.py`
- `tests/__init__.py`
- `tests/test_story_1_2.py`
