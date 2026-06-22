---
name: 'Luthier'
type: architecture-spine
purpose: build-substrate
altitude: feature
paradigm: 'strict-layered'
scope: 'Luthier — PySide6 GUI JUCE project generator'
status: final
created: '2026-06-22'
updated: '2026-06-22'
binds: []
sources:
  - _bmad-output/project-context.md
companions: []
---

# Architecture Spine — Luthier

## Design Paradigm

**Strict layered architecture** with a typed central model.

Three layers; dependencies flow downward only — `app/` → `core/` → `Templates/`. `core/` never imports from `app/`. `Templates/` is data, not code.

The **`ProjectSpec` dataclass** (`core/project_spec.py`) is the sole cross-layer contract: every layer that produces or consumes project data speaks `ProjectSpec`, never a raw `dict`.

```mermaid
graph TD
  app["app/ — UI (PySide6)"]
  core["core/ — Business logic"]
  tmpl["Templates/ — File templates"]
  tests["tests/ — pytest"]

  app --> core
  core --> tmpl
  tests --> core
  app -. "never" .-> tmpl
```

## Invariants & Rules

### AD-1 — ProjectSpec as the cross-layer contract

- **Binds:** all layers
- **Prevents:** key-mismatch bugs and silent failures from untyped dicts flowing across layer boundaries
- **Rule:** no layer passes a raw `dict` of project data across a layer boundary. `ProjectPage` exposes `spec() -> ProjectSpec`; `project_reader.read_project()` returns `Optional[ProjectSpec]`; `ProjectGenerator.generate()` accepts `ProjectSpec`. Fields use `snake_case` (Python); CMake template placeholders use `camelCase` (CMake convention). [ADOPTED]

### AD-2 — ProjectSpec is the single data model

- **Binds:** `ProjectPage`, `ProjectGenerator`, `ProjectWriter`, `project_reader`, `Preferences`
- **Prevents:** the two-dict split (`values` + `config`) that forced callers to assemble project data from two incompatible halves
- **Rule:** `ProjectSpec` carries both identity fields (plugin name, type, formats…) and artefact config fields (copy flags, per-OS paths). `ProjectPage.spec()` replaces `values()` + `config()`. [ADOPTED]

### AD-3 — Sidecar `.luthier.json` for round-trip; regex as fallback

- **Binds:** `ProjectWriter`, `project_reader`
- **Prevents:** regex fragility breaking round-trip when the generated CMake is reformatted or hand-edited; two competing deserialisers diverging over time
- **Rule:** `ProjectWriter` writes `.luthier.json` (full `ProjectSpec` serialised as JSON) alongside `CMakeLists.txt` at generation time. `project_reader.read_project()` is the **sole** deserialiser of `.luthier.json`; no other module reads or writes it. Falls back to `_parse_cmakelists()` when the sidecar is absent. A partial regex fallback (sidecar absent, CMake partially parseable) returns `None` — the UI reports a load failure; it never silently loads a partial `ProjectSpec`. [ADOPTED]

### AD-4 — Atomic project write

- **Binds:** `ProjectWriter`
- **Prevents:** a half-written, corrupted project directory when generation fails mid-way
- **Rule:** `ProjectWriter.write()` writes to a sibling temp directory (`<name>.tmp/`) then renames atomically to the final path — replacing the existing directory if present. On error, the temp directory is cleaned up and the original is left untouched. The old directory is never archived; the rename is the commit point and the overwrite is intentional (confirmed via the existing `MainWindow._confirm_overwrite()` guard). [ADOPTED]

### AD-5 — Preferences save-on-update; save is app-layer only

- **Binds:** `MainWindow`, `Preferences`
- **Prevents:** in-memory preference state diverging from disk; `core/` acquiring a hidden app-layer side-effect
- **Rule:** every call to `prefs.update(spec)` at a user-facing commit point (generate success, open success) is immediately followed by `prefs.save()`. Both calls are made by `MainWindow` only — `core/` never calls `prefs.save()` directly (would violate AD-8 and introduce a hidden side-effect in generation logic). [ADOPTED]

### AD-6 — Test strategy: pytest, two tiers, no Qt

- **Binds:** `tests/`
- **Prevents:** untested pure functions and fragile regex going undetected
- **Rule:** `tests/unit/` covers every public `core/` function with no Qt dependency (pure functions, no I/O). `tests/integration/` covers the full `ProjectSpec → write → read` round-trip using pytest's `tmp_path` fixture. No Qt widget tests. pytest is a dev-only dependency (`requirements-dev.txt`). [ADOPTED]

### AD-7 — `juce_dir` is Preferences-only

