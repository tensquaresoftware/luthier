---
baseline_commit: 14674f4c5b09d4c4f880945676300acc6c9a3d04
---

# Story 1.6: JUCE Directory in Preferences

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer,
I want to set my JUCE installation path in Preferences,
so that generated projects reference the correct JUCE location without requiring a system environment variable at configure time.

## Acceptance Criteria

1. **Given** the Preferences tab, **when** I view it, **then** a "JUCE directory" field is present and editable, with a placeholder indicating the expected path format for the current OS.
2. **Given** a `juce_dir` value is set in `Preferences`, **when** `MainWindow` triggers generation, **then** `render_context.build_context(spec, juce_dir=prefs.juce_dir)` receives `juce_dir` as a separate argument — it is never stored on `ProjectSpec` (AD-7).
3. **Given** `juce_dir` is non-empty, **when** `CMakeLists.txt` is generated, **then** the JUCE path is referenced in the appropriate CMake variable (e.g. `set(JUCE_DIR "...")`) before the existing discovery block so the preset/cache/ENV fallback chain still works.
4. **Given** `juce_dir` is empty, **when** a project is generated, **then** no preference-injected `set(JUCE_DIR "...")` line appears in `CMakeLists.txt` (existing ENV + platform-default discovery applies unchanged).
5. **Given** I edit Preferences (including JUCE directory) and click "Save Preferences", **when** save succeeds, **then** `juceDir` is persisted to `preferences.json` and survives app restart — without calling `Preferences.update(ProjectSpec)` (AD-7: `juceDir` is not on `ProjectSpec`).

## Tasks / Subtasks

- [x] Fix Preferences persistence for the Preferences tab (AC: 1, 5)
  - [x] Add `Preferences.apply_form(identity: dict, artefacts: dict) -> None` — updates identity keys + `juceDir` + artefact keys from form dicts (see Dev Notes for exact keys)
  - [x] Add `@property juce_dir -> str` on `Preferences` (reads `juceDir`, returns `""` when unset)
  - [x] Update `PreferencesPage._on_save()` to call `self._prefs.apply_form(self._form.values(), self._artefacts.values())` then `save()` — **do not** pass dicts to `update(ProjectSpec)` (currently raises `AttributeError` at runtime)
  - [x] Add OS-specific placeholder to `juceDir` `FieldSpec` in `_pref_specs()` (AC: 1)

- [x] Wire `juce_dir` through generation pipeline (AC: 2)
  - [x] `MainWindow._run_generation()`: pass `juce_dir=self._prefs.juce_dir` to `ProjectGenerator.generate()`
  - [x] `ProjectGenerator.generate(spec, juce_dir="")`: forward to `render_context.build_context(spec, juce_dir=juce_dir)`
  - [x] Verify `prefs.update(spec)` on generate/open success still does **not** touch `juceDir` (AD-7)

- [x] Inject JUCE path into render context + template (AC: 3, 4)
  - [x] Add `_juce_dir_line(juce_dir: str) -> dict` in `core/render_context.py` — returns `{"juceDirSetLine": ...}`
  - [x] Update `build_context(spec, juce_dir: str = "")` signature; call `context.update(_juce_dir_line(juce_dir))`
  - [x] Insert `{juceDirSetLine}` placeholder in `Templates/CMakeLists.txt` immediately before the `# Reference JUCE:` block (line ~74)

## Dev Notes

### Scope — 6 files

| File | Change |
|------|--------|
| `core/preferences.py` | Add `juce_dir` property + `apply_form()` |
| `app/pages/preferences.py` | Fix save path; add placeholder to `juceDir` field |
| `app/main_window.py` | Pass `juce_dir=self._prefs.juce_dir` to generator |
| `core/project_generator.py` | Add `juce_dir` param; forward to `build_context` |
| `core/render_context.py` | Add `juce_dir` param + `_juce_dir_line()` |
| `Templates/CMakeLists.txt` | Add `{juceDirSetLine}` before JUCE discovery block |

