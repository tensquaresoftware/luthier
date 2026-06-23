---
baseline_commit: d4ecf73
---

# Story 3.4: Integration Tests — Project Generation Round-Trip

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer (Guillaume),
I want integration tests that verify the full `ProjectSpec → generate → read` cycle,
so that any regression in round-trip fidelity is caught automatically without manual testing.

## Acceptance Criteria

1. **Given** `tests/integration/test_round_trip.py` using `tmp_path`, **when** `ProjectWriter.write(context, tokens, tmp_path / "project")` runs with a known `ProjectSpec`, **then** the output directory contains `CMakeLists.txt`, `CMakeUserPresets.json`, `.luthier.json`, and the 4 source files under `Source/`.
2. **Given** the written project directory, **when** `project_reader.read_project(dest)` is called, **then** the returned `ProjectSpec` equals the original on all fields.
3. **Given** the `.luthier.json` sidecar is deleted from the output directory, **when** `project_reader.read_project(dest)` is called using the CMake fallback, **then** it returns either a complete `ProjectSpec` (if CMake parsing succeeds) or `None` — never a partial spec.
4. **Given** a generated `CMakeLists.txt`, **when** its content is inspected, **then** no reference to `project-configuration.cmake` appears.

## Tasks / Subtasks

- [x] Add `tests/conftest.py` with shared integration helpers (recommended — deferred from 3-1/3-2/3-3)
  - [x] `make_spec(tmp_path, **kwargs) -> ProjectSpec` — canonical populated spec; `destination_dir=str(tmp_path)` by default
  - [x] `all_files(root: Path) -> dict[Path, bytes]` — recursive byte snapshot for regenerate diff
  - [x] `assert_spec_equal(actual, expected)` — field-by-field via `dataclasses.fields`
  - [x] `write_project(tmp_path, spec, *, overrides=None) -> tuple[Path, ProjectSpec]` — low-level `ProjectWriter` path
  - [x] `generate_project(tmp_path, spec=None, *, overrides=None, juce_dir="") -> tuple[Path, ProjectSpec]` — high-level `ProjectGenerator` path

- [x] Add `tests/integration/test_round_trip.py` (AC: 1–4)
  - [x] `test_writer_output_contains_required_files` — low-level `ProjectWriter.write`; assert AC1 paths exist (AC: 1)
  - [x] `test_read_project_returns_equivalent_spec` — generate → `read_project` → `assert_spec_equal` on all fields (AC: 2)
  - [x] `test_sidecar_json_round_trip` — read `.luthier.json` text → `json.loads` → `ProjectSpec.from_dict` → equals original (closes 3-3 deferral)
  - [x] `test_regenerate_produces_identical_tree` — `ProjectGenerator.generate` → read → regenerate → byte-for-byte file tree (from `test_story_2_1::TestRoundTrip`)
  - [x] `test_cmake_fallback_returns_complete_spec` — delete sidecar → `read_project_result` → full field equality, `missing_fields == ()` (AC: 3)
  - [x] `test_cmake_fallback_regenerate_identical_tree` — delete sidecar → read → regenerate → byte-for-byte (from `test_story_2_2`)
  - [x] `test_partial_cmake_returns_none_not_partial_spec` — strip `COMPANY_NAME` → `spec is None`, `"Company Name" in missing_fields` (AC: 3)
  - [x] `test_no_cmakelists_returns_none` — empty dir → `read_project_result` → `spec is None`
  - [x] `test_generated_cmakelists_has_no_project_configuration_reference` — assert substring absent in `CMakeLists.txt` only (AC: 4)
  - [x] Optional: `test_template_override_applied_at_generation` — custom `PluginProcessor.h` in overrides dir appears in output (AD-9)
  - [x] Optional: `test_legacy_project_configuration_cmake_compat` — port from `test_story_2_2` if not redundant with unit coverage

- [x] Regression guard
  - [x] `.venv/bin/pytest` — full suite green (100 existing pytest + new integration tests)
  - [x] `.venv/bin/python -m unittest discover -s tests -v` still passes (legacy `test_story_*.py` unchanged)
  - [x] Integration tests import only `core/*` — no Qt modules loaded (AD-6 / AD-8)

