---
project_name: 'Luthier'
user_name: 'Guillaume'
date: '2026-06-22'
sections_completed: ['technology_stack', 'architecture', 'patterns', 'critical_rules', 'known_issues', 'goals']
---

# Project Context for AI Agents

_Critical rules and patterns for Luthier. Focus on non-obvious details that prevent mistakes._

---

## Technology Stack & Versions

- **Python 3.14** (only interpreter installed; `cp310-abi3` ABI wheel)
- **PySide6 ≥ 6.7** — Qt bindings; never PyQt6 (licence incompatibility)
- **PyInstaller ≥ 6.0** — packaging only (dev dependency)
- **No external runtime deps** beyond PySide6; stdlib + PySide6 everywhere
- **Qt style**: `Fusion` + full custom QSS from `app/theme.py`
- **Run**: `.venv/bin/python main.py` — never `python main.py`
- **Build**: `.venv/bin/pyinstaller Build/luthier.spec --noconfirm --distpath Dist --workpath Build`
- **Headless check**: `.venv/bin/python main.py --check`

---

## Repository Layout

```
Luthier/
├── main.py                        # Entry point: QApplication + MainWindow
├── app/
│   ├── main_window.py             # QMainWindow: tab bar, page stack, bottom bar
│   ├── theme.py                   # Palette + build_stylesheet() — single source of truth for all QSS
│   ├── qss.py                     # repolish() helper
│   ├── resources.py               # Resource helpers
│   ├── pages/
│   │   ├── project.py             # ProjectPage (QScrollArea) — composes all sections
│   │   ├── project_info.py        # ProjectInfoPage — identity fields + bundle ID
│   │   ├── plugin_type.py         # PluginTypePage — radio buttons (synth/effect/midi)
│   │   ├── formats.py             # FormatsPage — checkboxes (AU/VST3/Standalone)
│   │   ├── compilation.py         # CompilationSection — C++ std, defs, include paths
│   │   ├── artefacts.py           # ArtefactsSection — copy settings, per-OS paths
│   │   ├── preferences.py         # PreferencesPage — identity defaults + artefact defaults
│   │   ├── templates.py           # TemplatesPage — C++ source template editor
│   │   └── about.py               # AboutPage — static info
│   └── widgets/
│       ├── validated_field.py     # ValidatedField + FieldSpec + make_field_label()
│       ├── validated_form.py      # ValidatedForm — stacks ValidatedField rows
│       ├── section.py             # Section — titled group with divider
│       ├── combo_field.py         # ComboField — label + QComboBox row
│       ├── text_area_field.py     # TextAreaField — label + QPlainTextEdit
│       ├── save_bar.py            # SaveBar — save/reset button row
│       └── cpp_highlighter.py     # C++ syntax highlighter (regex-based)
├── core/
│   ├── project_generator.py       # ProjectGenerator — orchestrates generation
│   ├── project_writer.py          # ProjectWriter — writes files from templates
│   ├── render_context.py          # build_context() + build_tokens() — data for templates
│   ├── rendering.py               # render() [str.format] + render_tokens() [@KEY@]
│   ├── project_reader.py          # read_project_result() — sidecar-only reload into ProjectSpec
│   ├── plugin_settings.py         # Pure functions: flags_for_type, bundle_id, categories
│   ├── validation.py              # Pure field validators → (bool, str) tuples
│   ├── preferences.py             # Preferences — JSON persistence in OS config dir
│   ├── app_state.py               # AppState — last-used parent dir (separate from prefs)
│   └── templates_store.py         # Read/write/reset C++ source template overrides
├── Templates/                     # Bundled project templates (versioned in repo)
│   ├── CMakeLists.txt             # str.format template ({{ }} for CMake literal braces); USER OPTIONS at top
│   ├── CMakeUserPresets.json      # verbatim copy
│   ├── README.md
│   ├── .gitignore / .cursorrules  # verbatim copies
│   ├── .vscode/                   # settings/tasks/launch: str.format; extensions: verbatim
│   ├── CMake/CopyVst3Elevated.ps1 # verbatim copy
│   └── Source/                    # @KEY@ token templates (valid C++ when unrendered)
│       ├── PluginProcessor.{h,cpp}
│       └── PluginEditor.{h,cpp}
├── resources/
│   ├── luthier-logo.png           # README / branding
│   └── icons/                     # App icon (icns, ico, png)
├── build/
│   └── luthier.spec               # PyInstaller spec
├── docs/
│   ├── luthier.png                # Logo (README)
│   ├── user-manual.md
│   └── architecture.md
└── rules/                         # Dev rules (optional local)
    └── ...
```

