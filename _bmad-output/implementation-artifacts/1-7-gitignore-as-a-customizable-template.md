---
baseline_commit: 659520fc5b09d4c4f880945676300acc6c9a3d04
---

# Story 1.7: .gitignore as a Customizable Template

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer,
I want to customize the generated `.gitignore` from within Luthier,
so that my project's ignore rules persist across regenerations without manual re-editing.

## Acceptance Criteria

1. **Given** the Templates tab, **when** I open the file selector combo, **then** `.gitignore` appears in the list alongside the 4 source files.
2. **Given** I select `.gitignore` and edit its content, then click "Save Override", **when** the save completes, **then** the override is persisted to `QStandardPaths::AppConfigLocation / Luthier / templates / .gitignore`.
3. **Given** a `.gitignore` override exists, **when** a project is generated, **then** the override content is written as `.gitignore` in the project directory (instead of the bundled default).
4. **Given** I click "Reset" on the `.gitignore` template, **when** confirmed, **then** the override file is deleted and the next generation uses the bundled default.
5. **Given** I click "Load File" and select an external file, **when** the file is loaded, **then** its content replaces the editor content — but is not persisted until "Save Override" is explicitly clicked.

## Tasks / Subtasks

- [x] Extend `templates_store` for `.gitignore` (AC: 2, 4)
  - [x] Add `GITIGNORE_FILE = ".gitignore"` and `EDITABLE_FILES` tuple (4 sources + `.gitignore`)
  - [x] Add `templates_root() -> Path` (`AppConfigLocation / Luthier / templates`)
  - [x] Keep `overrides_dir()` as `templates_root() / "Source"` (backward compatible for source overrides)
  - [x] Add `_bundled_path(name)` and `_override_path(name)` helpers — gitignore lives at repo root of `Templates/`, not `Templates/Source/`
  - [x] Refactor `read_default`, `read_effective`, `save_override`, `reset`, `has_override` to route through helpers

- [x] Wire `.gitignore` override into generation (AC: 3)
  - [x] Extend `ProjectWriter._override_for()` to resolve `.gitignore` overrides (currently only `_TOKENIZED` files)
  - [x] Override lookup: `templates_root() / ".gitignore"` when present; bundled default: `Templates/.gitignore`
  - [x] `.gitignore` stays in `_VERBATIM` — no rendering, verbatim copy only

- [x] Update Templates tab UI (AC: 1, 5)
  - [x] Populate combo from `templates_store.EDITABLE_FILES` (not `SOURCE_FILES` alone)
  - [x] Plain-text editor mode when `.gitignore` is selected — disable `CppHighlighter` (PRD F6)
  - [x] Re-enable `CppHighlighter` when switching back to a C++ source file
  - [x] Broaden "Load from file…" filter when `.gitignore` is selected (e.g. `All files (*)`)

### Review Findings

- [x] [Review][Patch] QFileDialog may hide dot-prefixed `.gitignore` files on load [app/pages/templates.py:107-111]
- [x] [Review][Defer] Override path resolution duplicated (`templates_store._override_path` vs `project_writer._overrides.parent`) [core/project_writer.py:85-87] — deferred, intentional per story spec AD-9
- [x] [Review][Defer] Hardcoded `".gitignore"` string in `ProjectWriter` instead of shared `GITIGNORE_FILE` constant [core/project_writer.py:85] — deferred, spec shows literal; minor consistency only
- [x] [Review][Defer] `.gitignore` special-cased in three modules rather than unified metadata [multiple] — deferred, minimal-scope approach per story spec
- [x] [Review][Defer] `_on_load_file` does not refresh status label after load [app/pages/templates.py:112-113] — deferred, pre-existing for source templates
- [x] [Review][Defer] No validation that loaded file matches selected template type [app/pages/templates.py:111-113] — deferred, pre-existing UX pattern
- [x] [Review][Defer] `Path.read_text` in load-file handler has no user-visible error handling [app/pages/templates.py:113] — deferred, pre-existing
- [x] [Review][Defer] Split override layout (`templates/.gitignore` vs `templates/Source/*`) [core/templates_store.py] — deferred, required by AC2
- [x] [Review][Defer] No automated tests for gitignore override paths or UI flows [—] — deferred, Epic 3 story 3-3 per spec
- [x] [Review][Defer] `read_default` raises `FileNotFoundError` if bundled asset missing [core/templates_store.py:51-52] — deferred, pre-existing
- [x] [Review][Defer] `save_override` accepts arbitrary `name` without allowlist [core/templates_store.py:60-63] — deferred, pre-existing; internal callers only

## Dev Notes

### Scope — 3 files (+ optional 4th)