## Dev Notes

### Gap Analysis — What Exists vs. What This Story Adds

| Component | Current state (post story 3-3) | This story |
|-----------|-------------------------------|------------|
| `tests/integration/` | Empty scaffold (`__init__.py` only) | **`test_round_trip.py`** — formal pytest integration tier |
| Round-trip coverage | Legacy **unittest** in `test_story_2_1.py`, `test_story_2_2.py` | **Pytest** equivalents under `tests/integration/` per AD-6 |
| `tests/conftest.py` | Does not exist (deferred since 3-1) | **New** — shared `make_spec`, `all_files`, `assert_spec_equal` |
| Sidecar JSON I/O | Unit tests `to_dict`/`from_dict` only (3-3); integration via unittest | **Direct** `json.loads(sidecar)` → `from_dict` in integration |
| CMake fallback | Covered in `test_story_2_2.py` (unittest) | Ported to pytest integration; partial-spec guard explicit |
| `project-configuration.cmake` in output | Not generated since story 1-4; unittest does not assert AC4 | **Explicit** AC4 assertion on generated `CMakeLists.txt` |
| pytest suite size | 100 tests | +8–10 integration tests expected |

**This story is test-only.** No changes to `core/*`, `app/*`, or `Templates/`.

### Scope — Files to Touch

| File | Change |
|------|--------|
| `tests/conftest.py` | **New** (recommended) |
| `tests/integration/test_round_trip.py` | **New** |

**Do NOT touch in this story:**
- `core/project_generator.py`, `core/project_writer.py`, `core/project_reader.py` — behavior is correct; test only
- `tests/test_story_1_2.py`, `tests/test_story_2_1.py`, `tests/test_story_2_2.py` — **keep** as regression; do not delete or migrate away (out of scope)
- `tests/unit/*` — no changes unless extracting a helper creates duplication (prefer `conftest.py` at `tests/` root)
- `pytest.ini` — already discovers `tests/integration/`; no change needed
- CI / `.github/` — still out of scope
- `Templates/README.md`, `Templates/.cursorrules` — still mention `project-configuration.cmake` in docs; AC4 applies to **generated `CMakeLists.txt` only**

### Epic AC Nuances (Read Before Implementing)

**AC #1 — low-level writer path:** Epic wording names `ProjectWriter.write(context, tokens, dest)` explicitly. Implement at least one test that calls the writer directly (not only via `ProjectGenerator`), matching the `test_story_2_1._write_project` pattern:

```python
from core import render_context
from core.project_generator import templates_dir
from core.project_writer import ProjectWriter

dest = tmp_path / spec.project_name
writer = ProjectWriter(templates_dir(), dest)
writer.write(render_context.build_context(spec), render_context.build_tokens(spec), spec)
```

Required paths to assert (relative to project root):

| Path | Category |
|------|----------|
| `CMakeLists.txt` | `_RENDERED` |
| `CMakeUserPresets.json` | `_RENDERED` |
| `.luthier.json` | sidecar (`_write_sidecar`) |
| `Source/PluginProcessor.h` | `_TOKENIZED` |
| `Source/PluginProcessor.cpp` | `_TOKENIZED` |
| `Source/PluginEditor.h` | `_TOKENIZED` |
| `Source/PluginEditor.cpp` | `_TOKENIZED` |

AC1 does **not** require asserting every `_VERBATIM` / `.vscode` file — only the four named in the epic.

**AC #2 — field equality:** Use `dataclasses.fields` loop (same as `test_story_2_1` and `test_project_spec.py`). Test with a **fully populated** spec (non-default values on all 21 fields). Always set `destination_dir=str(tmp_path)` so sidecar reinjection of `destinationDir` matches.

**AC #3 — never partial:** Use `read_project_result()` (not only `read_project()`) for fallback tests that need `missing_fields`. Negative case: strip `COMPANY_NAME` line from `CMakeLists.txt` after deleting sidecar → `spec is None` and `"Company Name" in missing_fields`. Positive case: delete sidecar only → complete spec with `missing_fields == ()`.

