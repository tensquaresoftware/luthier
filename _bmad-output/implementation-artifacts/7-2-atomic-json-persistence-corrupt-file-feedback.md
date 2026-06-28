---
baseline_commit: bdc7612f513a1f78d65d60f3e16f6eca487d25df
---

# Story 7.2: Atomic JSON Persistence & Corrupt-File Feedback

Status: done

<!-- Epic 7 — Release Hardening. Priority: SHOULD. Order: second (after 7.1). Ultimate context engine analysis completed - comprehensive developer guide created. -->

## Story

As a JUCE developer,
I want my preferences and app state saved safely and reported clearly when a config file is corrupt,
So that a crash during save never leaves me with a broken profile and I know when defaults were restored.

## Acceptance Criteria

1. **Given** `Preferences.save()` or `AppState.save()` is called, **when** the file is written, **then** content is written to a sibling temp file and atomically replaced (same commit semantics as `ProjectWriter` AD-4).
2. **Given** a corrupt or truncated `preferences.json` on startup, **when** Luthier loads preferences, **then** in-memory state falls back to factory defaults **and** a user-visible message explains that the file was reset.
3. **Given** a corrupt `app_state.json`, **when** Luthier loads app state, **then** defaults apply and the user is notified similarly.
4. **Given** unit tests with `tmp_path`, **when** a simulated crash occurs after temp write but before rename, **then** the original JSON file content is unchanged.
5. **Given** Epic 7.2 completion, **when** architecture docs are inspected, **then** AD-10 documents atomic JSON persistence for app config.

**Deferred:** schema `version` field for migrations — not blocking QA week.

## Tasks / Subtasks

- [x] Add shared atomic JSON write helper (AC: 1, 4)
  - [x] New `core/json_files.py` with `atomic_write_text(path: Path, content: str) -> None`
  - [x] Temp path: sibling file `{name}.tmp` (e.g. `preferences.json.tmp`) in same directory
  - [x] On failure after temp write: delete temp file, re-raise; **never** truncate the live file
  - [x] Wire into `Preferences.save()` and `AppState.save()`

- [x] Corrupt-load detection + core signals (AC: 2, 3)
  - [x] `Preferences`: add `load_warning: str | None` property (mirror `accent_color_warning` pattern)
  - [x] `AppState`: add `load_warning: str | None` property
  - [x] Treat as corrupt: `JSONDecodeError`, read `OSError`, non-`dict` root after parse
  - [x] On corrupt prefs: `factory_defaults()` + `accentColor` default + `save()` clean file + set `load_warning`
  - [x] On corrupt app state: reset internal defaults + `save()` clean file + set `load_warning`
  - [x] **Do not** notify for `validate_profile` failure alone (valid JSON, bad values) — existing auto-correct + optional `accent_color_warning` unchanged

- [x] App-layer user feedback (AC: 2, 3)
  - [x] `MainWindow.__init__`: after `ensure_initialized()` / `app_state.load()`, surface warnings via `_set_status(..., ok=False)`
  - [x] Priority: generator error → corrupt config warnings → accent warning (existing order extended)
  - [x] If both prefs and app_state corrupt, combine into one status message (two short sentences)
  - [x] No Qt imports in `core/`

- [x] Unit tests (AC: 4)
  - [x] Extend `tests/unit/test_preferences.py` — atomic save, corrupt load, crash simulation
  - [x] Extend `tests/unit/test_app_state.py` — same scenarios
  - [x] Optional: `tests/unit/test_json_files.py` for helper in isolation
  - [x] Use `tmp_path`; mock `Path.replace` to simulate crash; assert original bytes unchanged
  - [x] No Qt event loop required

- [x] Documentation (AC: 5)
  - [x] Add **AD-10** section to `docs/architecture.md` (spine already has AD-10)
  - [x] Update `preferences.py` / `app_state.py` rows in module contracts table
  - [x] Strike JSON persistence items in `_bmad-output/implementation-artifacts/deferred-work.md`