| File | Change |
|------|--------|
| `core/templates_store.py` | Add gitignore paths, `EDITABLE_FILES`, refactor path helpers |
| `core/project_writer.py` | Extend `_override_for()` for `.gitignore` |
| `app/pages/templates.py` | Combo list, plain-text mode, load-file filter |

**Do NOT touch:**
- `core/project_spec.py` — no template reference on `ProjectSpec` (AD-9)
- `Templates/.gitignore` bundled content — default is already correct; only expose customization
- `app/main_window.py` — `ProjectGenerator(overrides=templates_store.overrides_dir())` stays valid; `_override_for` resolves gitignore via `templates_store` path helpers (parent of `overrides_dir`)
- Any test files — Epic 3 (`tests/unit/test_templates_store.py` will cover this in story 3-3)
- `core/render_context.py`, `core/project_generator.py` — no rendering for `.gitignore`

### Current State — Partial Implementation

| Area | Status |
|------|--------|
| Bundled `Templates/.gitignore` | ✅ Exists (53 lines, C++/JUCE build artefacts) |
| `ProjectWriter` copies `.gitignore` | ✅ In `_VERBATIM` — always bundled default |
| `templates_store` source overrides | ✅ Works for 4 `Source/*` files |
| `.gitignore` in `templates_store` | ❌ Not in `SOURCE_FILES`; no read/save/reset |
| `ProjectWriter._override_for()` | ❌ Only checks `_TOKENIZED` — skips `.gitignore` |
| Templates tab combo | ❌ Lists `SOURCE_FILES` only (4 items) |
| Plain-text editor for `.gitignore` | ❌ `CppHighlighter` always active |

### Architecture Compliance (AD-9)

```
User edits .gitignore in TemplatesPage
        ↓ Save Override
templates_store.save_override(".gitignore", content)
        ↓ writes to
~/.../AppConfigLocation/Luthier/templates/.gitignore
        ↓ at generation (write time, not on ProjectSpec)
ProjectWriter._override_for(".gitignore")
        ↓ if override exists
project_dir/.gitignore  (user content)
        ↓ else
Templates/.gitignore  (bundled default)
```

- `ProjectSpec` / `.luthier.json`: **must not** reference template overrides
- Override resolution stays in `ProjectWriter` at write time — same pattern as source templates
- `MainWindow` continues passing `templates_store.overrides_dir()` (Source subdir); gitignore override is resolved via `templates_root()` (parent of `overrides_dir()`)

### `templates_store.py` — Exact Implementation

Add constants and path helpers:

```python
GITIGNORE_FILE = ".gitignore"

EDITABLE_FILES = SOURCE_FILES + (GITIGNORE_FILE,)

def templates_root() -> Path:
    location = QStandardPaths.StandardLocation.AppConfigLocation
    base = QStandardPaths.writableLocation(location)
    return Path(base) / "templates"

def overrides_dir() -> Path:
    return templates_root() / "Source"

def _bundled_path(name: str) -> Path:
    if name == GITIGNORE_FILE:
        return templates_dir() / GITIGNORE_FILE
    return templates_dir() / "Source" / name

def _override_path(name: str) -> Path:
    if name == GITIGNORE_FILE:
        return templates_root() / GITIGNORE_FILE
    return overrides_dir() / name
```

Refactor existing functions (same public API, extended behaviour):

```python
def has_override(name: str) -> bool:
    return _override_path(name).exists()

def read_default(name: str) -> str:
    return _bundled_path(name).read_text(encoding="utf-8")

def read_effective(name: str) -> str:
    path = _override_path(name)
    return path.read_text(encoding="utf-8") if path.exists() else read_default(name)

def save_override(name: str, content: str) -> None:
    target = _override_path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

def reset(name: str) -> None:
    _override_path(name).unlink(missing_ok=True)
```

**Path layout on disk (macOS example):**

| File | Bundled | User override |
|------|---------|---------------|
| `PluginProcessor.h` | `Templates/Source/PluginProcessor.h` | `~/Library/Preferences/Luthier/templates/Source/PluginProcessor.h` |
| `.gitignore` | `Templates/.gitignore` | `~/Library/Preferences/Luthier/templates/.gitignore` |

**Why gitignore is NOT under `Source/`:** It is a project-root file, not a source file. AC2 explicitly requires `templates / .gitignore` (not `templates/Source/.gitignore`).

### `project_writer.py` — Exact Edit

Extend `_override_for()` — minimal change, preserve existing Source logic:

```python
def _override_for(self, relative: str) -> Optional[Path]:
    if not self._overrides:
        return None
    if relative in _TOKENIZED:
        candidate = self._overrides / Path(relative).name
        return candidate if candidate.exists() else None
    if relative == ".gitignore":
        candidate = self._overrides.parent / ".gitignore"
        return candidate if candidate.exists() else None
    return None
```