- **Binds:** `ProjectSpec`, `Preferences`, `render_context`
- **Prevents:** per-project JUCE path drift and unnecessary sidecar bloat
- **Rule:** `juce_dir` is never a field on `ProjectSpec`. It describes the dev environment, not the plugin. It is read from `Preferences` at generation time and passed separately to `render_context`; it does not participate in the round-trip. [ADOPTED]

### AD-8 — Dependency direction is enforced by import discipline

- **Binds:** all modules
- **Prevents:** a core module importing a Qt widget, collapsing the layer boundary and making core untestable without a display
- **Rule:** no module under `core/` imports from `app/`. Violations are caught by any test runner (import of `core/` must not trigger a Qt import). `Preferences` lives in `core/` and carries no Qt dependency. [ADOPTED]

### AD-9 — User template overrides are resolved at write time, not stored in ProjectSpec

- **Binds:** `ProjectWriter`, `templates_store`, `ProjectSpec`
- **Prevents:** two incompatible representations of template selection (stored ID vs. resolved Path) diverging across modules
- **Rule:** `ProjectSpec` carries no reference to user template overrides. `ProjectWriter` resolves overrides at write time via `templates_store.overrides_dir()` — a `Path` injected at construction. The override lookup is `ProjectWriter`'s responsibility alone; no other module resolves or stores it. [ADOPTED]

## Consistency Conventions

| Concern | Convention |
|---|---|
| Python identifiers | `snake_case` for functions, variables, fields; `PascalCase` for classes |
| CMake template keys | `camelCase` (`{projectName}`, `{cxxStandard}`, …) |
| CMake literal braces | Doubled: `${{VAR}}` in `str.format` templates |
| Token placeholders (C++ sources) | `@KEY@` form only; files remain valid C++ without substitution |
| File encoding | `encoding="utf-8"` on every `open()` / `read_text()` / `write_text()` |
| OS paths | `QStandardPaths` only; never hardcode `~/Library` or platform paths |
| Error propagation | `core/` raises standard Python exceptions (no custom hierarchy yet); `MainWindow` is the single catch boundary for user-visible errors; bare `except Exception` is acceptable only in `MainWindow` action handlers |
| Comments | Only for non-obvious *why* (hidden constraint, workaround, subtle invariant); never document *what* |

## Stack

| Name | Version |
|---|---|
| Python | 3.14 (cp310-abi3 ABI wheel) |
| PySide6 | ≥ 6.7 |
| Qt style | Fusion + custom QSS (`app/theme.py`) |
| pytest | latest (dev only) |
| PyInstaller | ≥ 6.0 (dev/packaging only) |

## Structural Seed

```text
Luthier/
  main.py                      # entry point: QApplication + MainWindow
  core/
    project_spec.py            # ProjectSpec dataclass — the cross-layer contract  ← NEW
    project_generator.py       # orchestrates generation; accepts ProjectSpec
    project_writer.py          # atomic write + .luthier.json sidecar
    project_reader.py          # .luthier.json first, CMake regex fallback
    render_context.py          # ProjectSpec → template context dict
    preferences.py             # Preferences — juce_dir lives here, not on ProjectSpec
    plugin_settings.py         # pure: flags, bundle_id, categories
    validation.py              # pure: field validators → (bool, str)
    rendering.py               # render() [str.format] + render_tokens() [@KEY@]
    templates_store.py         # read/write/reset user source template overrides
  app/
    main_window.py             # QMainWindow: tab bar, stack, generate/open actions
    theme.py                   # Palette + build_stylesheet() — single QSS source
    pages/                     # one file per tab/section; emit validityChanged
    widgets/                   # reusable field widgets (ValidatedField, ComboField…)
  tests/
    unit/                      # pure core/ functions — no I/O, no Qt
    integration/               # ProjectSpec round-trip with tmp_path
  Templates/                   # bundled JUCE project templates (versioned in repo)
  Resources/                   # luthier.svg
  Build/                       # luthier.spec (PyInstaller)
  requirements.txt             # PySide6
  requirements-dev.txt         # -r requirements.txt, PyInstaller, pytest
```

## Deferred

| Decision | Reason deferred |
|---|---|
| CLAP format support | `plugin_formats: str` on `ProjectSpec` already carries it. Note: CLAP in JUCE requires the third-party `clap-juce-extensions` CMake module — the CMakeLists.txt template will need a conditional block; decide scope and dependency management at story time |
| JUCE path UI in PreferencesPage | Implementation task; key already exists in `Preferences._DEFAULTS`, just needs a UI row |
| Qt/UI test coverage | No Qt headless test runner identified; `core/` tests deliver higher ROI first |
| Template rendering error boundary | `rendering.render()` raises `KeyError` on malformed template; catch and re-raise as `RenderError` is an implementation detail for a story |