**Folder casing**: `templates/`, `resources/`, `build/`, `dist/`, `docs/`, `app/`, and `core/` are lowercase. `templates/Source/` and `templates/CMake/` use PascalCase for JUCE layout parity.

---

## Architecture

### Data Flow

```
User fills form (ProjectPage)
  → ProjectPage.spec() → ProjectSpec
  → MainWindow._on_generate()
      → ProjectGenerator.generate(spec)
          → render_context.build_context(spec) → context dict (str.format keys)
          → render_context.build_tokens(spec) → tokens dict (@KEY@ keys)
          → ProjectWriter(templates_dir, project_dir, overrides).write(context, tokens)
      → AppState.remember_parent(spec.host_destination_dir()) + save()  [app_state.json only]
  → MainWindow._on_open()
      → read_project_result() → ProjectSpec → ProjectPage.load(spec)  [no prefs write]
```

### Two-Pass Template Rendering

**Critical distinction** — two separate rendering mechanisms:

| Pass | Files | Method | Key Format | Purpose |
|------|-------|--------|-----------|---------|
| str.format | CMakeLists.txt, *.cmake, .vscode/*.json, README.md | `rendering.render()` | `{key}` | CMake/JSON templates |
| Token replace | Source/*.{h,cpp} | `rendering.render_tokens()` | `@KEY@` | C++ stays valid without substitution |

In str.format templates, literal CMake braces must be doubled: `${{VAR}}` renders as `${VAR}`.

Only two tokens exist for source files: `@PROJECT_NAME@` and `@PROJECT_DISPLAY_NAME@`.

### Round-Trip: Reading Back a Generated Project

`project_reader.read_project_result(project_dir)` reads `.luthier.json` only (AD-3, story 8.2). Key rules:
- Sidecar missing or invalid → `ProjectReadResult(spec=None, error=...)`
- No CMake regex fallback
- On success, host **destination** is injected from the parent of the opened project folder
- `ProjectSpec.from_dict()` deserialises the sidecar JSON (six workspace keys per OS)

### Template Overrides

Users can override the 4 Source files. Override path: `~/.../AppConfigLocation/Luthier/templates/Source/<filename>`.  
`templates_store` module manages read/write/reset. `ProjectWriter._override_for()` checks overrides only for `_TOKENIZED` files.

### Preferences Persistence

`core/preferences.py` — JSON at `~/.../AppConfigLocation/Luthier/preferences.json`.  
Keys: `manufacturer`, `manufacturerCode`, `pluginCode`, `companyCopyright`, `companyWebsite`, `companyEmail`, six workspace keys (`destinationDirWindows/Macos/Linux`, `juceDirWindows/Macos/Linux`), `artefactsDirWindows/Macos/Linux`, `copyToSystemFolders`, `copyToArtefactsDir`.

**AD-5 (revised):** `preferences.json` is written **only** by: (1) first-launch factory file creation, (2) Preferences tab auto-save on valid edit, (3) successful Import Preferences. `MainWindow` calls `prefs.save()` only after auto-save or import — **never** after Open Project or Generate Project. Open and Generate must not call `Preferences.update(ProjectSpec)`.

### App State

`core/app_state.py` — JSON at `~/.../AppConfigLocation/Luthier/app_state.json` (sibling of `preferences.json`, **not** part of Import/Export profile).  
Fields: `lastUsedParentDir`, `lastPrefsProfileDir`, `windowGeometry` (Qt bytes), `windowRect`, `windowMaximized`. Written after successful Generate (`remember_parent`), Import/Export path picks, and window resize/move (debounced). Used by Choose… / Open dialog start dirs via `dialog_start_dir()` and by `MainWindow` to restore size, position, and maximized state.

---

## UI Patterns

### Tabs (not sidebar)

Navigation is a **`QTabBar`** at the top (not a sidebar). Tabs: `["Project", "Preferences", "Templates", "About"]`. Controlled by `MainWindow` via `QStackedWidget`.

### Section Composition

`ProjectPage` (QScrollArea) composes sections using `Section(title, body_widget)`. Each section widget is standalone and reusable. Sections: Project Info, Plugin Type, Formats, Compilation, Artefacts.

### Validated Fields

`ValidatedField(FieldSpec)` — label + QLineEdit + ✓/✗ mark + inline error. Validator signature: `(str) -> (bool, str)`. Mark is hidden when field is empty. Error label is visible only when field is non-empty and invalid.

`ValidatedForm` — vertical stack of `ValidatedField`s, emits `validityChanged` as aggregate.

`FieldSpec` dataclass: `key`, `label`, `validator`, `default=""`, `placeholder=""`.

`make_field_label(text)` — creates a fixed-width (150px) left-aligned `QLabel#FieldLabel`. Use it for all form row labels for consistent alignment.

### Signal Pattern

Pages emit `validityChanged = Signal(bool)`. `MainWindow` connects to `ProjectPage.validityChanged` to enable/disable "Generate Project" button.

### QSS Theming

All styling is in `app/theme.py:build_stylesheet()`. The `Palette` class defines all colours. `kMainColor_ = "#FF6633"` is the single accent source.

Orange action buttons use `objectName`: `#GenerateButton`, `#OpenButton`, `#SaveButton`, `#ActionButton`.

Status labels: `#StatusOk` (green) / `#StatusErr` (red). Apply with `repolish()` after changing `objectName` property.

Dynamic property states (e.g., `#FieldMark[state="ok"]`) require `repolish(widget)` after `setProperty(...)`.

SVG icons (checkbox tick, combo caret) are written to the OS cache dir at startup using `_icon_url()`.

### PyInstaller Frozen Assets

When frozen, `sys._MEIPASS` is set. `templates_dir()` in `project_generator.py` resolves `sys._MEIPASS / "Templates"`. The spec bundles `Templates/` and `Resources/luthier.svg`. Qt SVG plugins are included for the logo.

---

## Critical Implementation Rules

### Python

- No type annotations in function signatures beyond what already exists (project uses minimal annotations)
- `Optional[X]` import from `typing` (Python 3.9 compat via cp310-abi3 wheel)
- All file I/O: `encoding="utf-8"` explicitly
- No f-strings in QSS (already uses f-string in `build_stylesheet`; keep existing pattern)
- `QStandardPaths` for all OS-specific paths (config, cache) — never hardcode `~/Library` etc.

### Clean Code Rules (Rules/process-clean-code.md — MANDATORY)

3-phase process for every code change:
1. **DESIGN** — SRP, DRY/YAGNI/KISS/ETC, explicit names, dependencies
2. **IMPLEMENTATION** — follow design; if limit exceeded → stop and extract
3. **AUTO-REVIEW** — check all metrics; failure → back to phase 1

Hard limits:
- Function/method: **15 lines** (20 max for orchestration that only delegates)
- Class: **200 lines**
- Parameters: **3** (use dataclass if more)
- Cyclomatic complexity: **< 5**
- Indentation levels: **2**

Priority when conflicts: **correctness > KISS/YAGNI > SOLID > premature DRY**

### Naming Conventions

- Python files: `snake_case.py`
- Python classes: `PascalCase`
- Python functions/variables: `snake_case`
- Qt object names (for QSS): `PascalCase` strings (`setObjectName`)
- Validators: `validate_<field_name>(value: str) -> ValidationResult`
- Form keys (dict keys from `.values()`): `camelCase` (matches CMake template placeholders)
- Git commits: English only
- Folder names at project root: `PascalCase` (except Python packages `app/`, `core/`)

### No Comments Policy

Comments only for **non-obvious WHY** (hidden constraint, workaround, subtle invariant). Never document WHAT the code does. Never reference the current task/story in comments.

### PySide6 Specifics

- Always `QVBoxLayout(parent_widget)` — pass parent directly; do not call `setLayout()` separately
- `QScrollArea.setWidgetResizable(True)` required for content to fill width
- `QComboBox` with custom view needs `setView(QListView())` to fix truncation
- Dynamic QSS properties: call `repolish(widget)` (from `app/qss.py`) after `setProperty()`
- Never use `app.exec_()` (deprecated) — use `app.exec()`

### Template Authoring

When modifying `Templates/CMakeLists.txt` or `*.cmake`:
- All CMake variable references become `${{VAR}}` (double-brace to survive `str.format`)
- All project values use single braces: `{projectName}`, `{cxxStandard}`, etc.
- Optional blocks (headerSearchPaths, extraDefinitionsBlock) are injected as pre-formatted multiline strings or empty strings — never conditional in the template itself

When modifying Source templates:
- Use `@PROJECT_NAME@` and `@PROJECT_DISPLAY_NAME@` only
- Templates must be valid C++ without substitution (no `{` placeholders)

---

## Known Issues / Areas for Improvement

These were identified during brownfield analysis and represent the main refactoring targets:

1. **Test coverage** — core validators, generation pipeline, and sidecar reload covered by `tests/unit/` and `tests/integration/`; Qt widget tests remain manual (AD-6)
2. **`project_reader.py`** — sidecar-only; malformed sidecar returns explicit `error` string
3. **`ProjectWriter._reset_project_dir()` is destructive** — silently deletes and recreates the entire project dir on every generation; no backup or diff
4. **Preferences auto-save** — `PreferencesPage` auto-saves on valid edit; Open/Generate no longer write `preferences.json` (Story 5.4)
5. **`MainWindow` orchestration is wide** — handles generation, open, status, prefs, templates: borderline single responsibility
6. **JUCE dir on Project tab** — exposed via `FolderField`; persisted on `ProjectSpec` / `.luthier.json`, not synced to global prefs on Open/Generate
7. **`_field_specs` and `_pref_specs` exceed 15 lines** — conscious deviation; acceptable as pure data (complexity 1)
8. **`build_stylesheet()` exceeds 15 lines** — acceptable as pure data (QSS string); matches pre-existing pattern
9. **No error boundary for template rendering** — `str.format` with a malformed template raises `KeyError`; not caught gracefully
10. **`ProjectPage.config()` returns artefact values only** — naming is misleading; `config` sounds like "all settings" but is only the copy/artefact half

---

## Feature Goals (Next Development Phase)

From user requirements stated at project init:

1. **Modify existing project settings** — fully functional round-trip (open → edit any field → regenerate); currently works but needs robustness (issue #2, #3 above)
2. **User-supplied source templates** — already implemented via `templates_store`; needs UX polish and documentation
3. **Test suite** — unit tests for `core/` (validators, reader, render_context, plugin_settings) as baseline; no mocking needed (pure functions)
4. **Robustness of CMake parsing** — consider a more structured parser or normalize generated output to guarantee round-trip
5. **JUCE version / path management** — expose JUCE location in Preferences for users who don't use the default `/Applications/JUCE`
6. **CLAP format support** — mentioned in CMakeLists.txt comment as future; Linux priority

---

## Reference Paths

| Resource | Path |
|----------|------|
| Prototype generator (reference only, do not modify) | `/Volumes/Guillaume/Dev/SDKs/JUCE/Tools/Juce-Project-Generator/` |
| Projucer sources (UX/feature inspiration) | `/Applications/JUCE/extras/Projucer/` |
| JUCE installation | `/Applications/JUCE/` |
| GitHub repo | `https://github.com/tensquaresoftware/luthier` |
| Preferences JSON (runtime) | `~/Library/Preferences/Luthier/preferences.json` (macOS) |
| App state JSON (runtime) | `~/Library/Preferences/Luthier/app_state.json` (macOS) |
| Template overrides (runtime) | `~/Library/Preferences/Luthier/templates/Source/` (macOS) |
