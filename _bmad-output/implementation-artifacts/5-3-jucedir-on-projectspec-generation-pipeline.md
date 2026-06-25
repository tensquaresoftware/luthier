---
baseline_commit: aec1e2e
---

# Story 5.3: juceDir on ProjectSpec & Generation Pipeline

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer,
I want the JUCE directory stored on my project and round-tripped in `.luthier.json`,
So that each project can target a different JUCE version and reload faithfully.

## Acceptance Criteria

1. **Given** `ProjectSpec`, **when** serialized via `to_dict()` / `.luthier.json`, **then** `juceDir` is included and restored by `from_dict()`.
2. **Given** a non-empty `spec.juce_dir`, **when** `ProjectGenerator.generate(spec)` runs, **then** `render_context.build_context(spec)` emits the `set(JUCE_DIR "...")` line from `spec.juce_dir` — no separate `juce_dir=` argument.
3. **Given** empty `spec.juce_dir`, **when** generation runs, **then** no preference-injected JUCE line appears (CMake discovery applies).
4. **Given** generate → open → regenerate without changes, **when** `.luthier.json` is compared, **then** `juceDir` round-trips with empty diff on all sidecar fields.
5. **Given** unit and integration tests, **when** pytest runs, **then** tests use `generate(spec)` without `juce_dir=` parameter; AD-7 empty-string workarounds removed where obsolete.
6. **Given** `tests/unit/test_project_spec.py` (or equivalent), **when** `ProjectSpec.from_dict(spec.to_dict())` runs on a spec with non-empty `juce_dir`, **then** `juceDir` round-trips in the dict and the reconstructed spec matches on all fields.

## Tasks / Subtasks

- [x] Add `juce_dir` to `ProjectSpec` (AC: 1, 6)
  - [x] Add field `juce_dir: str = ""` after `destination_dir` in `core/project_spec.py`
  - [x] Add `"juceDir": self.juce_dir` in `to_dict()`
  - [x] Add `juce_dir=d.get("juceDir", "")` in `from_dict()`
  - [x] Mirror `destination_dir` / `destinationDir` naming pattern exactly

- [x] Move JUCE path source from parameter to spec in render pipeline (AC: 2, 3)
  - [x] Change `build_context(spec: ProjectSpec) -> dict` — remove `juce_dir=` parameter
  - [x] Call `_juce_dir_line(spec.juce_dir)` instead of `_juce_dir_line(juce_dir)`
  - [x] Keep `_juce_dir_line()` logic unchanged: strip whitespace; empty → `{"juceDirSetLine": ""}`; non-empty → `set(JUCE_DIR "...")\n`
  - [x] **Do not** fall back to `Preferences.juce_dir` inside `core/` — empty spec means empty line (CMake env/platform discovery in `Templates/CMakeLists.txt`)

- [x] Simplify `ProjectGenerator.generate` signature (AC: 2, 5)
  - [x] `generate(self, spec: ProjectSpec) -> Path` — drop `juce_dir` parameter
  - [x] `context = render_context.build_context(spec)` — no second argument

- [x] Stop prefs injection at generate time in `MainWindow` (AC: 2, 3)
  - [x] `_run_generation`: change `self._generator.generate(spec, juce_dir=self._prefs.juce_dir)` → `self._generator.generate(spec)`
  - [x] **Do not** remove `prefs.update(spec)` / `prefs.save()` here — Story 5.4

- [x] Update unit tests (AC: 5, 6)
  - [x] `tests/unit/test_project_spec.py`: add `test_juce_dir_round_trip_non_empty` with path like `/Applications/JUCE`
  - [x] Existing `test_to_dict_from_dict_round_trip_all_fields` auto-covers field once added (uses `fields(ProjectSpec)`)
  - [x] `tests/unit/test_render_context.py`: rewrite `test_build_context_juce_dir_empty` and `test_build_context_juce_dir_set` to set `spec.juce_dir` on the spec — remove `juce_dir=` second arg from all `build_context()` calls