**Critical:** When sidecar **exists** but is malformed, `read_project()` returns `None` with **no** CMake fallback (AD-3). That behavior is already in `test_story_2_1` unittest — optional to port; not required by epic AC.

**AC #4 — CMakeLists.txt only:** Assert `"project-configuration.cmake" not in (dest / "CMakeLists.txt").read_text(encoding="utf-8")`. Do not fail on `README.md` or `.cursorrules` references (bundled verbatim copies may still mention the old file).

### Generation Pipeline — Integration Touchpoints

```
ProjectSpec (destination_dir, project_name, …)
    ↓
ProjectGenerator.generate(spec, juce_dir="")
    ├── render_context.build_context(spec, juce_dir)
    ├── render_context.build_tokens(spec)
    └── ProjectWriter(templates_dir(), project_dir, overrides).write(context, tokens, spec)
            ├── _write_all() → _RENDERED + _TOKENIZED + _VERBATIM
            ├── _write_sidecar() → .luthier.json (spec.to_dict(), indent=2)
            └── atomic: {name}.tmp → rename → {name}/
    ↓
project_reader.read_project(project_dir)
    ├── sidecar exists → _read_sidecar (injects destinationDir = str(project_dir.parent))
    └── no sidecar → _parse_cmakelists() → complete or None
```

**Production wiring reference** (`MainWindow` passes overrides):

```python
ProjectGenerator(overrides=templates_store.overrides_dir())
```

For integration tests, pass `overrides=tmp_path / "overrides"` directly to avoid `QStandardPaths` / Qt.

**AD-7:** Always pass `juce_dir=""` unless testing JUCE injection (covered in `test_render_context.py` unit tests). `juce_dir` is not on `ProjectSpec` and does not round-trip.

**AD-9 override layout** (for optional override test):

| Template relative path | Override lookup |
|------------------------|-----------------|
| `Source/PluginProcessor.h` | `{overrides}/PluginProcessor.h` |
| `.gitignore` | `{overrides.parent}/.gitignore` |

`ProjectWriter._override_for()` checks `candidate.exists()` — file must exist on disk before generation.

### `core/project_writer.py` — Write Contract

```11:33:core/project_writer.py
_RENDERED = (
    "CMakeLists.txt",
    "CMakeUserPresets.json",
    ...
)
_TOKENIZED = (
    "Source/PluginProcessor.h",
    ...
)
_VERBATIM = (
    ".vscode/extensions.json",
    ".cursorrules",
    ".gitignore",
    ...
)
```

```43:59:core/project_writer.py
    def write(self, context: dict, tokens: dict, spec: ProjectSpec) -> None:
        tmp = self._project.parent / (self._project.name + ".tmp")
        ...
            self._write_all(tmp, context, tokens)
            self._write_sidecar(tmp, spec)
            ...
            tmp.rename(self._project)
```

Sidecar format: `json.dumps(spec.to_dict(), indent=2, ensure_ascii=False)` — integration test should parse this exact file.

### `core/project_reader.py` — Read Contract

```72:91:core/project_reader.py
def read_project_result(project_dir: Path) -> ProjectReadResult:
    sidecar = project_dir / _SIDECAR
    if sidecar.exists():
        return ProjectReadResult(spec=_read_sidecar(sidecar, project_dir))
    return _read_from_cmake_result(project_dir)

def _read_sidecar(sidecar: Path, project_dir: Path) -> Optional[ProjectSpec]:
    ...
    data["destinationDir"] = str(project_dir.parent)
    return ProjectSpec.from_dict(data)
```

**Round-trip nuance:** Sidecar JSON does not store `destinationDir` from write time; reader injects it from filesystem layout. Tests must set `spec.destination_dir = str(tmp_path)` before generate so injected value matches.

**CMake fallback** reads copy/artefact settings from `CMakeLists.txt` inline block (post story 1-4) or legacy `project-configuration.cmake` if present (`_parse_build_settings`).