**Do NOT touch:**
- `core/project_spec.py` — no `juce_dir` field (AD-7)
- `Preferences.update(spec: ProjectSpec)` mapping — keep `juceDir` absent
- `Templates/CMakeUserPresets.json` — out of scope (presets continue using `$env{JUCE_DIR}`; injected `set(JUCE_DIR)` in CMakeLists.txt satisfies cache before preset configure)
- `core/project_reader.py` — round-trip does not include `juce_dir` (AD-7)
- Any test files — Epic 3; manual verification only for this story

### Current State — Partial Implementation

| Area | Status |
|------|--------|
| `juceDir` in `_DEFAULTS` | ✅ Exists in `core/preferences.py:18` |
| UI field in Preferences tab | ✅ Exists in `app/pages/preferences.py:37-39` but **no placeholder** |
| Preferences save | ❌ **Broken** — `_on_save()` calls `update(dict)` which expects `ProjectSpec` → `AttributeError` |
| `juce_dir` property on Preferences | ❌ Missing |
| Generation wiring | ❌ `build_context(spec)` has no `juce_dir` param |
| CMakeLists injection | ❌ Template always uses ENV/platform discovery only |

### Architecture Compliance (AD-7)

```
Preferences.juce_dir  (machine-level dev environment)
        ↓ separate argument, never on ProjectSpec
MainWindow._run_generation()
        ↓
ProjectGenerator.generate(spec, juce_dir=...)
        ↓
render_context.build_context(spec, juce_dir=...)
        ↓
Templates/CMakeLists.txt  →  {juceDirSetLine}
```

- `ProjectSpec.to_dict()` / `.luthier.json` sidecar: **must not** gain a `juceDir` key
- `Preferences.update(spec)` after generate/open: **must not** overwrite `juceDir` from project data
- Only `Preferences.apply_form()` (Preferences tab save) writes `juceDir`

### `Preferences.apply_form()` — Exact Implementation

Add to `core/preferences.py`:

```python
_IDENTITY_KEYS = (
    "manufacturer", "manufacturerCode", "pluginCode",
    "companyCopyright", "companyWebsite", "companyEmail",
    "destination", "juceDir",
)

_ARTEFACT_KEYS = (
    "copyToSystemFolders", "copyToArtefactsDir",
    "artefactsDirWindows", "artefactsDirMacos", "artefactsDirLinux",
)

@property
def juce_dir(self) -> str:
    return self.get("juceDir") or ""

def apply_form(self, identity: dict, artefacts: dict) -> None:
    for key in _IDENTITY_KEYS:
        if key in identity:
            self._data[key] = identity[key]
    for key in _ARTEFACT_KEYS:
        if key in artefacts:
            self._data[key] = artefacts[key]
```

Clean code: `apply_form` is 6 lines, complexity 2. `_IDENTITY_KEYS` / `_ARTEFACT_KEYS` tuples are pure data (same precedent as `_pref_specs`).

**Why not reuse `update(ProjectSpec)`:** AD-7 forbids `juceDir` on `ProjectSpec`. The Preferences tab edits fields that span identity + environment (`juceDir`) + artefacts — a dedicated form commit method keeps boundaries clear.

### `PreferencesPage` — Placeholder + Save Fix

Add helper in `app/pages/preferences.py`:

```python
import sys

def _juce_dir_placeholder() -> str:
    if sys.platform == "win32":
        return "C:/Program Files/JUCE"
    if sys.platform == "darwin":
        return "/Applications/JUCE"
    return "/usr/local/JUCE"
```

Update `FieldSpec` for `juceDir`:

```python
FieldSpec("juceDir", "JUCE directory",
          validation.validate_optional_path,
          default=prefs.get("juceDir"),
          placeholder=_juce_dir_placeholder()),
```

Update `_on_save()`:

```python
def _on_save(self) -> None:
    if not (self._form.is_valid() and self._artefacts.is_valid()):
        self._bar.set_status("Fix the invalid fields before saving.", ok=False)
        return
    self._prefs.apply_form(self._form.values(), self._artefacts.values())
    self._prefs.save()
    self._bar.set_status("Preferences saved.", ok=True)
```

### Generation Pipeline — Exact Edits

**`app/main_window.py`** — `_run_generation()` only (AD-5: prefs.update/save unchanged):

```python
project_dir = self._generator.generate(spec, juce_dir=self._prefs.juce_dir)
```

**`core/project_generator.py`**:

```python
def generate(self, spec: ProjectSpec, juce_dir: str = "") -> Path:
    project_dir = Path(spec.destination_dir) / spec.project_name
    context = render_context.build_context(spec, juce_dir=juce_dir)
    ...
```

**`core/render_context.py`**:

```python
def build_context(spec: ProjectSpec, juce_dir: str = "") -> dict:
    d = spec.to_dict()
    ...
    context.update(_juce_dir_line(juce_dir))
    ...


def _juce_dir_line(juce_dir: str) -> dict:
    path = (juce_dir or "").strip()
    if not path:
        return {"juceDirSetLine": ""}
    return {"juceDirSetLine": f'set(JUCE_DIR "{path}")\n'}
```

**Why a single `set(JUCE_DIR "...")` line:** The existing discovery block (lines 76–87) already prioritizes `DEFINED JUCE_DIR` first. Injecting `set(JUCE_DIR "…")` before that block seeds the variable; the subsequent `if(DEFINED JUCE_DIR …)` branch picks it up. No need to replace the discovery logic.

**Windows path note:** Paths like `C:/Program Files/JUCE` use forward slashes — valid in CMake on all platforms. Backslash paths from user input may need future escaping (deferred, same class as artefact paths in story 1-4/1-5). Do not add escaping in this story.

### `Templates/CMakeLists.txt` — Exact Edit

Insert `{juceDirSetLine}` before line 74 (`# Reference JUCE:`):

```cmake
set(CMAKE_CXX_STANDARD {cxxStandard})
set(CMAKE_CXX_STANDARD_REQUIRED ON)

{juceDirSetLine}# Reference JUCE: priority cache (preset/-D), then ENV, then platform default
```

When empty: `{juceDirSetLine}` renders to nothing — comment line stays intact.
When set: renders to `set(JUCE_DIR "/Applications/JUCE")\n` — blank line before comment is acceptable (or include `\n` in helper as shown).

### Clean Code Metrics Verification

| Function | Lines | Params | Complexity |
|----------|-------|--------|------------|
| `build_context()` (updated) | 11 | 2 | 1 |
| `_juce_dir_line()` | 5 | 1 | 2 |
| `apply_form()` | 6 | 2 | 2 |
| `juce_dir` property | 2 | 1 (self) | 1 |
| `generate()` (updated) | 6 | 2 | 1 |

All within limits. ✓

### Regression Guardrails

| Behavior | Must preserve |
|----------|---------------|
| Generate with empty `juceDir` | Identical CMakeLists JUCE block to current (ENV + platform defaults) |
| Generate/open → `prefs.update(spec)` | Still does not touch `juceDir` |
| `ProjectSpec` fields | Unchanged — no new attributes |
| Story 1-5 artefact preset injection | Unaffected — separate context keys |
| AD-5 save-on-update | `MainWindow` still calls `update(spec)` + `save()` after generate/open only |

### Known Deferred Issues (Do Not Fix Here)

- Windows backslash paths in CMake `set()` strings — pre-existing (stories 1-4/1-5 deferred-work)
- `CMakeUserPresets.json` still uses `$env{JUCE_DIR}` — intentional; user can set env or rely on CMakeLists `set(JUCE_DIR)` seeding cache
- No automated tests — Epic 3
- Preferences save-on-every-keystroke — only explicit "Save Preferences" button (pre-existing UX)