- [x] Update integration tests and conftest (AC: 4, 5)
  - [x] `tests/conftest.py`: remove `juce_dir` from `generate_project()` signature and call
  - [x] `tests/integration/test_round_trip.py`: remove all `juce_dir=""` from `generator.generate()` calls
  - [x] Add `test_juce_dir_sidecar_round_trip`: generate with `juce_dir="/tmp/juce-test"`, assert `.luthier.json` contains `"juceDir"`, `read_project` restores it
  - [x] Add `test_regenerate_preserves_juce_dir`: generate with non-empty `juce_dir`, read, regenerate, assert sidecar `juceDir` unchanged and `CMakeLists.txt` still contains `set(JUCE_DIR "/tmp/juce-test")`
  - [x] `tests/test_story_2_1.py`, `tests/test_story_2_2.py`: remove `juce_dir=""` from `generate()` calls

- [x] Regression
  - [x] `.venv/bin/pytest` — full suite green
  - [x] Grep codebase for `juce_dir=` on `generate(` or `build_context(` — zero hits outside docs/planning artifacts

## Dev Notes

### Scope — Core/Pipeline Only (Not Project Tab UI)

Story 5.3 owns **data model + generation pipeline**. Story 5.2 (`ready-for-dev`) owns Project tab `FolderField` for JUCE directory. Until 5.2 lands, tests set `juce_dir` directly on `ProjectSpec`; production UI still lacks a Project tab field but generate will read `spec.juce_dir` (empty unless set programmatically or after 5.2).

**Recommended epic order:** 5.1 ✅ → **5.3** → 5.2 → 5.4 → 5.5. Story 5.2 AC5 depends on this story's `ProjectSpec.juce_dir`.

### Current State — Gap Analysis

| Area | Today (post 5.1) | Target (5.3) |
|------|------------------|--------------|
| `ProjectSpec.juce_dir` | **Missing** from dataclass | Field + `juceDir` in dict/sidecar |
| `.luthier.json` | No `juceDir` key | Full spec includes `juceDir` |
| `build_context(spec, juce_dir=)` | Separate param from caller | `build_context(spec)` reads `spec.juce_dir` |
| `generate(spec, juce_dir=)` | Separate param | `generate(spec)` only |
| `MainWindow._run_generation` | `juce_dir=self._prefs.juce_dir` | `generate(spec)` — prefs not read at generate |
| `Preferences.juce_dir` | Used at generate time | **Seed only** (startup / Create New Project) |
| Tests | `juce_dir=""` workaround everywhere | Spec field only |

### Architecture Compliance

**AD-1:** `ProjectSpec` remains the sole cross-layer contract. Adding `juce_dir` extends the contract; no raw dicts at generate boundary.

**AD-2:** `ProjectSpec` carries `juce_dir` alongside `destination_dir`. Per-project JUCE path is project data, not global prefs.

**AD-3:** Sidecar is `spec.to_dict()` written by `ProjectWriter._write_sidecar()`. Adding `juceDir` to `to_dict()` automatically persists it. `project_reader` uses `ProjectSpec.from_dict()` — **no reader changes required**. CMake regex fallback does not parse `JUCE_DIR` — legacy projects without sidecar get empty `juce_dir` (acceptable).

**AD-5 (not in scope):** Open/Generate still call `prefs.update(spec)` + `save()` — leave unchanged until Story 5.4.

**AD-7 (revised — this story implements it):** `ProjectSpec.juce_dir` is authoritative at generate. `Preferences.juce_dir` is default seed via `seed_dict()` only. `render_context.build_context(spec)` — no separate `juce_dir=` parameter.

**AD-6:** No Qt tests. All changes testable via pure unit + `tmp_path` integration tests.

**AD-8:** All edits in `core/` + one line in `app/main_window.py`. No new Qt imports in `core/`.

### Files to Touch