### Recommended `make_spec` Defaults

Mirror `tests/test_story_2_1._make_spec` — the canonical integration fixture:

```python
def make_spec(tmp_path, **kwargs):
    from core.project_spec import ProjectSpec
    defaults = dict(
        project_name="MyPlugin",
        project_display_name="My Plugin",
        project_version="1.0.0",
        manufacturer_name="Acme",
        manufacturer_code="Acme",
        plugin_code="Mypl",
        company_copyright="Copyright 2026",
        company_website="https://acme.example",
        company_email="dev@acme.example",
        destination_dir=str(tmp_path),
        plugin_type="synth",
        plugin_formats="VST3",
        cxx_standard="C++20",
        preprocessor_definitions="FOO=1",
        header_search_paths="/extra/include",
        copy_to_system_folders=True,
        copy_to_artefacts_dir=False,
        artefacts_dir_windows="C:\\out",
        artefacts_dir_macos="/out/mac",
        artefacts_dir_linux="/out/linux",
    )
    defaults.update(kwargs)
    return ProjectSpec(**defaults)
```

Place in `tests/conftest.py` so integration tests and future stories can import via pytest fixture:

```python
@pytest.fixture
def make_spec(tmp_path):
    def _factory(**kwargs):
        ...
    return _factory
```

Or plain functions if fixtures add unnecessary indirection — keep helpers ≤ 15 lines (NFR1).

### Legacy Test Migration Map

| Legacy unittest (`test_story_*.py`) | New pytest integration test |
|-------------------------------------|----------------------------|
| `test_story_2_1::test_read_sidecar_returns_all_fields` | `test_read_project_returns_equivalent_spec` |
| `test_story_2_1::test_round_trip_empty_diff` | `test_regenerate_produces_identical_tree` |
| `test_story_2_2::test_cmake_fallback_without_sidecar` | `test_cmake_fallback_returns_complete_spec` |
| `test_story_2_2::test_cmake_fallback_round_trip` | `test_cmake_fallback_regenerate_identical_tree` |
| `test_story_2_2::test_partial_cmake_returns_none_with_missing_fields` | `test_partial_cmake_returns_none_not_partial_spec` |
| `test_story_2_2::test_no_cmakelists_returns_none` | `test_no_cmakelists_returns_none` |
| *(none)* | `test_writer_output_contains_required_files` (AC1 explicit) |
| *(none)* | `test_generated_cmakelists_has_no_project_configuration_reference` (AC4) |
| *(none)* | `test_sidecar_json_round_trip` (3-3 deferral) |

**Do not delete legacy tests** — pytest runs both; duplication is acceptable until a future cleanup story.

### `all_files` Helper — Byte-for-Byte Regenerate Check

```python
def all_files(root: Path) -> dict[Path, bytes]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root)] = path.read_bytes()
    return result
```

After regenerate, compare `set(before) == set(after)` and `before[rel] == after[rel]` for every relative path. This catches template rendering regressions that field equality alone would miss.

### Pytest Infrastructure

**Run commands:**

```bash
.venv/bin/pytest                         # full suite from repo root
.venv/bin/pytest tests/integration -v    # integration only
.venv/bin/python -m unittest discover -s tests -v   # legacy regression
```

**Config** — `pytest.ini` already sets `testpaths = tests`, `pythonpath = .`.

- Use `tmp_path` fixture (not `tempfile.TemporaryDirectory`)
- Use `monkeypatch` only if testing `templates_store` overrides (optional test)
- `@pytest.mark.parametrize("plugin_type", ["synth", "effect", "midi"])` on read-fidelity test is optional but high value
- No `pytest-cov` — YAGNI
- Test functions ≤ 15 lines per NFR1 — extract helpers to `conftest.py`

### No-Qt Requirement (AD-6 / AD-8)

Integration tests must import only `core/*` modules — same as legacy round-trip tests. Do **not** import `templates_store` in the default integration path (it loads PySide6 for `QStandardPaths`).