### Testing

No automated tests yet (Epic 3). Manual verification:

1. `.venv/bin/python main.py --check` exits 0
2. Open Preferences tab → "JUCE directory" field visible with OS-appropriate placeholder (AC1)
3. Set JUCE directory to `/Applications/JUCE` (or valid local path) → Save Preferences → restart app → value persists (AC5)
4. Generate project with `juceDir` set → open `CMakeLists.txt`:
   - Contains `set(JUCE_DIR "/Applications/JUCE")` (or your path) before discovery block (AC3)
   - Discovery block still present below
5. Clear JUCE directory → Save Preferences → regenerate → `CMakeLists.txt` has **no** preference-injected `set(JUCE_DIR` line (AC4)
6. Inspect `.luthier.json` sidecar → no `juceDir` key (AD-7)
7. Generate project → `prefs.update(spec)` → verify `juceDir` in `preferences.json` unchanged from step 3

### References

- Story 1.6 ACs: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md) §Story 1.6
- AD-7: [_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md](_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md) §AD-7
- AD-5 prefs save pattern: [app/main_window.py](app/main_window.py) `_run_generation`, `_load_project`
- Current JUCE discovery block: [Templates/CMakeLists.txt:74-99](Templates/CMakeLists.txt)
- Partial UI (needs placeholder + save fix): [app/pages/preferences.py](app/pages/preferences.py)
- Preferences defaults (`juceDir` key): [core/preferences.py](core/preferences.py)
- Story 1-3 AD-7 enforcement: [_bmad-output/implementation-artifacts/1-3-app-layer-uses-projectspec-via-spec.md](_bmad-output/implementation-artifacts/1-3-app-layer-uses-projectspec-via-spec.md)
- Known issue #6 (juce dir not wired): [_bmad-output/project-context.md](_bmad-output/project-context.md) §Known Issues

## Dev Agent Record

### Agent Model Used

Claude (Cursor Agent)

### Debug Log References

- Fixed broken Preferences save: `_on_save()` was calling `update(dict)` which expects `ProjectSpec` → `AttributeError` at runtime
- `Preferences.update(spec)` confirmed unchanged — `juceDir` absent from candidates mapping (AD-7)

### Completion Notes List

- Added `Preferences.apply_form()`, `juce_dir` property, and `_IDENTITY_KEYS` / `_ARTEFACT_KEYS` tuples in `core/preferences.py`
- Fixed `PreferencesPage._on_save()` to use `apply_form()`; added OS-specific `_juce_dir_placeholder()` for the JUCE directory field
- Wired `juce_dir` through `MainWindow._run_generation()` → `ProjectGenerator.generate()` → `render_context.build_context()`
- Added `_juce_dir_line()` helper and `{juceDirSetLine}` placeholder in `Templates/CMakeLists.txt` before JUCE discovery block
- Verified: empty `juce_dir` produces no injected `set(JUCE_DIR)` line; non-empty injects before discovery block; `.luthier.json` has no `juceDir` key
- `.venv/bin/python main.py --check` exits 0; `pytest tests/` — 11 passed

### File List

- core/preferences.py
- app/pages/preferences.py
- app/main_window.py
- core/project_generator.py
- core/render_context.py
- Templates/CMakeLists.txt

### Change Log

- 2026-06-23: Story 1-6 — JUCE directory preference wired through generation pipeline; Preferences save fixed via `apply_form()` (AD-7)

### Review Findings

- [x] [Review][Patch] `juce_dir` property should coerce to str and strip [`core/preferences.py:71-72`]
- [x] [Review][Defer] CMake path special characters not escaped in `_juce_dir_line` [`core/render_context.py:35`] — deferred, explicitly scoped out in story spec (same class as 1-4/1-5)
- [x] [Review][Defer] No automated tests for juce_dir pipeline — deferred, Epic 3 per story spec