| File | Change |
|------|--------|
| `core/project_spec.py` | Add `juce_dir` field + dict mapping |
| `core/render_context.py` | Remove `juce_dir=` param; read `spec.juce_dir` |
| `core/project_generator.py` | Remove `juce_dir=` param |
| `app/main_window.py` | `generate(spec)` without prefs injection |
| `tests/unit/test_project_spec.py` | Explicit non-empty `juceDir` round-trip test |
| `tests/unit/test_render_context.py` | Assert via `spec.juce_dir`, not second arg |
| `tests/conftest.py` | Remove `juce_dir` from `generate_project()` |
| `tests/integration/test_round_trip.py` | Remove workarounds; add `juceDir` sidecar tests |
| `tests/test_story_2_1.py` | Remove `juce_dir=""` |
| `tests/test_story_2_2.py` | Remove `juce_dir=""` |

### Do NOT Touch in This Story

| File | Reason |
|------|--------|
| `app/pages/project_info.py`, `app/pages/project.py` | Project tab JUCE `FolderField` — Story 5.2 |
| `core/preferences.py` | `seed_dict()` already has `juceDir`; `update()` sync removal — Story 5.4 |
| `core/project_reader.py` | Sidecar path already uses `from_dict()`; CMake `JUCE_DIR` parse not in AC |
| `core/project_writer.py` | Already writes full `to_dict()` — no change needed |
| `Templates/CMakeLists.txt` | `{juceDirSetLine}` placeholder already exists (line 74) |
| `_bmad-output/project-context.md`, `ARCHITECTURE-SPINE.md` | Doc sync after 5.4 when AD-5 lands in code |

### Implementation Details — `ProjectSpec`

Follow existing field pattern in `core/project_spec.py`:

```python
# After destination_dir:
juce_dir: str = ""

# to_dict:
"juceDir": self.juce_dir,

# from_dict:
juce_dir=d.get("juceDir", ""),
```

`test_to_dict_from_dict_round_trip_all_fields` iterates `dataclasses.fields(ProjectSpec)` — new field is covered automatically. Add explicit test with non-empty path for AC6 clarity.

### Implementation Details — `render_context`

Current (to remove):

```python
def build_context(spec: ProjectSpec, juce_dir: str = "") -> dict:
    ...
    context.update(_juce_dir_line(juce_dir))
```

Target:

```python
def build_context(spec: ProjectSpec) -> dict:
    ...
    context.update(_juce_dir_line(spec.juce_dir))
```

`_juce_dir_line()` stays private and unchanged. Template `Templates/CMakeLists.txt` line 74:

```
{juceDirSetLine}# Reference JUCE: priority cache (preset/-D), then ENV, then platform default
```

When `juceDirSetLine` is empty, CMake falls through to `ENV{JUCE_DIR}` and platform defaults (`/Applications/JUCE`, etc.).

### Implementation Details — `MainWindow`

Current (`app/main_window.py` ~line 256):

```python
project_dir = self._generator.generate(spec, juce_dir=self._prefs.juce_dir)
```

Target:

```python
project_dir = self._generator.generate(spec)
```

**Critical:** Do not substitute `spec.juce_dir or self._prefs.juce_dir` — AC3 requires empty spec → no injected line, not prefs fallback.

Until Story 5.2 wires Project tab UI, `spec.juce_dir` will be `""` for manual Generate from UI. Users relying on prefs JUCE path at generate time will see behavior change until 5.2 is done — acceptable per epic ordering (5.3 before 5.2 is recommended; if 5.2 ships first, `ProjectPage.spec()` will populate `juceDir` from the folder field).

### Sidecar Round-Trip (Automatic)

`ProjectWriter._write_sidecar()`:

```python
json.dumps(spec.to_dict(), indent=2, ensure_ascii=False)
```

Once `juceDir` is in `to_dict()`, sidecar persistence is free. `project_reader._read_sidecar()` injects `destinationDir` from disk path then calls `from_dict()` — `juceDir` restores from JSON as-is.

### Test Patterns