- [x] Regression
  - [x] Full suite: `.venv/bin/pytest` (202+ passed baseline from 7.1)
  - [x] AD-5 unchanged: Open/Generate still never write `preferences.json`

## Dev Notes

### Epic 7 context

Epic 7 is the post-MVP quality gate before manual QA (week of 2026-07-07). Story 7.1 (CI) is **done**. This story closes deferred JSON persistence debt from Story 5.4 code review (`[Review][Defer]` on non-atomic write and silent corrupt load).

| Story | Scope |
|-------|-------|
| 7.1 | GitHub Actions pytest CI — **done** |
| **7.2** | Atomic prefs + app_state JSON; corrupt-file feedback |
| 7.3 | Generation/reload edge cases (CMake quoting, sidecar validation) |
| 7.4 | Test hygiene + minor UI hardening |

### Current implementation — MUST replace

**Non-atomic direct write (both modules):**

```183:185:core/preferences.py
    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
```

```66:68:core/app_state.py
    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
```

**Silent corrupt read — prefs:**

```257:261:core/preferences.py
    def _read(self) -> dict:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
```

When `_read()` returns `{}` for a corrupt existing file, `load()` may leave factory-ish in-memory state, **pass** `validate_profile`, and **never rewrite** the corrupt file on disk — user sees no feedback. This bug must be fixed as part of AC2.

**Silent corrupt read — app state:**

```42:48:core/app_state.py
    def load(self) -> None:
        if not self._path.exists():
            return
        try:
            loaded = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
```

Same silent swallow — fix for AC3.

### Recommended implementation

#### 1. `core/json_files.py` (new)

```python
def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (path.name + ".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise
```

**Why a file temp, not a directory:** AD-4 uses a temp **directory** because `ProjectWriter` writes many files. Config JSON is a **single file** — sibling `{filename}.tmp` + `Path.replace()` is the standard atomic pattern (uses `os.replace`, atomic on same filesystem).

**Do not** reuse `ProjectWriter`'s directory-rename logic for JSON — wrong abstraction.

Keep helper ≤15 lines (clean-code rule). Both `save()` methods become thin wrappers calling `atomic_write_text(self._path, json.dumps(...))`.

#### 2. Load warning constants (module-level strings in `core/`)

Suggested messages (English — user-facing UI strings in codebase are English):

- Prefs: `"Preferences file was corrupt and has been reset to defaults."`
- App state: `"App state file was corrupt and has been reset to defaults."`

Expose via read-only properties; cleared at start of each `load()`.

#### 3. `Preferences.load()` corrupt path

When file exists and read fails or root is not `dict`:

1. Set `load_warning` to prefs message
2. `self._data = factory_defaults()` (+ accent default handling per existing logic)
3. `self.save()` to replace corrupt file atomically
4. Do **not** set `load_warning` when file is simply missing (first-run path uses `ensure_initialized()`)

Preserve existing branches for invalid-but-parseable JSON (`validate_profile` fails) and `accent_color_warning` — orthogonal concerns.

#### 4. `AppState.load()` corrupt path

When file exists and read fails or root is not `dict`:

1. Set `load_warning`
2. Reset `_data` to constructor defaults (empty strings / `None` / `False`)
3. `save()` clean file

#### 5. `MainWindow` bootstrap

Existing startup in `__init__`:

```74:95:app/main_window.py
        self._prefs = prefs or Preferences(Preferences.default_path())
        self._prefs.ensure_initialized()
        ...
        self._app_state = AppState(AppState.default_path())
        self._app_state.load()
        ...
        if self._generator.error:
            self._set_status(self._generator.error, ok=False)
        elif self._prefs.accent_color_warning:
            self._set_status(self._prefs.accent_color_warning, ok=False)
```

Insert corrupt-config check **before** accent warning:

```python
config_warnings = [w for w in (self._prefs.load_warning, self._app_state.load_warning) if w]
if self._generator.error:
    self._set_status(self._generator.error, ok=False)
elif config_warnings:
    self._set_status(" ".join(config_warnings), ok=False)
elif self._prefs.accent_color_warning:
    ...
```

