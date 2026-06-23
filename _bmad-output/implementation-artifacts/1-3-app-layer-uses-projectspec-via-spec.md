---
baseline_commit: 425fe3e
---

# Story 1.3: App Layer Uses ProjectSpec via spec()

Status: done

## Story

As a JUCE developer,
I want the UI to assemble a typed `ProjectSpec` when I trigger generation or open a project,
so that there is a single, complete data object passed to the engine with no partial dict assembly.

## Acceptance Criteria

1. `ProjectPage.spec()` returns a `ProjectSpec` carrying both identity fields and artefact config fields — replacing the former `values()` + `config()` split.
2. `MainWindow._on_generate()` calls `project_page.spec()` and passes the result directly to `ProjectGenerator.generate(spec)` — no intermediate dict is assembled in `MainWindow`.
3. After successful generation, `prefs.update(spec)` is called immediately followed by `prefs.save()` — in that order, in `MainWindow` only (AD-5).
4. After successful open via "Open Project…", `prefs.update(spec)` followed by `prefs.save()` is called — same pattern as generation (AD-5).

## Tasks / Subtasks

- [x] Update `core/preferences.py` — change `update()` to accept `ProjectSpec` (AC: 3, 4)
  - [x] Add `from core.project_spec import ProjectSpec` to imports
  - [x] Change `update(self, values: dict)` → `update(self, spec: ProjectSpec)`: explicit mapping from spec snake_case fields to prefs camelCase keys (see Dev Notes for exact mapping)
  - [x] Verify: `juceDir` is NOT updated (no field on `ProjectSpec` per AD-7)
- [x] Add `spec()` to `app/pages/project.py` (AC: 1)
  - [x] Add `from core.project_spec import ProjectSpec` to imports
  - [x] Add `spec(self) -> ProjectSpec`: assemble `d` from `_info.values()` + pluginType + pluginFormats + compilation + artefacts; return `ProjectSpec.from_dict(d)` (see Dev Notes for exact implementation)
  - [x] Change `load(self, values: dict)` → `load(self, spec: ProjectSpec)`: `d = spec.to_dict()` then pass `d` to child pages; use `spec.plugin_type` for `_type.set_type()` and `spec.plugin_formats` for `_formats.set_formats()`
- [x] Update `app/main_window.py` (AC: 2, 3, 4)
  - [x] Add `from core.project_spec import ProjectSpec` to imports
  - [x] Change `_on_generate()`: get `spec = self._project_page.spec()`, pass to `_confirm_overwrite(spec)` and `_run_generation(spec)`
  - [x] Change `_confirm_overwrite(self, values: dict)` → `_confirm_overwrite(self, spec: ProjectSpec)`: use `spec.destination_dir` and `spec.project_name` instead of dict keys
  - [x] Change `_run_generation(self, values: dict)` → `_run_generation(self, spec: ProjectSpec)`: call `self._generator.generate(spec)` (no `config()` argument); on success, call `self._prefs.update(spec)` then `self._prefs.save()` before `_set_status`
  - [x] Change `_load_project()`: rename `values` → `spec`, call `self._project_page.load(spec)`, `self._prefs.update(spec)`, `self._prefs.save()`; access `spec.project_name` (not `values['projectName']`)

## Dev Notes

### Scope — 3 files only

| File | Change |
|------|--------|
| `core/preferences.py` | `update(spec: ProjectSpec)` signature + explicit field mapping |
| `app/pages/project.py` | add `spec() -> ProjectSpec`; change `load(spec: ProjectSpec)` |
| `app/main_window.py` | use `spec()` throughout; add `prefs.update(spec)` + `prefs.save()` on generate/open success |

**Do NOT touch in this story:**
- `app/pages/project_info.py`, `artefacts.py`, `compilation.py`, `plugin_type.py`, `formats.py` — child pages still take `dict` internally; `spec.to_dict()` bridges the gap
- `core/project_generator.py`, `core/project_writer.py`, `core/render_context.py`, `core/project_reader.py` — already updated in stories 1.1 and 1.2
- `core/project_spec.py` — no changes
- Any other file not listed above