**Unit — `test_project_spec.py`:**

```python
def test_juce_dir_round_trip_non_empty():
    original = _make_spec(juce_dir="/Applications/JUCE")
    restored = ProjectSpec.from_dict(original.to_dict())
    assert restored.juce_dir == "/Applications/JUCE"
    _assert_fields_equal(restored, original)
    assert original.to_dict()["juceDir"] == "/Applications/JUCE"
```

**Unit — `test_render_context.py` (rewrite existing tests):**

```python
def test_build_context_juce_dir_empty():
    spec = _make_spec(juce_dir="")
    assert build_context(spec)["juceDirSetLine"] == ""
    spec_whitespace = _make_spec(juce_dir="   ")
    assert build_context(spec_whitespace)["juceDirSetLine"] == ""

def test_build_context_juce_dir_set():
    spec = _make_spec(juce_dir="/Applications/JUCE")
    line = build_context(spec)["juceDirSetLine"]
    assert line == 'set(JUCE_DIR "/Applications/JUCE")\n'
```

**Integration — new test in `test_round_trip.py`:**

```python
def test_juce_dir_sidecar_round_trip(tmp_path):
    from core import project_reader

    juce_path = "/tmp/juce-test"
    spec = make_spec(tmp_path, juce_dir=juce_path)
    project_dir, _ = generate_project(tmp_path, spec=spec)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert data["juceDir"] == juce_path
    loaded = project_reader.read_project(project_dir)
    assert loaded is not None
    assert loaded.juce_dir == juce_path
```

Ensure `make_spec()` in `conftest.py` accepts `juce_dir` kwarg (pass through to `ProjectSpec`).

**Integration — regenerate with juce_dir:**

```python
def test_regenerate_preserves_juce_dir(tmp_path):
    from core import project_reader
    from core.project_generator import ProjectGenerator

    juce_path = "/Applications/JUCE"
    spec = make_spec(tmp_path, juce_dir=juce_path)
    generator = ProjectGenerator()
    project_dir = generator.generate(spec)
    cmake_before = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert f'set(JUCE_DIR "{juce_path}")' in cmake_before

    loaded = project_reader.read_project(project_dir)
    assert loaded is not None
    generator.generate(loaded)
    sidecar = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    assert sidecar["juceDir"] == juce_path
```

### Cross-Story Dependencies

| Story | Relationship |
|-------|--------------|
| 5.1 | **Done** — `Preferences.juce_dir`, `seed_dict()["juceDir"]`, Preferences UI `FolderField` |
| 5.2 | **Blocked on 5.3 for AC5** — Project tab JUCE field emits `juceDir` into `ProjectPage.spec()` |
| 5.4 | Removes `prefs.update()` / `save()` on Open/Generate; decouples prefs persistence |
| 5.5 | Create New Project re-seeds from `seed_dict()` including `juceDir` |

### Previous Story Intelligence

**5.1 (done):** `Preferences.seed_dict()` already returns `"juceDir": self.get("juceDir")` for new-project seeding. `validate_optional_path` validates JUCE path. `FolderField` exists for Preferences tab. Do not regress import/export or auto-save.

**5.2 (ready-for-dev, not implemented):** Planned to add `FolderField` on Project tab and `_seed_new_project()`. Story 5.2 dev notes say: if implementing 5.2 standalone, add minimal `ProjectSpec.juce_dir` slice — **5.3 delivers that slice plus full pipeline switch**. After 5.3, 5.2 can wire UI knowing `spec().juce_dir` round-trips and generate reads it.

### Git Intelligence

Recent commits (baseline `aec1e2e`):
- `aec1e2e` — Export live preferences profile only when form is valid (5.1 review fix)
- `93c0bc3` — Preferences profile workflow with auto-save and import/export (5.1)
- No Epic 5.3 code yet; `project_spec.py` has 21 fields, no `juce_dir`
- All `generate()` call sites pass `juce_dir=` explicitly or via prefs