`main.py` passes the same `prefs` instance into `MainWindow(prefs)` — corrupt prefs detected in `ensure_initialized()` → `load()` will surface once in MainWindow. No duplicate status needed in `main.py`.

### Architecture compliance

| AD | Requirement | This story |
|----|-------------|------------|
| AD-4 | Temp-then-commit write semantics | Same semantics via file `.tmp` + `replace()` |
| AD-5 | Prefs save triggers unchanged | Only auto-save, import, factory init — verify no new save paths |
| AD-10 | Atomic JSON + corrupt feedback | Primary deliverable |
| AD-6 | No MainWindow widget tests | Unit-test `core/` only |
| Error propagation | `core/` exposes warnings; `MainWindow` displays | Follow spine convention |

**Out of scope:** `templates_store.save_override()` (user C++ templates), `.luthier.json` sidecar (Story 7.3), JSON schema versioning.

### File structure requirements

| File | Action |
|------|--------|
| `core/json_files.py` | **NEW** — `atomic_write_text` |
| `core/preferences.py` | **UPDATE** — `save()`, `_read()`/`load()`, `load_warning` |
| `core/app_state.py` | **UPDATE** — `save()`, `load()`, `load_warning` |
| `app/main_window.py` | **UPDATE** — startup status for corrupt config |
| `tests/unit/test_preferences.py` | **UPDATE** — new tests |
| `tests/unit/test_app_state.py` | **UPDATE** — new tests |
| `docs/architecture.md` | **UPDATE** — AD-10 section + module table |
| `_bmad-output/implementation-artifacts/deferred-work.md` | **UPDATE** — remove struck JSON items |

**Do not modify:** `ProjectWriter`, `project_reader`, `templates_store`, CI workflow.

### Testing requirements

**Crash simulation (AC4):**

```python
original = path.read_bytes()
with patch.object(Path, "replace", side_effect=OSError("simulated crash")):
    with pytest.raises(OSError):
        prefs.save()
assert path.read_bytes() == original
assert (path.parent / (path.name + ".tmp")).exists() is False  # temp cleaned up
```

**Atomic write happy path:** after `save()`, assert `(path.parent / (path.name + ".tmp")).exists()` is False and JSON parses.

**Corrupt load prefs:** write `"{ truncated"` to file → `load()` → `load_warning` set, `factory_defaults()` in memory, file on disk valid JSON.

**Corrupt load app state:** write `"not json"` → `load()` → `load_warning` set, defaults restored.

**Regression guards:**

- `test_app_state_save_does_not_touch_preferences_json` — must still pass
- `test_load_invalid_accent_corrects_file_and_sets_warning` — accent path unchanged
- `test_accent_color_survives_invalid_profile_reset` — valid JSON partial corrupt still works

Run: `.venv/bin/pytest tests/unit/test_preferences.py tests/unit/test_app_state.py` then full suite.

### Previous story intelligence (7.1)

From `7-1-github-actions-ci-for-pytest.md`:

- CI runs on `ubuntu-latest` with Qt offscreen deps — new unit tests must pass in CI without GUI
- Baseline: **202 passed, 2 skipped** locally; keep green
- Review pattern: document non-obvious CI deps in CONTRIBUTING when touching test infra (not required for pure `core/` unit tests)
- Path normalization: use forward slashes in test path assertions (`normalize_portable_path` convention)

### Git intelligence