### Current State of Files Being Modified

**`app/pages/project.py`** — `values()` builds a camelCase dict from child pages; `config()` delegates to `self._artefacts.values()`. Both are used only by `MainWindow`. `load(values: dict)` dispatches to each child page's `load()`. Imports: no `core.project_spec` yet.

**`app/main_window.py`** — `_on_generate()` calls `values()` + `config()` then passes raw dict to `generate(values, config)` (wrong signature as of story 1.2). `_load_project()` assigns `read_project()` result to `values` and accesses it as a dict (`values['projectName']`) — this crashes at runtime since story 1.2 changed `read_project()` to return `Optional[ProjectSpec]`. `_confirm_overwrite()` and `_run_generation()` also take the old values dict.

**`core/preferences.py`** — `update(self, values: dict)` filters by `_DEFAULTS` keys. Problem: the old dict from `read_project()` used keys like `manufacturerName` but prefs uses `manufacturer` — so the mapping was silently wrong. Story 1.3 makes the mapping explicit. `preferences.py` already imports `from PySide6.QtCore import QStandardPaths` (pre-existing; not an AD-8 violation — AD-8 bans `core/ → app/` imports, not Qt imports).

### `Preferences.update()` — Exact Implementation

```python
from core.project_spec import ProjectSpec   # add to existing imports

def update(self, spec: ProjectSpec) -> None:
    self._data.update({
        "manufacturer": spec.manufacturer_name,
        "manufacturerCode": spec.manufacturer_code,
        "pluginCode": spec.plugin_code,
        "destination": spec.destination_dir,
        "companyCopyright": spec.company_copyright,
        "companyWebsite": spec.company_website,
        "companyEmail": spec.company_email,
        "artefactsDirWindows": spec.artefacts_dir_windows,
        "artefactsDirMacos": spec.artefacts_dir_macos,
        "artefactsDirLinux": spec.artefacts_dir_linux,
        "copyToSystemFolders": spec.copy_to_system_folders,
        "copyToArtefactsDir": spec.copy_to_artefacts_dir,
    })
```

Key: `juceDir` is NOT in the mapping (AD-7: `juce_dir` is not on `ProjectSpec`). The old dict-filter approach was silently no-oping on most keys due to camelCase mismatch — this explicit mapping fixes it correctly.

Clean code: 14 lines, complexity 1. Accepted as pure data (same precedent as `_field_specs` in project_info.py).

### `ProjectPage.spec()` — Exact Implementation

```python
from core.project_spec import ProjectSpec   # add to existing imports

def spec(self) -> ProjectSpec:
    d = dict(self._info.values())
    d["pluginType"] = self._type.selected_type()
    d["pluginFormats"] = self._formats.value()
    d.update(self._compilation.values())
    d.update(self._artefacts.values())
    return ProjectSpec.from_dict(d)
```

Keys produced by each child:
- `_info.values()`: `projectName`, `projectDisplayName`, `projectVersion`, `manufacturerName`, `companyCopyright`, `companyWebsite`, `companyEmail`, `manufacturerCode`, `pluginCode`, `destinationDir` (note: `_info.values()` applies the display name fallback: if `projectDisplayName` is blank, it is set to `projectName`)
- `_type.selected_type()`: string `"synth"`, `"effect"`, or `"midi"` (runtime values from `PluginTypePage` — note: default on `ProjectSpec` is `"Instrument"` but live app values are lowercased)
- `_formats.value()`: space-separated string
- `_compilation.values()`: `cxxStandard`, `preprocessorDefinitions`, `headerSearchPaths`
- `_artefacts.values()`: `copyToSystemFolders`, `copyToArtefactsDir`, `artefactsDirWindows`, `artefactsDirMacos`, `artefactsDirLinux`