### Latest Tech Information

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- CMake `JUCE_DIR` discovery chain unchanged in template — only the optional `set(JUCE_DIR "...")` prefix line is spec-driven
- No library version changes required for this story

### Project Structure Notes

- Primary edits: `core/project_spec.py`, `core/render_context.py`, `core/project_generator.py`, `app/main_window.py`
- Test edits: `tests/unit/`, `tests/integration/`, `tests/conftest.py`, story regression files
- Run tests: `.venv/bin/pytest`
- Run app: `.venv/bin/python main.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.3]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md#AD-2, #AD-3, #AD-7]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-06-25.md#Story-5.3]
- [Source: _bmad-output/implementation-artifacts/5-1-preferences-model-profile-workflow.md]
- [Source: _bmad-output/implementation-artifacts/5-2-project-ui-choose-buttons-layout.md — prerequisite notes]
- [Source: core/project_spec.py — add field here]
- [Source: core/render_context.py — `_juce_dir_line()`]
- [Source: core/project_generator.py — `generate()` signature]
- [Source: app/main_window.py — `_run_generation`]
- [Source: Templates/CMakeLists.txt#line-74 — `{juceDirSetLine}`]
- [Source: tests/conftest.py — `generate_project()` helper]

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-sonnet-medium-thinking

### Debug Log References

### Completion Notes List

- Added `juce_dir` field to `ProjectSpec` with `juceDir` camelCase dict mapping; sidecar round-trip is automatic via existing `to_dict()` / `from_dict()` pipeline.
- Removed separate `juce_dir=` parameter from `build_context()`, `ProjectGenerator.generate()`, and `MainWindow._run_generation()` — generation now reads `spec.juce_dir` exclusively (AD-7 revised).
- Updated unit tests (`test_project_spec`, `test_render_context`) and integration tests (`test_round_trip`, story 2.1/2.2 regressions); added `test_juce_dir_sidecar_round_trip` and `test_regenerate_preserves_juce_dir`.
- Full pytest suite: 123 passed, 0 failed. Grep confirms zero `juce_dir=` on `generate(` / `build_context(` in Python source.

### File List

- core/project_spec.py
- core/render_context.py
- core/project_generator.py
- app/main_window.py
- tests/unit/test_project_spec.py
- tests/unit/test_render_context.py
- tests/conftest.py
- tests/integration/test_round_trip.py
- tests/test_story_2_1.py
- tests/test_story_2_2.py

### Change Log

- 2026-06-25: Story 5.3 — `juce_dir` on ProjectSpec; generation pipeline reads spec field; prefs no longer injected at generate time.

### Review Findings

- [x] [Review][Patch] Renforcer `test_regenerate_preserves_juce_dir` — ajouter assertion CMake post-regenerate et égalité sidecar complète avant/après (AC4 / task ligne 57) [tests/integration/test_round_trip.py:149]

- [x] [Review][Defer] Generate UI sans injection prefs `juceDir` [app/main_window.py:256] — deferred, comportement attendu AD-7 / epic ordering 5.3 avant 5.2
- [x] [Review][Defer] Open → Generate perd `juceDir` côté UI [app/pages/project.py:43-49] — deferred, Story 5.2 (ProjectPage FolderField + `spec()`)
- [x] [Review][Defer] Regenerate après lecture CMake-only supprime ligne `JUCE_DIR` [core/project_generator.py:39] — deferred, spec: pas de parse `JUCE_DIR` dans `project_reader`
- [x] [Review][Defer] `from_dict` avec `juceDir: null` en JSON [core/project_spec.py:66] — deferred, pattern pré-existant sur tous les champs (story 1-1)
- [x] [Review][Defer] Échappement chemins spéciaux dans `_juce_dir_line` [core/render_context.py:35] — deferred, pré-existant depuis story 1-6
- [x] [Review][Defer] Sidecar whitespace-only vs CMake vide [core/project_spec.py:66] — deferred, hors AC ; normalisation optionnelle