Recent commits on `main` are doc/epic-7 planning (7.1 merged via PR #1). No in-flight code changes for 7.2 yet — greenfield implementation on current `core/preferences.py` / `core/app_state.py`.

### Latest technical information

- **Python 3.14** / **cp310-abi3**: `pathlib.Path.replace()` delegates to `os.replace()` — atomic replacement when temp and target share a filesystem (always true for sibling `.tmp` in same directory).
- **Pattern:** write complete content to temp → `replace()` is the standard alternative to write-in-place; avoids torn reads if another process reads mid-write.
- **Windows note:** `os.replace` overwrites destination atomically on Windows 10+; same pattern already relied on implicitly for project dir renames in AD-4.
- **No new dependencies** — stdlib only per project stack rules.

### Project context reference

From `_bmad-output/project-context.md`:

- All file I/O: `encoding="utf-8"` explicitly
- `QStandardPaths` for config paths — unchanged
- Function ≤15 lines; extract helper rather than bloating `save()`/`load()`
- No comments referencing story numbers
- Git commits: English only

Persistence locations (runtime):

| File | Path (macOS) | Written by |
|------|--------------|------------|
| `preferences.json` | `~/Library/Preferences/Luthier/preferences.json` | Factory, Preferences auto-save, Import |
| `app_state.json` | sibling | Generate, Import/Export paths, window geometry |

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 7, Story 7.2]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` — AD-4, AD-10]
- [Source: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-06-28.md` — § Story 7.2, deferred-work mapping]
- [Source: `_bmad-output/implementation-artifacts/deferred-work.md` — Persistance JSON section]
- [Source: `_bmad-output/implementation-artifacts/5-4-decouple-open-generate-from-preferences-json.md` — `[Review][Defer]` items this story closes]
- [Source: `core/project_writer.py` — AD-4 reference implementation]
- [Source: `app/main_window.py` — `accent_color_warning` status pattern]

### Review Findings

- [x] [Review][Patch] Prefs `load_warning` cleared before status bar reads it [app/main_window.py:75, core/preferences.py:174-175] — fixed via `_initialized` guard on `ensure_initialized()` so second call in `MainWindow` is a no-op.
- [x] [Review][Patch] `_reset_corrupt_file()` save failure can crash startup [core/preferences.py:205-209, core/app_state.py:88-91] — fixed: `save()` wrapped in try/except `OSError`; warning and in-memory defaults retained.
- [x] [Review][Patch] Missing test for read `OSError` corrupt path [tests/unit/test_preferences.py, tests/unit/test_app_state.py] — added `test_load_read_oserror_resets_and_sets_warning` in both modules.
- [x] [Review][Patch] Missing regression assert that `validate_profile` failure does not set `load_warning` [tests/unit/test_preferences.py] — assert added to `test_accent_color_survives_invalid_profile_reset`.
- [x] [Review][Defer] No `fsync` after temp write [core/json_files.py:10] — deferred, pre-existing; AD-4 `ProjectWriter` uses same durability level; out of scope for 7.2.
- [x] [Review][Defer] Orphaned `.tmp` after SIGKILL or power loss [core/json_files.py:8] — deferred, pre-existing; inherent atomic-write limitation; no recovery path documented beyond manual cleanup.

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-sonnet-medium-thinking (Cursor)

### Debug Log References

- Full suite: `python3 -m pytest` → 214 passed, 2 skipped (baseline 202 + 12 new tests)

### Completion Notes List

- Added `core/json_files.atomic_write_text()` — sibling `.tmp` + `Path.replace()` with cleanup on failure.
- `Preferences` and `AppState` now save atomically; corrupt load resets defaults, rewrites clean file, exposes `load_warning`.
- `MainWindow` startup surfaces corrupt-config warnings before accent warnings; combined message when both files corrupt.
- AD-10 section added to `docs/architecture.md`; deferred-work JSON items struck (version field remains open).
- Existing accent/validate_profile paths unchanged for valid JSON with bad values.

### File List

- `core/json_files.py` (new)
- `core/preferences.py`
- `core/app_state.py`
- `app/main_window.py`
- `tests/unit/test_json_files.py` (new)
- `tests/unit/test_preferences.py`
- `tests/unit/test_app_state.py`
- `docs/architecture.md`
- `_bmad-output/implementation-artifacts/deferred-work.md`

### Change Log

- 2026-06-28: Atomic JSON persistence for preferences/app_state; corrupt-load feedback via `load_warning` and status bar (Story 7.2).