**Why `self._overrides.parent`:** `self._overrides` is `templates_root() / "Source"` (injected from `main_window`). Parent is `templates_root()` where `.gitignore` override lives. No `main_window` change required.

**Alternative (prefer if `_overrides.parent` feels fragile):** import `templates_store` and call `templates_store._override_path(".gitignore")` — but private helper; cleaner to add public `override_path_for_relative(relative: str) -> Optional[Path]` if you want zero coupling to directory layout in `ProjectWriter`. Either approach is acceptable; keep function ≤ 15 lines.

### `app/pages/templates.py` — Exact Edits

**Combo population** — replace `SOURCE_FILES` with `EDITABLE_FILES`:

```python
self._selector.addItems(templates_store.EDITABLE_FILES)
```

**Plain-text mode for `.gitignore`** — store optional highlighter, toggle on selection:

```python
def __init__(self):
    ...
    self._highlighter: CppHighlighter | None = CppHighlighter(self._editor.document())
    ...

def _load_selected(self, name: str) -> None:
    self._set_syntax_mode(name)
    self._editor.setPlainText(templates_store.read_effective(name))
    self._update_status(name)

def _set_syntax_mode(self, name: str) -> None:
    if name == templates_store.GITIGNORE_FILE:
        if self._highlighter:
            self._highlighter.setDocument(None)
            self._highlighter = None
        return
    if not self._highlighter:
        self._highlighter = CppHighlighter(self._editor.document())
```

**Load file filter** — branch on current selection:

```python
def _on_load_file(self) -> None:
    name = self._selector.currentText()
    if name == templates_store.GITIGNORE_FILE:
        filt = "Git ignore (*.gitignore);;All files (*)"
    else:
        filt = "C++ source (*.h *.cpp);;All files (*)"
    path, _ = QFileDialog.getOpenFileName(self, "Load template file", "", filt)
    ...
```

**Note:** `Load File` already does not persist — only updates editor (AC5 satisfied by existing behaviour).

### Clean Code Metrics Verification

| Function | Lines | Params | Complexity |
|----------|-------|--------|------------|
| `templates_root()` | 3 | 0 | 1 |
| `_bundled_path()` | 3 | 1 | 2 |
| `_override_path()` | 3 | 1 | 2 |
| `_override_for()` (updated) | 9 | 1 | 4 |
| `_set_syntax_mode()` | 8 | 1 | 3 |

All within limits. ✓

### Regression Guardrails

| Behavior | Must preserve |
|----------|---------------|
| Source template overrides | Unchanged paths under `templates/Source/` |
| Source template generation | `_TOKENIZED` override resolution unchanged |
| Generate without any overrides | Bundled `Templates/.gitignore` written verbatim |
| `ProjectSpec` / `.luthier.json` | No template override fields |
| C++ editor highlighting | Still active for all 4 source files after switching back from `.gitignore` |
| AD-9 write-time resolution | Overrides not stored on spec; resolved only in `ProjectWriter` |

### Known Deferred Issues (Do Not Fix Here)

- No automated tests for `templates_store` gitignore paths — Epic 3 story 3-3
- `project-context.md` §Template Overrides still says "4 Source files" — update in a docs pass if desired, not required for this story
- Reset has no confirmation dialog — pre-existing UX for source templates; do not add confirmation only for gitignore

### Testing

No new automated tests (Epic 3). Manual verification:

1. `.venv/bin/python main.py --check` exits 0
2. Open Templates tab → combo shows 5 items including `.gitignore` (AC1)
3. Select `.gitignore` → editor shows bundled default; no C++ syntax colouring (plain text)
4. Edit content → Save Override → verify file at `~/Library/Preferences/Luthier/templates/.gitignore` (AC2)
5. Generate project → `project_dir/.gitignore` matches override content (AC3)
6. Reset → override file deleted; editor shows bundled default; regenerate → bundled default in project (AC4)
7. Load File → pick external `.gitignore` → editor updates; **do not** Save → regenerate → still uses previous override (or bundled if none) (AC5)
8. Switch `.gitignore` → `PluginProcessor.h` → C++ highlighting returns
9. Existing source template override still works (regression)

### References

