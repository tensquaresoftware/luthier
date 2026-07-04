---
epic: 9
story: 6
story_key: 9-6-test-suite-scaffold-only-regression
depends_on: [9-1, 9-2, 9-3, 9-4, 9-7, 9-8]
blocks: [9-5]
implementation_order: 7
pivot_date: 2026-07-04
baseline_commit: d8d356f
baseline_tests: "313 collected, 3 skipped (pre-9.6)"
---

# Story 9.6: Test Suite — Scaffold-Only Regression

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a contributor,
I want the test suite aligned with scaffold-only semantics,
So that CI catches regressions in generate guard and plugin characteristics without false reload coverage.

## Context

**Epic 9 pivot (2026-07-04):** Luthier is a **one-shot JUCE/CMake skeleton generator**. Stories **9.1–9.4**, **9.7**, and **9.8** are **done** — Open/reload removed, generate guard + session regenerate carve-out, decoupled characteristics, template pipeline wired to `ProjectSpec`, Preferences-only accent.

**Story 9.6 is the Epic 9 quality gate:** align tests with scaffold-only semantics, close deferred coverage gaps from prior story reviews, and ensure CI (`pytest`) reflects the v1.0 product model — **not** a Projucer-like reload lifecycle.

**Important:** Much test work landed incrementally in 9.1–9.4 and 9.8. This story is **consolidation + gap-fill**, not a ground-up rewrite. Do not delete working coverage unless it asserts removed behaviour (Open/reload/sidecar read).

**Planning references:**
- `_bmad-output/planning-artifacts/epics.md` — Epic 9, Story 9.6
- `_bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md` — §8 Story 9.6, §9.6 test inventory
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md` — test impact, grep checklist
- `_bmad-output/implementation-artifacts/deferred-work.md` — items explicitly deferred to 9.6

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.8 → 9.4 → 9.6 → 9.5`

### What changes vs what stays

| Area | Change (9.6) | Keep unchanged |
|------|--------------|----------------|
| Reload tests | Remove/rename any remaining Open/reload semantics in names, docstrings, assertions | Write-only sidecar fidelity via `ProjectSpec.from_dict(sidecar_json)` |
| Guard coverage | Add hidden-file block tests (`.DS_Store`, `.git/`) deferred from 9.2 | Existing `test_generate_guard.py` matrix |
| Characteristics | Ensure validation matrix complete; optional parametrized CMake spot-checks per plugin type | `test_plugin_characteristics.py`, `test_buses_properties.py`, 9.4 integration tests |
| Accent sidecar | Rename stale tests; optional DRY helper for `assert "accentColor" not in sidecar` | Preferences accent tests in `test_preferences.py` / `test_accent_colors.py` |
| Architecture doc | Update stale test count in `_bmad-output/architecture.md` | AD-6 strategy (unit + integration, no Qt widget tests) |
| App / core code | — | **No production code changes** unless a test reveals a real bug |

### Critical distinction for dev agent

**Write-only sidecar tests are valid.** Tests that read `.luthier.json` with `json.loads` + `ProjectSpec.from_dict()` assert **generation output fidelity** — not app reload. Do **not** remove `test_sidecar_json_matches_spec` or similar unless they import `project_reader` or simulate Open Project.

**Session regenerate tests use `allow_overwrite=True`** on `generate_project()` / `ProjectGenerator.generate()` — this mirrors Story 9.8 core path after user confirms. Do not conflate with deleted overwrite-on-any-folder behaviour from pre-9.2.

## Acceptance Criteria

### AC1 — No reload/Open test coverage remains

**Given** the `tests/` tree  
**Then** no file imports `core.project_reader` or calls `read_project` / `read_project_result`  
**And** no test name, module docstring, or assertion references **Open Project…**, `_load_project`, or sidecar **read-back into the app**  
**And** `tests/unit/test_project_reader.py` does not exist (deleted in 9.1)

**Allowed:** `ProjectSpec.from_dict(json.loads(sidecar))` for write-only fidelity; variable names like `reloaded = Preferences(...)` for JSON persistence tests.

### AC2 — Generate guard regression matrix complete

**Given** `tests/unit/test_generate_guard.py` (and integration helpers)  
**Then** coverage includes at minimum:

| Scenario | Expected |
|----------|----------|
| Non-empty dir, fresh session (no `lastGeneratedProjectDir`) | `destination_blocks_generate` → True; `GenerateBlockedError` on second generate without `allow_overwrite` |
| Empty existing dir | Generate allowed |
| Missing dir | Generate allowed |
| Non-directory path | Blocked |
| Session same-path | `session_regenerate_eligible` → True when paths match |
| Different non-empty path in session | Not eligible |
| **`allow_overwrite=True`** after first generate | Regenerate succeeds; sidecar/content updates |
| **Hidden entries** (`.DS_Store` file, `.git/` directory) | `destination_blocks_generate` → True (deferred from 9.2 review) |

### AC3 — Session regenerate semantics (9.8) preserved in tests

**Given** integration coverage in `tests/integration/test_round_trip.py`  
**Then** at least one test proves regenerate with `allow_overwrite=True` updates CMake/cpp from **current** `ProjectSpec` (already: `test_session_regenerate_updates_characteristics`)  
**And** guard tests prove fresh session cannot regenerate brownfield folder without session memory

### AC4 — Characteristics validation matrix

**Given** `tests/unit/test_plugin_characteristics.py`  
**Then** asserts at minimum:
- `characteristics_conflict(True, True)` → invalid (synth + MIDI effect)
- Instrument preset + `needs_midi_output=True` → valid (Matrix-Control case)
- All three plugin type preset defaults
- `flags_for_type()` still returns preset CMake strings (shim for legacy callers — not generate truth)

**Optional enhancement:** parametrized integration spot-check — generate for `TYPE_INSTRUMENT`, `TYPE_AUDIO_EFFECT`, `TYPE_MIDI_EFFECT` and assert type-appropriate CMake flags in `CMakeLists.txt`.

### AC5 — Template emission spot-checks

**Given** integration or unit tests  
**Then** CMake characteristic flags are asserted for spec overrides beyond preset defaults (9.4 delivered Matrix-Control, mono buses, MIDI effect empty buses, description quoting)  
**And** no test expects `flags_for_type(pluginType)` output in generated projects when spec fields differ from preset

### AC6 — Sidecar excludes accent; stale names cleaned

**Given** sidecar assertions across `test_round_trip.py`, `test_project_writer.py`, `test_frozen_bundle.py`, `test_cmake_cross_platform.py`  
**Then** each generated sidecar test includes `assert "accentColor" not in data` (consolidate via shared helper in `conftest.py` if duplication is noisy — optional)  
**And** rename or rewrite stale identifiers:
- `test_preferences_decouple.py` module docstring / `test_preferences_file_unchanged_after_simulated_open_generate_workflow` → Generate-only wording
- `test_project_dirty_guard.py` `test_load_project_clears_dirty_state` → post-generate baseline sync naming
- `test_cmake_cross_platform.py` `test_cross_origin_sidecar_preserves_spec_ac4` docstring — remove "app reload" phrasing

**And** `test_project_spec.py` retains `test_from_dict_ignores_legacy_accent_color_key` (legacy key stripped, not round-tripped)

### AC7 — CI green

**Given** GitHub Actions workflow `.github/workflows/pytest.yml`  
**When** `.venv/bin/pytest` runs locally  
**Then** full suite passes (current baseline: **313 collected**, **3 skipped** — frozen bundle / cmake host skips)

### AC8 — Out of scope (explicit)

**Not in 9.6:** User manual updates (`docs/user/**` — Story 9.5), QA checklist updates (`docs/tests/**` — 9.5), Qt widget tests for `MainWindow` confirm dialogs (AD-6 manual smoke), reintroducing `project_reader`, production code refactors unless fixing a test-discovered bug.

## Tasks / Subtasks

- [x] **Audit grep** (AC: 1)
  - [x] Run `rg -i 'project_reader|read_project|Open Project|_load_project' tests/` — fix any hits
  - [x] Confirm `core/project_reader.py` absent from repo
- [x] **Guard gap-fill** (AC: 2)
  - [x] Add `test_destination_blocks_hidden_ds_store` and `test_destination_blocks_git_directory` to `test_generate_guard.py`
- [x] **Rename stale test semantics** (AC: 6)
  - [x] Update `test_preferences_decouple.py` docstring + test name
  - [x] Rename `test_load_project_clears_dirty_state` → e.g. `test_post_generate_baseline_clears_dirty_state`
  - [x] Fix `test_cmake_cross_platform.py` AC4 docstring
- [x] **Optional consolidation** (AC: 6)
  - [x] Add `assert_sidecar_omits_accent(data: dict)` in `tests/conftest.py` if ≥3 duplicate one-liners remain