`ProjectSpec.from_dict(d)` uses `.get(key, default)` for every field — safe with the assembled dict.

### `ProjectPage.load()` — Exact Implementation

```python
def load(self, spec: ProjectSpec) -> None:
    d = spec.to_dict()
    self._info.load(d)
    self._type.set_type(spec.plugin_type)
    self._formats.set_formats(spec.plugin_formats)
    self._compilation.load(d)
    self._artefacts.load(d)
```

Child pages that take a dict (`_info`, `_compilation`, `_artefacts`) receive `spec.to_dict()` unchanged — no modification to those pages. `_type.set_type()` and `_formats.set_formats()` still use their existing str arguments.

### `MainWindow` — Exact Implementation

**`_on_generate()`:**
```python
def _on_generate(self) -> None:
    spec = self._project_page.spec()
    if not self._confirm_overwrite(spec):
        return
    self._run_generation(spec)
```

**`_confirm_overwrite()`:**
```python
def _confirm_overwrite(self, spec: ProjectSpec) -> bool:
    if not self._generator.project_exists(spec.destination_dir, spec.project_name):
        return True
    answer = QMessageBox.question(
        self,
        "Overwrite project",
        f"A folder named '{spec.project_name}' already exists. Overwrite it?",
    )
    return answer == QMessageBox.Yes
```

**`_run_generation()`:**
```python
def _run_generation(self, spec: ProjectSpec) -> None:
    try:
        project_dir = self._generator.generate(spec)
    except Exception as error:
        self._set_status(f"Generation failed: {error}", ok=False)
        return
    self._prefs.update(spec)
    self._prefs.save()
    self._set_status(f"Project generated at {project_dir}", ok=True)
```

**`_load_project()`:**
```python
def _load_project(self, project_dir: Path) -> None:
    spec = read_project(project_dir)
    if spec is None:
        self._set_status(f"Not a JUCE plugin project: {project_dir}", ok=False)
        return
    self._project_page.load(spec)
    self._prefs.update(spec)
    self._prefs.save()
    self._set_status(f"Loaded {spec.project_name} from {project_dir}", ok=True)
```

### Tests

No new tests in this story. All changes are in `app/` (Qt-dependent widgets, no AD-6 Qt tests) or in `core/preferences.py` which already imports Qt at module level (pre-existing). Verification is manual: run the app (`/.venv/bin/python main.py`), generate a project, open it.

The existing `tests/test_story_1_2.py::TestNoQtImport` continues to pass — story 1.3 touches no `core/` import chains that tests check.

### Architecture Rules Enforced

| Rule | How enforced here |
|------|-----------------|
| AD-1: no raw dict across layer boundary | `ProjectPage.spec()` replaces `values()` + `config()` split; `load(spec)` takes ProjectSpec |
| AD-2: single data model | `ProjectSpec` now carries both identity and artefact config; split API removed from the call path |
| AD-5: prefs save-on-update in MainWindow only | `_run_generation()` and `_load_project()` both call `update(spec)` + `save()` in sequence |
| AD-7: juce_dir not on ProjectSpec | Not in `Preferences.update()` mapping; never read from spec |
| AD-8: core/ never imports app/ | `core/preferences.py` imports `ProjectSpec` from `core.project_spec` — same layer, not a violation |

### Previous Story Intelligence

From story 1.2 completion notes:
- "Intentional temporary regression: `main_window.py` still calls `generate(values, config)` (wrong signature)" — this is exactly what story 1.3 fixes
- "`read_project()` returns `Optional[ProjectSpec]` but `_load_project()` treats result as dict" — also fixed here
- "Discovered: `ProjectSpec.plugin_type` default is `"Instrument"` but valid runtime values are `"synth"/"effect"/"midi"`" — important: `spec()` assembles from `_type.selected_type()` which returns the live app value; `from_dict()` stores whatever string is passed. The render_context uses the string via `plugin_settings.flags_for_type()` which must handle these values — do NOT change pluginType casing

