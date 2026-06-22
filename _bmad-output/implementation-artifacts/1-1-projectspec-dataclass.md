---
baseline_commit: 7d24b75d848e7516e6b76466cc30aa4089677deb
---

# Story 1.1: ProjectSpec Dataclass

Status: done

## Story

As a developer (contributor),
I want a typed `ProjectSpec` dataclass as the single data model for all project fields,
so that layer boundaries are explicit and key-mismatch bugs are caught at type-check time rather than silently at runtime.

## Acceptance Criteria

1. `core/project_spec.py` exists with the `ProjectSpec` dataclass; any layer passing project data across a boundary uses a `ProjectSpec` instance — no raw `dict` crosses a layer boundary.
2. `spec.to_dict()` returns a JSON-serializable `dict` preserving all fields with their correct types.
3. `ProjectSpec.from_dict(d)` called on a `dict` produced by `to_dict()` reconstructs an instance equal to the original on all fields.
4. Importing `core/project_spec.py` in a test triggers no Qt module import as a side effect (AD-8).

## Tasks / Subtasks

- [x] Create `core/project_spec.py` (AC: 1, 4)
  - [x] Define `ProjectSpec` as a `@dataclass` with all 20 fields listed in Dev Notes
  - [x] Use Python `snake_case` attribute names with `camelCase` dict keys in serialization
  - [x] No import of any PySide6/Qt module anywhere in the file
- [x] Implement `to_dict(self) -> dict` (AC: 2)
  - [x] Returns a plain `dict` with `camelCase` string keys matching the existing form conventions
  - [x] All values must be JSON-serializable (str/bool — no custom types)
- [x] Implement `from_dict(d: dict) -> "ProjectSpec"` classmethod (AC: 3)
  - [x] Reads the same `camelCase` keys emitted by `to_dict()`
  - [x] Uses `.get(key, default)` for every field so a partial dict never raises `KeyError`
  - [x] Reconstructed instance must compare equal to the original via `==`

### Review Findings

- [x] [Review][Defer] Bool coercion silencieux dans `from_dict` — `d.get("copyToSystemFolders", False)` accepte n'importe quelle valeur truthy/falsy sans conversion ; un appelant futur passant `"ON"` stockerait une string au lieu d'un bool, cassant `_on_off()` dans `render_context.py`. Tous les callers actuels fournissent des bools propres (`project_reader._bool()`, `ProjectPage.config()`). — deferred, pre-existing design decision (`ProjectSpec` est un conteneur sans validation)
- [x] [Review][Defer] Defaults non liés entre champ dataclass et fallback `from_dict` — ex. `copy_to_artefacts_dir: bool = True` et `d.get("copyToArtefactsDir", True)` sont synchronisés manuellement ; un changement de l'un sans l'autre introduira un bug silencieux. — deferred, pre-existing

## Dev Notes

### Field Inventory

`ProjectSpec` carries the union of the current `ProjectPage.values()` dict and `ProjectPage.config()` dict. Every field below maps to a key already used in the existing codebase — do not rename or invent new keys.

| Python attribute | `to_dict()` key | Type | Default |
|---|---|---|---|
| `project_name` | `projectName` | `str` | `""` |
| `project_display_name` | `projectDisplayName` | `str` | `""` |
| `project_version` | `projectVersion` | `str` | `"1.0.0"` |
| `manufacturer_name` | `manufacturerName` | `str` | `""` |
| `manufacturer_code` | `manufacturerCode` | `str` | `""` |
| `plugin_code` | `pluginCode` | `str` | `""` |
| `company_copyright` | `companyCopyright` | `str` | `""` |
| `company_website` | `companyWebsite` | `str` | `""` |
| `company_email` | `companyEmail` | `str` | `""` |
| `destination_dir` | `destinationDir` | `str` | `""` |
| `plugin_type` | `pluginType` | `str` | `"Instrument"` |
| `plugin_formats` | `pluginFormats` | `str` | `""` |
| `cxx_standard` | `cxxStandard` | `str` | `"C++17"` |
| `preprocessor_definitions` | `preprocessorDefinitions` | `str` | `""` |
| `header_search_paths` | `headerSearchPaths` | `str` | `""` |
| `copy_to_system_folders` | `copyToSystemFolders` | `bool` | `False` |
| `copy_to_artefacts_dir` | `copyToArtefactsDir` | `bool` | `True` |
| `artefacts_dir_windows` | `artefactsDirWindows` | `str` | `""` |
| `artefacts_dir_macos` | `artefactsDirMacos` | `str` | `""` |
| `artefacts_dir_linux` | `artefactsDirLinux` | `str` | `""` |