- Story 1.7 ACs: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md) §Story 1.7
- FR6 / F6 customizable templates: [_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md](_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md) §F6
- AD-9 override at write time: [_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md) §AD-9
- Current `templates_store` (Source-only): [core/templates_store.py](core/templates_store.py)
- Current `ProjectWriter` (no gitignore override): [core/project_writer.py:79-83](core/project_writer.py)
- Current Templates UI (4 files only): [app/pages/templates.py](app/pages/templates.py)
- Bundled default: [Templates/.gitignore](Templates/.gitignore)
- Override injection point: [app/main_window.py:39](app/main_window.py) `overrides=templates_store.overrides_dir()`
- Previous story patterns: [_bmad-output/implementation-artifacts/1-6-juce-directory-in-preferences.md](_bmad-output/implementation-artifacts/1-6-juce-directory-in-preferences.md)

## Dev Agent Record

### Agent Model Used

Composer (Cursor)

### Debug Log References

- Verified path helpers and `_override_for` via inline Python checks (gitignore at `templates_root()`, source files at `templates_root()/Source/`).
- `main.py --check` exits 0; existing test suite (11 tests) passes with no regressions.

### Completion Notes List

- Extended `templates_store` with `GITIGNORE_FILE`, `EDITABLE_FILES`, `templates_root()`, `_bundled_path()`, `_override_path()`; all read/save/reset/has_override functions route through path helpers.
- `ProjectWriter._override_for()` now resolves `.gitignore` via `self._overrides.parent / ".gitignore"` — no `main_window` change required.
- Templates tab combo shows 5 editable files; CppHighlighter toggled off for `.gitignore`, re-enabled on C++ file selection; load-file dialog uses gitignore-specific filter.
- All 5 acceptance criteria satisfied. No automated tests added (deferred to Epic 3 story 3-3 per story spec).

### File List

- `core/templates_store.py` (modified)
- `core/project_writer.py` (modified)
- `app/pages/templates.py` (modified)

### Change Log

- 2026-06-23: Code review — QFileDialog ShowHidden + DontUseNativeDialog for `.gitignore` load (AC5).

## Previous Story Intelligence (Story 1-6)

- Story 1-6 established the pattern of **minimal-scope edits** with explicit "Do NOT touch" lists and regression guardrails — follow same structure
- `Preferences.apply_form()` fixed a broken save path — Templates save already works via `templates_store.save_override()`; no analogous bug here
- Manual verification checklist format from 1-6 is the project norm until Epic 3
- Code review from 1-6 deferred CMake path escaping and automated tests — same deferrals apply
- Commit style: `Wire JUCE directory preference through generation pipeline (story 1-6, done)`

## Git Intelligence Summary

Recent commits (Epic 1 progression):

| Commit | Story | Files touched | Pattern |
|--------|-------|---------------|---------|
| `659520f` | 1-6 | preferences, main_window, project_generator, render_context, CMakeLists | Separate arg pipeline (`juce_dir`), not on ProjectSpec |
| `14674f4` | 1-5 | render_context, project_writer, CMakeUserPresets.json | Move file from `_VERBATIM` → `_RENDERED`; context injection |
| `c58a341` | 1-4 | CMakeLists.txt | Template consolidation |
| `c3bb7bf` | 1-3 | app layer, ProjectSpec | End-to-end spec contract |
| `425fe3e` | 1-2 | project_generator, project_writer | Core pipeline accepts ProjectSpec |

**Actionable for 1-7:** Extend existing `templates_store` / `ProjectWriter._override_for` pattern — do not introduce new persistence mechanism or ProjectSpec fields. Story 1-5 precedent: moving handling between verbatim/rendered categories — here extend override resolution without changing generation orchestration.

## Latest Tech Information

- **PySide6 `QSyntaxHighlighter`:** Call `highlighter.setDocument(None)` to detach; create new `CppHighlighter(editor.document())` to reattach. No `QPlainTextEdit.setHighlighter()` API.
- **Qt `QStandardPaths.AppConfigLocation`:** On macOS resolves to `~/Library/Preferences/<AppName>/` — matches existing `preferences.json` and `templates/Source/` layout.
- **`.gitignore` format:** Plain text, one pattern per line; `#` comments; no encoding requirements beyond UTF-8 (project standard).
- No external libraries needed — stdlib + existing PySide6 only.

## Project Context Reference

Key rules from [_bmad-output/project-context.md](_bmad-output/project-context.md):

- Run: `.venv/bin/python main.py` / `--check`
- `encoding="utf-8"` on all file I/O
- `QStandardPaths` for OS paths — never hardcode `~/Library`
- Clean code limits: 15 lines/function, complexity < 5
- Template overrides: currently documented as 4 Source files only — this story extends to 5 editable templates per FR6
- `ProjectWriter` atomic write via temp dir — `.gitignore` flows through existing `_VERBATIM` loop unchanged

### Story Completion Status

- Status: **ready-for-dev**
- Ultimate context engine analysis completed — comprehensive developer guide created