For optional override test, either:
- Pass `overrides=tmp_path / "Source"` directly to `ProjectGenerator(overrides=...)` with a hand-placed file, **or**
- Monkeypatch `QStandardPaths` (pattern from `test_templates_store.py`) in that one test only

Subprocess-based import isolation deferred — not required for this story.

### Architecture Compliance

| AD / NFR | Requirement | Story 3-4 action |
|----------|-------------|------------------|
| AD-1 | `ProjectSpec` cross-layer contract | Integration verifies writer → reader equality |
| AD-3 | Sidecar first; fallback complete or `None` | AC2 + AC3 tests |
| AD-4 | Atomic write | Already tested in `test_story_1_2`; no duplicate unless regression gap found |
| AD-6 | `tests/integration/` round-trip with `tmp_path` | **Primary deliverable** |
| AD-7 | `juce_dir` not on `ProjectSpec` | Pass `juce_dir=""` in all integration tests |
| AD-8 | `core/` no Qt imports in tests | Integration imports `core/*` only |
| AD-9 | Overrides at write time | Optional override test via `ProjectGenerator(overrides=...)` |
| NFR2 | Integration tier for round-trip | Closes Epic 3 integration gap |
| NFR1 | Functions ≤ 15 lines | Helpers in `conftest.py`; parametrize where needed |

[Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md` §AD-3, §AD-6, §AD-9]

### Previous Story Intelligence (Story 3-3)

**Established patterns to reuse:**
- `_make_spec` / `_assert_fields_equal` from `tests/unit/test_project_spec.py`
- `_patch_config_root` monkeypatch from `tests/unit/test_templates_store.py` (override test only)
- Field-by-field assertion via `dataclasses.fields`
- Full suite: 100 pytest + 20 unittest after 3-3

**Explicitly deferred to this story (from 3-3 dev notes):**
- `tests/conftest.py` with shared `_make_spec`
- `tests/integration/test_round_trip.py`
- `json.loads(sidecar)` → `from_dict` integration path
- `ProjectWriter._override_for()` wiring test

**Do not duplicate unit coverage:**
- `ProjectSpec.to_dict`/`from_dict` edge cases — stay in `test_project_spec.py`
- `render_context.build_context` optional blocks — stay in `test_render_context.py`
- Atomic write failure cleanup — stay in `test_story_1_2.py`

### Git Intelligence

| Commit | Relevance |
|--------|-----------|
| `d4ecf73` Story 3-2 done | 84 pytest tests; rendering + render_context unit coverage |
| `c3e1309` Story 3-1 done | pytest infrastructure; `tests/unit/` established |
| `9fac1f8` Epic 2 done | `test_story_2_1.py`, `test_story_2_2.py` — primary migration source |
| `c58a341` Story 1-4 | Inlined copy config into `CMakeLists.txt`; AC4 guard |

No production code changes expected — test-only diff.

### Latest Technical Information

- **pytest 9.x** (floor `>=8.0` in `requirements-dev.txt`) — `tmp_path`, `monkeypatch` built-in; no plugins required
- **`tmp_path`** is function-scoped and auto-cleaned — preferred over `tempfile.TemporaryDirectory()`
- **Sidecar JSON** uses `indent=2` — byte comparison in regenerate test includes sidecar; regenerating from loaded spec should produce identical bytes if round-trip is lossless
- No web research required — stdlib + existing pytest + in-repo legacy tests define the contract

### Project Structure Notes

```text
tests/
  conftest.py              # NEW — shared helpers (story 3-4)
  test_story_1_2.py        # keep — atomic write, sidecar smoke
  test_story_2_1.py        # keep — unittest round-trip reference
  test_story_2_2.py        # keep — unittest CMake fallback reference
  unit/
    test_project_spec.py   # dataclass layer round-trip
    test_templates_store.py
    ...                    # stories 3-1, 3-2, 3-3
  integration/
    __init__.py
    test_round_trip.py     # NEW — story 3-4
```

### Downstream Story Boundaries

| Story | Relationship to 3-4 |
|-------|---------------------|
| Epic 3 complete after 3-4 | No further test stories in epic; retrospective optional |
| Epic 4 | Cross-platform cmake validation (4-3) may add CI-level integration later — out of scope |
| Future cleanup | Migrating/removing duplicate `test_story_*.py` unittest modules — not this story |

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` §Story 3.4]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md` §AD-3, §AD-6, §AD-9]
- [Source: `_bmad-output/implementation-artifacts/3-3-unit-tests-projectspec-and-templates-store.md`]
- [Source: `_bmad-output/project-context.md` §Round-Trip, §Two-Pass Template Rendering]
- [Source: `core/project_generator.py`, `core/project_writer.py`, `core/project_reader.py`]
- [Source: `tests/test_story_2_1.py`, `tests/test_story_2_2.py` — migration reference]

### Review Findings

- [x] [Review][Patch] `write_project` ignores `spec.destination_dir` [`tests/conftest.py:60-61`] — fixed: uses `Path(spec.destination_dir) / spec.project_name`.
- [x] [Review][Patch] `make_spec` exceeds NFR1 15-line limit [`tests/conftest.py:9-33`] — fixed: defaults extracted to `_default_spec_fields`.
- [x] [Review][Patch] `test_legacy_project_configuration_cmake_compat` exceeds NFR1 15-line limit [`tests/integration/test_round_trip.py:135-169`] — fixed: extracted `install_legacy_project_configuration_cmake` to `conftest.py`.
- [x] [Review][Defer] No `@pytest.mark.parametrize` for `plugin_type` [`tests/integration/test_round_trip.py`] — deferred, spec marks as optional high-value coverage.
- [x] [Review][Defer] Malformed sidecar → `None` without CMake fallback not ported [`tests/integration/test_round_trip.py`] — deferred, spec explicitly optional (covered in `test_story_2_1` unittest).
- [x] [Review][Defer] `IS_SYNTH` / `plugin_type` CMake fallback variants untested [`tests/integration/test_round_trip.py:96-108`] — deferred, only `COMPANY_NAME` negative case ported from legacy tests.
- [x] [Review][Defer] `test_partial_cmake` regex narrow vs CMake formatting variants [`tests/integration/test_round_trip.py:103`] — deferred, matches legacy `test_story_2_2` pattern; broader regex hardening is Epic 3+.
- [x] [Review][Defer] `test_legacy_project_configuration_cmake_compat` regex coupled to template banner text [`tests/integration/test_round_trip.py:151-157`] — deferred, ported from legacy; template wording change is separate concern.
- [x] [Review][Defer] No `read_project` round-trip via `write_project` path [`tests/integration/test_round_trip.py`] — deferred, AC2 satisfied via `generate_project`; writer read parity is optional hardening.
- [x] [Review][Defer] Byte-identical `assert_trees_equal` may be sensitive to non-deterministic output [`tests/conftest.py:49-52`] — deferred, templates are deterministic; same pattern as legacy unittest round-trip tests.

## Dev Agent Record

### Agent Model Used

Composer (Cursor Agent)

### Debug Log References

- Red-green-refactor: integration tests written first against existing core pipeline; all 11 passed on first run after helper extraction to `conftest.py`.

### Completion Notes List

- Ultimate context engine analysis completed — comprehensive developer guide created (2026-06-23).
- Added `tests/conftest.py` with shared `make_spec`, `all_files`, `assert_spec_equal`, `assert_trees_equal`, `write_project`, and `generate_project` helpers.
- Added `tests/integration/test_round_trip.py` with 11 pytest integration tests covering AC1–AC4, sidecar JSON round-trip, regenerate byte-for-byte fidelity, CMake fallback complete/None guards, AC4 CMakeLists guard, template override (AD-9), and legacy `project-configuration.cmake` compat.
- Full regression: 111 pytest + 20 unittest, all green. Integration tier imports `core/*` only — no Qt.

### File List

- tests/conftest.py (new)
- tests/integration/test_round_trip.py (new)

### Change Log

- 2026-06-24: Story 3-4 implementation — pytest integration tier for project generation round-trip; shared conftest helpers; 11 new integration tests.