**`plugin_type` valid values:** `"Instrument"`, `"Effect"`, `"MIDI Effect"` — matches `plugin_settings.py` exactly.

**`plugin_formats` format:** space-separated CMake token string, e.g. `"VST3 AU Standalone"` — matches what `FormatsPage.value()` and `project_reader._read_formats()` currently produce.

### Architecture / Constraints

- **File**: `core/project_spec.py` — new file, no existing file to rename.
- **No Qt**: Zero imports from `PySide6` or `PyQt6`. This is `core/` — AD-8 prohibits any `app/` import from `core/`. Qt is only in `app/`.
- **`@dataclass`**: Use `from dataclasses import dataclass`. `@dataclass(eq=True)` (the default) provides `__eq__` automatically — required by AC 3.
- **`Optional` import**: Use `from typing import Optional` if needed (project convention for Python 3.9 ABI compat). Not strictly required here since all fields are plain `str`/`bool`.
- **No `__post_init__` validation**: `ProjectSpec` is a pure data container. Validation lives in `core/validation.py`. Do not add validation logic here.
- **Size limit**: The class must stay ≤ 200 lines. With 20 fields + 2 methods, this is comfortable; do not pad with comments.

### Existing Code to NOT Touch

This story creates one new file only. Do **not** modify:
- `core/project_generator.py` — still uses `values: dict, config: dict` (changed in story 1.2)
- `core/render_context.py` — still uses `dict` (changed in story 1.2)
- `core/project_reader.py` — still returns `Optional[dict]` (changed in story 1.2)
- `app/pages/project.py` — still exposes `values()` and `config()` (changed in story 1.3)
- `app/main_window.py` — still calls `values()` + `config()` separately (changed in story 1.3)

### `to_dict()` / `from_dict()` Contract

```python
# to_dict() — all camelCase keys, JSON-safe values
spec.to_dict() == {
    "projectName": spec.project_name,
    "copyToSystemFolders": spec.copy_to_system_folders,  # bool preserved
    ...
}

# from_dict() — reads same camelCase keys, uses defaults for missing
spec2 = ProjectSpec.from_dict(spec.to_dict())
assert spec2 == spec  # must hold for any spec
```

`from_dict` must use `.get(key, default)` — never index directly — so that partial dicts (e.g. a sidecar with a missing optional field after a schema bump) do not raise `KeyError`.

### Cross-Story Dependencies

- **Story 1.2** will modify `ProjectGenerator.generate()`, `render_context.build_context()`, `ProjectWriter.write()`, and `project_reader.read_project()` to accept/return `ProjectSpec`. This story is the prerequisite.
- **Story 1.3** will add `ProjectPage.spec()` to the UI layer and wire `MainWindow` to use it.
- **Story 3.3** will write `tests/unit/test_project_spec.py` that tests `to_dict()` / `from_dict()` round-trip. Do not add tests now.

### Project Structure Notes

- New file goes in `core/` (lowercase Python package). Do not create `Core/` (PascalCase is only for non-package root folders like `Build/`, `Templates/`).
- The `core/` package has no `__init__.py` that needs updating — Python discovers modules automatically.

### References

- Field names sourced from: [app/pages/project_info.py](app/pages/project_info.py), [app/pages/compilation.py](app/pages/compilation.py), [app/pages/artefacts.py](app/pages/artefacts.py), [app/pages/project.py](app/pages/project.py)
- Artefact config keys sourced from: [core/preferences.py](core/preferences.py) `_DEFAULTS` and `_RENDER_KEYS`
- AD-1, AD-2, AD-8: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md) §Additional Requirements
- Clean code limits: [_bmad-output/project-context.md](_bmad-output/project-context.md) §Critical Implementation Rules

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Created `core/project_spec.py` (72 lines): `@dataclass` with 20 fields (str/bool), `to_dict()` → camelCase dict, `from_dict()` classmethod with `.get()` defaults. Zero Qt imports. All ACs verified by manual Python validation script.

### File List

- core/project_spec.py (new)

## Change Log

- 2026-06-23: Created `core/project_spec.py` — `ProjectSpec` dataclass with 20 fields, `to_dict()` and `from_dict()` round-trip serialization. No Qt dependencies.