- [x] **Optional parametrized plugin-type CMake checks** (AC: 4, 5)
  - [x] Extend `test_round_trip.py` or add `test_scaffold_cmake_flags_by_plugin_type.py`
- [x] **Docs touch** (AC: 7)
  - [x] Update `_bmad-output/architecture.md` Testing section: test count (~313), remove "158 tests" stale figure; note scaffold-only integration scope
- [x] **Verify** (AC: 7)
  - [x] Run `.venv/bin/pytest` — full green
  - [x] Update deferred-work.md: mark 9.6-resolved items (hidden-file tests, sidecar regenerate coverage) if addressed

### Review Findings

- [x] [Review][Patch] `test_sidecar_json_round_trip` omits accent assertion [tests/integration/test_round_trip.py:49]
- [x] [Review][Patch] Matrix-Control unit test never exercises `needs_midi_output=True` [tests/unit/test_plugin_characteristics.py:120]
- [x] [Review][Patch] `test_session_regenerate_updates_characteristics` does not verify sidecar rewrite [tests/integration/test_round_trip.py:152]
- [x] [Review][Patch] `sprint-status.yaml` header comment says `ready-for-dev` while status is `review` [_bmad-output/implementation-artifacts/sprint-status.yaml:1]
- [x] [Review][Defer] Substring-based CMake/cpp assertions fragile to template formatting [tests/integration/test_round_trip.py] — deferred, pre-existing pattern
- [x] [Review][Defer] Regenerate test mutates `ProjectSpec` in place instead of fresh instance [tests/integration/test_round_trip.py:152] — deferred, minor test-style debt

## Dev Notes

### Current test inventory (pre-9.6 baseline)

| Module | Role | 9.6 action |
|--------|------|------------|
| `tests/unit/test_generate_guard.py` | Guard + session eligibility + overwrite | Add hidden-file cases |
| `tests/unit/test_plugin_characteristics.py` | Preset defaults + conflict matrix | Verify complete; extend if gaps |
| `tests/unit/test_buses_properties.py` | Bus body presets (9.4) | Keep |
| `tests/integration/test_round_trip.py` | Generate fidelity, sidecar, session regenerate | Rename docstrings only; keep tests |
| `tests/unit/test_preferences_decouple.py` | AD-5 Generate does not write prefs | Rename Open wording |
| `tests/unit/test_project_dirty_guard.py` | Create New Project dirty guard | Rename `load_project` test |
| `tests/integration/test_cmake_cross_platform.py` | CMake configure + sidecar clone | Fix AC4 docstring |
| `tests/integration/test_frozen_bundle.py` | PyInstaller bundle smoke | Keep accent assertion |
| `tests/unit/test_project_spec.py` | Spec round-trip, accent key ignored | Keep |
| `tests/unit/test_project_writer.py` | Sidecar omit accent | Keep |
| ~~`tests/unit/test_project_reader.py`~~ | — | **Already deleted (9.1)** |

### Valid sidecar round-trip pattern (keep)

```python
def test_sidecar_json_round_trip(tmp_path):
    project_dir, spec = generate_project(tmp_path)
    data = json.loads((project_dir / ".luthier.json").read_text(encoding="utf-8"))
    restored = ProjectSpec.from_dict(data)  # NOT project_reader — write-only fidelity
    assert_spec_equal(restored, spec)
```

This test validates that `.luthier.json` is a faithful snapshot of `ProjectSpec` at generation time — for humans/AI tools per AD-3. It does **not** imply app reload.

### Hidden-file guard tests (sketch)

```python
def test_destination_blocks_hidden_ds_store(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / ".DS_Store").write_bytes(b"\x00")
    assert destination_blocks_generate(project_dir) is True


def test_destination_blocks_git_directory(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()
    assert destination_blocks_generate(project_dir) is True
```

Behaviour already correct via `any(project_dir.iterdir())` in `destination_blocks_generate()` — 9.2 review deferred explicit tests to 9.6.

### Stale naming to fix

```84:90:tests/unit/test_project_dirty_guard.py
def test_load_project_clears_dirty_state():
    """After load (e.g. post-generate), the form should not appear unsaved."""
```

Rename to reflect **post-generate baseline sync** (`ProjectPage.load(spec)` after Generate), not Open Project reload.

```1:1:tests/unit/test_preferences_decouple.py
"""Tests that Open/Generate workflows do not modify preferences.json."""
```

Change to Generate-only workflow wording (Open path removed in 9.1).