From story 1.1:
- `ProjectSpec.from_dict(d)` uses `.get(key, default)` for every field — safe with partial dicts

### Project Structure Notes

- `app/pages/project.py`: add import `from core.project_spec import ProjectSpec`; add `spec()` method; change `load()` signature
- `app/main_window.py`: add import `from core.project_spec import ProjectSpec`; update 4 methods; remove unused `values`/`config` calls
- `core/preferences.py`: add import `from core.project_spec import ProjectSpec`; change `update()` signature
- No new files

### References

- AD-1, AD-2, AD-5, AD-7, AD-8: [_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md)
- Story 1.3 ACs: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md) §Story 1.3
- Current state of files: [app/main_window.py](app/main_window.py), [app/pages/project.py](app/pages/project.py), [core/preferences.py](core/preferences.py)
- Child page value keys: [app/pages/project_info.py](app/pages/project_info.py), [app/pages/compilation.py](app/pages/compilation.py), [app/pages/artefacts.py](app/pages/artefacts.py)
- Clean code limits: [_bmad-output/project-context.md](_bmad-output/project-context.md) §Critical Implementation Rules

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- AC-1: `ProjectPage.spec()` added — assembles `ProjectSpec` from all child pages via `from_dict()`.
- AC-1: `ProjectPage.load()` now accepts `ProjectSpec`; bridges to child dict-based APIs via `spec.to_dict()`.
- AC-2: `MainWindow._on_generate()` calls `spec()` and passes `ProjectSpec` to `_confirm_overwrite` + `_run_generation`; no intermediate dict.
- AC-3: `_run_generation()` calls `prefs.update(spec)` then `prefs.save()` on success.
- AC-4: `_load_project()` calls `prefs.update(spec)` then `prefs.save()` after loading.
- AD-7 enforced: `juceDir` absent from `Preferences.update()` mapping.
- AD-8 enforced: `core/preferences.py` imports from `core.project_spec` (same layer).
- Regression: `TestNoQtImport` still passes — no Qt import leaked into core.
- Headless check: `main.py --check` returns `error: None`.
- Intentional: `values()` and `config()` kept on `ProjectPage` (not called by MainWindow anymore, but removal is not in story scope).

### File List

- `core/preferences.py`
- `app/pages/project.py`
- `app/main_window.py`

### Review Findings

- [x] [Review][Decision] Empty `plugin_formats` after `ProjectPage.load()` silently invalidates form — resolved: added `if not spec.plugin_formats` guard in `_load_project` with explicit error status and early return.
- [x] [Review][Patch] Uncaught `OSError` from `_prefs.save()` after generate and after open [app/main_window.py] — fixed: `_prefs.save()` wrapped in `try/except OSError` in both `_load_project` and `_run_generation`; error shown via `_set_status`.
- [x] [Review][Patch] `Preferences.update()` unconditionally overwrites optional fields with empty strings [core/preferences.py] — fixed: filter added (`isinstance(v, bool) or v`) so only non-empty strings and bools are written; existing prefs preserved when spec field is empty.
- [x] [Review][Defer] Key collision in `spec()` between sections unguarded [app/pages/project.py] — deferred, pre-existing risk
- [x] [Review][Defer] `spec()`/`load()` round-trip symmetry not covered by tests — deferred, pre-existing test gap
- [x] [Review][Defer] `Preferences → ProjectSpec` import coupling direction [core/preferences.py] — deferred, hypothetical circular dependency risk
- [x] [Review][Defer] `Preferences.update()` field list must stay manually in sync with `ProjectSpec` [core/preferences.py] — deferred, intentional design tradeoff per spec

## Change Log

- 2026-06-23: Story 1-3 implemented — app layer now uses `ProjectSpec` end-to-end; `Preferences.update()` accepts `ProjectSpec`; `ProjectPage.spec()` added; `MainWindow` generate/open paths unified around typed spec with explicit `prefs.save()` calls.