### Architecture doc stale count

```165:178:_bmad-output/architecture.md
## Testing {#testing}
...
- **158 tests** collected; no display required for the default suite.
```

Update to current count and scaffold-only integration description after 9.6.

### Overlap with other Epic 9 stories

| Story | Boundary |
|-------|----------|
| 9.1–9.4, 9.7, 9.8 | Done — delivered focused tests; 9.6 does not rework their production code |
| **9.6** | Test alignment, grep audit, deferred coverage, doc touch |
| 9.5 | User manuals + README + QA checklists — out of scope |

### Anti-patterns (do NOT)

- **Do not** reintroduce `project_reader` or Open/reload integration tests
- **Do not** remove sidecar JSON fidelity tests that use `from_dict` only
- **Do not** add Qt widget tests for Generate confirm dialogs (AD-6)
- **Do not** change generate guard or session regenerate production semantics unless a test proves a bug
- **Do not** scope-creep into `docs/user/**` (Story 9.5)

### Project Structure Notes

- **Test layout unchanged:** `tests/unit/` for core; `tests/integration/` for generate round-trip
- **Run:** `.venv/bin/pytest` from repo root
- **CI:** `.github/workflows/pytest.yml` — Python 3.11 on ubuntu-latest, `QT_QPA_PLATFORM=offscreen`
- **Shared helpers:** `tests/conftest.py` — `make_spec`, `generate_project`, `assert_spec_equal`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 9.6]
- [Source: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §8 Story 9.6]
- [Source: _bmad-output/implementation-artifacts/deferred-work.md — 9.1, 9.2 deferred items]
- [Source: _bmad-output/implementation-artifacts/9-4-template-pipeline-audio-io-midi-description.md — test baseline 309 passed]
- [Source: tests/conftest.py]
- [Source: tests/unit/test_generate_guard.py]
- [Source: tests/integration/test_round_trip.py]
- [Source: _bmad-output/architecture.md#Testing]

## Dev Agent Guardrails

### Technical requirements

1. **Tests-only story** — default to zero production code changes; fix app/core only if pytest exposes a real regression.
2. **Grep gate:** `tests/` must have zero references to `project_reader`, `read_project`, `Open Project`.
3. **Preserve 9.2/9.8 guard semantics** — hidden-file tests document behaviour; do not weaken `destination_blocks_generate`.
4. **Preserve 9.4 template tests** — do not revert spec-driven CMake/bus assertions to preset-only expectations.
5. **Sidecar accent invariant** — every integration test that reads `.luthier.json` must assert no `accentColor`.
6. **Session regenerate** — tests use `allow_overwrite=True`; never simulate pre-9.2 unconditional overwrite dialog.

### Architecture compliance

| AD | Rule for 9.6 |
|----|--------------|
| AD-3 | Sidecar tests assert write-only snapshot; no read path in app |
| AD-5 | Keep `test_preferences_decouple` — Generate never writes prefs |
| AD-6 | No Qt GUI tests; headless pytest only |
| AD-8 | Core import guard tests remain; no `project_reader` in import list |

### Library / framework requirements

- **pytest ≥ 8.0** (`requirements-dev.txt`) — no new test dependencies
- **Python 3.14** local dev; CI uses **3.11** (workflow) — tests must pass on both
- No web research required

### File structure requirements

| File | Action |
|------|--------|
| `tests/unit/test_generate_guard.py` | Add hidden-file block tests |
| `tests/unit/test_preferences_decouple.py` | Rename docstring + test function |
| `tests/unit/test_project_dirty_guard.py` | Rename stale `load_project` test |
| `tests/integration/test_cmake_cross_platform.py` | Fix docstring |
| `tests/conftest.py` | Optional `assert_sidecar_omits_accent` helper |
| `tests/integration/test_round_trip.py` | Optional parametrized plugin-type CMake checks |
| `_bmad-output/architecture.md` | Update test count + scaffold-only testing note |
| `_bmad-output/implementation-artifacts/deferred-work.md` | Mark resolved 9.6 items |

**Do not modify:** `app/**`, `core/**` (unless bug fix), `docs/user/**`, `Templates/**`

### Testing requirements

**Must pass before marking done:**
```bash
.venv/bin/pytest
```

**Pre-flight audit:**
```bash
rg -i 'project_reader|read_project|Open Project|_load_project' tests/
# Expected: no matches (after 9.6 renames)
```

**Manual smoke (optional — AD-6):**
1. Fresh app → Generate into non-empty folder → blocked
2. Same session → Generate same path → destructive confirm → succeeds
3. Restart app → Generate same brownfield path → blocked

### Previous story intelligence

**From 9.4 (done):**
- Integration tests for Matrix-Control, mono buses, MIDI effect, session regenerate characteristics
- `test_buses_properties.py` — four audio I/O presets
- Baseline: **309 passed, 3 skipped** after 9.4

**From 9.8 (done):**
- `test_generate_guard.py` covers session eligibility, `allow_overwrite`, git preservation
- `AppState.last_generated_project_dir()` session memory — not persisted across restart

**From 9.2 (done):**
- Hidden-file block deferred explicitly to 9.6
- `test_regenerate_preserves_git_directory` kept (session overwrite path)

**From 9.1 (done):**
- `test_project_reader.py` deleted; `test_regenerate_*` sidecar-read paths removed intentionally
- Sidecar→regenerate coverage partially restored in 9.4 integration test

### Git intelligence

Recent Epic 9 commits (patterns to follow):
- `d8d356f` — Story 9.8: session regenerate + `allow_overwrite`
- `97c808c` — Stories 9.2–9.3: generate guard + characteristics spec
- Story 9.4 work (in working tree): template pipeline tests, `test_buses_properties.py`

Follow established patterns: minimal diffs, pytest green, test names match scaffold-only vocabulary.

### Latest tech information

No new libraries. pytest 8.x collection/execution unchanged. CI workflow uses `actions/setup-python@v5` with Python 3.11 — ensure no 3.14-only syntax in new tests without `from __future__` compatibility (project uses minimal annotations already).

## Project Context Reference

Key rules from `_bmad-output/project-context.md`:
- Scaffold-only data flow: `ProjectPage.spec()` → guard → `ProjectGenerator.generate()` → write-only `.luthier.json`
- No module reads `.luthier.json` at runtime (AD-3, Epic 9)
- Generate guard: non-empty blocked except session same-path + confirm (9.8)
- Run tests: `.venv/bin/pytest`
- Test coverage in `tests/unit/` + `tests/integration/`; Qt widgets manual QA only

## Story Completion Status

- **Status:** done
- **Completion note:** Test suite aligned with scaffold-only semantics; 319 collected, 316 passed, 3 skipped; code review patches applied (accent gap, Matrix-Control unit test, regenerate sidecar assert).
- **Next story after dev:** 9.5 (`9-5-documentation-v1-guide-manuals-readme`) — user-facing docs; depends on stable scaffold-only test baseline from 9.6

## Dev Agent Record

### Agent Model Used

Claude (Cursor Agent)

### Debug Log References

- Grep audit: zero hits for `project_reader|read_project|Open Project|_load_project` in `tests/`
- `core/project_reader.py` confirmed absent from repo

### Completion Notes List

- Added hidden-file guard tests (`.DS_Store`, `.git/`) deferred from Story 9.2 review
- Renamed stale Open/reload test identifiers to scaffold-only vocabulary (preferences decouple, dirty guard, cmake cross-platform docstring)
- Added `assert_sidecar_omits_accent()` helper in `conftest.py`; wired into 6 sidecar assertion sites
- Added `test_instrument_with_midi_output_matrix_control_valid` for AC4 Matrix-Control case
- Added parametrized `test_scaffold_cmake_flags_match_plugin_type_preset` for all three plugin types
- Updated `_bmad-output/architecture.md` test count (319 collected) and scaffold-only integration scope
- Marked deferred items resolved in `deferred-work.md` (hidden-file tests, sidecar regenerate coverage)
- Full suite: **316 passed, 3 skipped** — no production code changes

### File List

- tests/unit/test_generate_guard.py
- tests/unit/test_preferences_decouple.py
- tests/unit/test_project_dirty_guard.py
- tests/unit/test_plugin_characteristics.py
- tests/conftest.py
- tests/integration/test_round_trip.py
- tests/integration/test_cmake_cross_platform.py
- tests/integration/test_frozen_bundle.py
- tests/unit/test_project_writer.py
- _bmad-output/architecture.md
- _bmad-output/implementation-artifacts/deferred-work.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/implementation-artifacts/9-6-test-suite-scaffold-only-regression.md

### Change Log

- 2026-07-04: Story 9.6 — scaffold-only test alignment, guard gap-fill, stale rename cleanup, accent helper DRY, architecture doc update (319 tests)
