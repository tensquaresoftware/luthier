---
epic: 9
story: 2
story_key: 9-2-block-generate-non-empty-destination
depends_on: [9-1, 9-7]
blocks: [9-6]
implementation_order: 3
pivot_date: 2026-07-04
baseline_commit: a09f879
---

# Story 9.2: Block Generate on Non-Empty Destination

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a JUCE developer,
I want Generate refused when the target folder already contains files,
So that I cannot accidentally destroy an existing project (e.g. Matrix-Control).

## Context

**Epic 9 pivot (2026-07-04):** Luthier is a **one-shot JUCE/CMake skeleton generator**. Stories **9.1** and **9.7** are **done** — Open/reload removed, accent Preferences-only, OS tree connectors shipped. Story **9.2** replaces the legacy **overwrite confirmation** with a **hard block** when the target project directory already exists and is not empty.

**FR10:** Generate is hard-blocked when `{host_destination}/{project_name}/` exists and is non-empty. No overwrite-with-confirmation in v1.0.

**Planning references:**
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md` — §5 F4 Generate Guard, AD-4 revision, FR10
- `_bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md` — §8 Story 9.2, §9.2 file inventory
- `_bmad-output/planning-artifacts/epics.md` — Epic 9, Story 9.2

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.4 → 9.6 → 9.5`

### What changes vs what stays

| Area | Remove / replace (9.2) | Keep |
|------|------------------------|------|
| Overwrite UX | `MainWindow._confirm_overwrite()` + `confirm_yes_no` overwrite dialog | Destination picker when host path missing/invalid (unchanged) |
| `project_exists()` | Replace with non-empty guard semantics | `ProjectGenerator.generate()` pipeline, atomic `ProjectWriter` |
| Regenerate same folder | **Forbidden** — second Generate into populated dir blocked | First Generate into fresh or **empty** project subfolder |
| Sidecar / Open | — | Write-only `.luthier.json`; no reload path |
| Tests | `test_regenerate_*` that assert successful re-generation | New guard matrix tests; CI green |

### Critical distinction for dev agent

Today `_confirm_overwrite()` only checks **existence**, then asks the user to overwrite. That dialog **destroys** existing trees via `ProjectWriter.write()` (rmtree + atomic rename). Story 9.2 **eliminates** that path entirely — the Matrix-Control safety case is the primary driver.

**Target directory:** `Path(spec.host_destination_dir()) / spec.project_name` — same path `ProjectGenerator.generate()` uses today.

## Acceptance Criteria

### AC1 — Non-empty destination hard-blocked

**Given** target project directory `{destination}/{projectName}/` **exists** and is **non-empty** (any entry from `iterdir()`, including hidden files like `.DS_Store` or `.git/`)  
**When** user clicks **Generate Project**  
**Then** generation does **not** start  
**And** status bar shows error (`ok=False`)  
**And** `QMessageBox.warning` shows the exact message:

> This folder already exists and is not empty. Luthier only creates new projects. Choose an empty folder or a different project name.

**Suggested dialog title:** `"Generate Project"` (consistent with other MainWindow warnings).

### AC2 — Fresh path allowed

**Given** target project directory does **not** exist (parent destination may exist)  
**When** user clicks Generate  
**Then** generation proceeds (current behaviour — `ProjectWriter` creates via tmp rename)

### AC3 — Empty existing directory allowed

**Given** target project directory **exists** as an **empty** directory (`mkdir` with no children)  
**When** user clicks Generate  
**Then** generation proceeds (PO decision — empty is OK; writer replaces empty dir via existing atomic write)

### AC4 — Core defense-in-depth

**Given** `ProjectGenerator.generate(spec)` called directly (bypassing UI)  
**When** target directory exists and is non-empty  
**Then** generation does **not** run `ProjectWriter.write()`  
**And** raises a clear exception (e.g. `GenerateBlockedError`) with the same user-facing message string

### AC5 — Overwrite confirm removed

**Given** codebase after story  
**Then** `_confirm_overwrite()` is **deleted**  
**And** no `confirm_yes_no` / overwrite dialog for Generate  
**And** `ProjectGenerator.project_exists()` removed or replaced by the guard helper (no dead API)

### AC6 — Tests cover guard matrix

**Given** unit tests (preferred: `tests/unit/test_generate_guard.py`)  
**Then** cover at minimum:
- non-empty existing dir → blocked (UI helper and/or `ProjectGenerator.generate` raises)
- empty existing dir → allowed (generate succeeds)
- fresh path (subdir absent) → allowed (generate succeeds)

**And** conflicting regenerate tests updated or removed so full `pytest` passes:
- `tests/integration/test_round_trip.py::test_regenerate_produces_identical_tree`
- `tests/integration/test_round_trip.py::test_regenerate_preserves_juce_dir`
- `tests/unit/test_project_writer.py::test_regenerate_preserves_git_directory`

*(Story 9.6 will broaden scaffold-only test alignment; 9.2 must not leave CI red.)*

### AC7 — Architecture docs updated

**Given** AD-4 / generate guard documented in planning  
**Then** `_bmad-output/project-context.md` and `architecture-spine.md` AD-4 rule no longer reference `_confirm_overwrite()`  
**And** data flow mentions pre-generate guard before `ProjectGenerator.generate()`

## Tasks / Subtasks

- [x] **Add core guard helper** (AC: 1, 2, 3, 4)
  - [x] In `core/project_generator.py` (or small `core/generate_guard.py` if cleaner): constant `GENERATE_BLOCKED_MESSAGE`, function `project_dir_for_spec(spec) -> Path`, function `destination_blocks_generate(project_dir: Path) -> bool`
  - [x] Logic: `not exists` → allow; `exists` and not directory → block; `exists` and empty dir → allow; `exists` and `any(iterdir())` → block
  - [x] `ProjectGenerator.generate()`: call guard at top; raise `GenerateBlockedError(GENERATE_BLOCKED_MESSAGE)` when blocked
- [x] **Replace app-layer overwrite confirm** (AC: 1, 5)
  - [x] `app/main_window.py`: remove `_confirm_overwrite()`; in `_on_generate()` after destination picker / validity, call guard on `project_dir_for_spec(spec)`
  - [x] On block: `_set_status(message, ok=False)` + `QMessageBox.warning(self, "Generate Project", message)`; return without `_run_generation`
  - [x] `_run_generation`: optionally catch `GenerateBlockedError` as belt-and-suspenders (should not happen if `_on_generate` guards first)
- [x] **Remove dead API** (AC: 5)
  - [x] Delete `ProjectGenerator.project_exists()` if fully superseded
  - [x] Grep `project_exists` / `_confirm_overwrite` / `Overwrite project` — zero hits except changelog/docs
- [x] **Tests** (AC: 6)
  - [x] Add `tests/unit/test_generate_guard.py` — pure Path matrix + `ProjectGenerator.generate` integration via `tmp_path`
  - [x] Remove or rewrite the three `test_regenerate_*` tests listed in AC6
  - [x] Run `.venv/bin/pytest` — full suite green
- [x] **Update architecture context** (AC: 7)
  - [x] `_bmad-output/project-context.md`: data flow guard step; revise Known Issue #2 (destructive overwrite no longer user-accessible)
  - [x] `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md`: AD-4 rule — hard block replaces `_confirm_overwrite()`
  - [x] `_bmad-output/implementation-artifacts/deferred-work.md`: close item « `_confirm_overwrite` still allows destructive regeneration »

### Review Findings

- [x] [Review][Patch] Status bar uses short `GENERATE_BLOCKED_STATUS` instead of PO message [`app/main_window.py:472`, `app/main_window.py:491`, `core/project_generator.py:20`] — AC1 partial, Dev Guardrail #2; dialog shows exact string but `_set_status` uses `"Generation blocked — folder not empty."`; spec tasks require same `message` for both surfaces; fix: use `GENERATE_BLOCKED_MESSAGE` everywhere and remove `GENERATE_BLOCKED_STATUS`
- [x] [Review][Patch] `GenerateBlockedError.message` not asserted in tests [`tests/unit/test_generate_guard.py:46`] — AC4/AC6 gap; `test_generate_blocked_on_non_empty` only checks exception type, not `error.message == GENERATE_BLOCKED_MESSAGE`
- [x] [Review][Defer] `iterdir()` PermissionError uncaught [`core/project_generator.py:38`] — deferred, pre-existing pattern; rare on desktop; would surface as generic "Generation failed" not block UX
- [x] [Review][Defer] TOCTOU between guard check and `ProjectWriter.write()` [`core/project_generator.py:63-67`] — deferred, pre-existing; concurrent population between UI check and write is out of v1.0 scope; defense-in-depth catch mitigates user double-click only
- [x] [Review][Defer] Tilde paths not expanded in `project_dir_for_spec()` [`core/project_generator.py:30`] — deferred, pre-existing; `resolve_dir()` expands `~` but guard uses raw `Path(host_destination_dir())`; same path construction existed before 9.2
- [x] [Review][Defer] Hidden-file block scenario not tested (`.DS_Store`, `.git`) [`tests/unit/test_generate_guard.py`] — deferred; behavior correct via `any(iterdir())`; AC6 minimum matrix met; broader coverage deferred to Story 9.6
- [x] [Review][Defer] No integration test for end-to-end UI block flow [`app/main_window.py`] — deferred, pre-existing AD-6; unit guard matrix + manual smoke per spec; Qt widget tests out of scope

## Dev Notes

### Current state — files to modify

#### `app/main_window.py` — overwrite path (REPLACE)

```448:486:app/main_window.py
    def _on_generate(self) -> None:
        spec = self._project_page.spec()
        dest = spec.host_destination_dir().strip()
        if not dest or resolve_dir(dest) is None:
            chosen = QFileDialog.getExistingDirectory(
                ...
            )
            ...
        if not self._confirm_overwrite(spec):
            return
        self._run_generation(spec)

    def _confirm_overwrite(self, spec: ProjectSpec) -> bool:
        if not self._generator.project_exists(spec.host_destination_dir(), spec.project_name):
            return True
        return confirm_yes_no(
            self,
            "Overwrite project",
            f"A folder named '{spec.project_name}' already exists. Overwrite it?",
            default_yes=False,
        )
```

**Target `_on_generate` flow:**
1. Existing destination picker when host path missing (unchanged)
2. `project_dir = Path(spec.host_destination_dir()) / spec.project_name`
3. If `destination_blocks_generate(project_dir)`: status + warning dialog → return
4. `_run_generation(spec)` — no confirm dialog

**Preserve:** `_run_generation` success path — `ProjectPage.load(spec)`, `AppState.remember_parent()`, status OK message.

#### `core/project_generator.py` — thin guard insertion

```36:44:core/project_generator.py
    def project_exists(self, destination: str, project_name: str) -> bool:
        return (Path(destination) / project_name).exists()

    def generate(self, spec: ProjectSpec) -> Path:
        project_dir = Path(spec.host_destination_dir()) / spec.project_name
        context = render_context.build_context(spec)
        ...
```

- `project_exists` checks **existence only** — insufficient for FR10; **remove** after guard lands
- `generate()` must refuse **before** `ProjectWriter.write()` when blocked — defense-in-depth

#### `core/project_writer.py` — **no behavioural change required**

Atomic tmp-dir write still replaces an **empty** existing directory. Do **not** add a second conflicting guard inside `write()` unless dev agent wants redundant check — single source of truth in `project_generator` is enough per handoff §9.2.

**Docstring note:** `write()` docstring still warns that replacing existing project dir is destructive — accurate for empty-dir case only after 9.2.

### Suggested guard implementation

```python
# core/project_generator.py (sketch)

GENERATE_BLOCKED_MESSAGE = (
    "This folder already exists and is not empty. "
    "Luthier only creates new projects. "
    "Choose an empty folder or a different project name."
)

class GenerateBlockedError(Exception):
    def __init__(self, message: str = GENERATE_BLOCKED_MESSAGE) -> None:
        super().__init__(message)
        self.message = message

def project_dir_for_spec(spec: ProjectSpec) -> Path:
    return Path(spec.host_destination_dir()) / spec.project_name

def destination_blocks_generate(project_dir: Path) -> bool:
    if not project_dir.exists():
        return False
    if not project_dir.is_dir():
        return True
    return any(project_dir.iterdir())
```

Import guard helpers in `main_window.py` from `core.project_generator` (keep one module unless file grows past clean-code limits).

### User message — exact string (PO)

Use **verbatim** (including final period):

`This folder already exists and is not empty. Luthier only creates new projects. Choose an empty folder or a different project name.`

Single constant shared by UI and core exception — prevents drift.

### Planning nuance — markers vs non-empty

Sprint change proposal §5 F4 also mentions blocking when folder contains `.luthier.json` or Luthier-signed `CMakeLists.txt`. **Implementation rule for 9.2:** the **`any(iterdir())` non-empty check is sufficient** — those markers always imply a non-empty directory. Do **not** add separate marker detection unless product owner requests it later.

### Tests that conflict today

| Test | Current behaviour | Required change |
|------|-------------------|-----------------|
| `test_regenerate_produces_identical_tree` | Calls `generate()` twice on same spec | **Remove** or replace with `pytest.raises(GenerateBlockedError)` on second call |
| `test_regenerate_preserves_juce_dir` | Regenerate asserts sidecar/CMake unchanged | **Remove** — regenerate no longer supported |
| `test_regenerate_preserves_git_directory` | Regenerate preserves `.git` | **Remove** — git preservation on regenerate is out of scope for scaffold-only |

**New tests (minimum):**

```python
def test_destination_blocks_non_empty_dir(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    (project_dir / "CMakeLists.txt").write_text("cmake", encoding="utf-8")
    assert destination_blocks_generate(project_dir) is True

def test_destination_allows_empty_dir(tmp_path):
    project_dir = tmp_path / "MyPlugin"
    project_dir.mkdir()
    assert destination_blocks_generate(project_dir) is False

def test_destination_allows_missing_dir(tmp_path):
    assert destination_blocks_generate(tmp_path / "MyPlugin") is False

def test_generate_blocked_on_non_empty(tmp_path):
    spec = make_spec(tmp_path)
    generator = ProjectGenerator()
    generator.generate(spec)  # first OK
    with pytest.raises(GenerateBlockedError):
        generator.generate(spec)
```

### Target data flow (post-9.2)

```
User clicks Generate
  → ProjectPage.spec() → ProjectSpec
  → (optional) destination folder picker
  → destination_blocks_generate(project_dir)?
       yes → status error + QMessageBox.warning → STOP
       no  → ProjectGenerator.generate(spec)
              → ProjectWriter.write() (atomic; may replace empty dir)
       → ProjectPage.load(spec) + AppState.remember_parent()
```

### Overlap with other Epic 9 stories

| Story | Boundary |
|-------|----------|
| 9.1 | Open removal — **done**; do not touch |
| 9.7 | UI accent/tree — **done**; do not touch |
| 9.3–9.4 | Plugin characteristics — **out of scope** |
| 9.6 | Broader test doc alignment — 9.2 fixes regenerate tests minimally; 9.6 may add more guard coverage |
| 9.5 | User manuals / QA checklists mentioning guard — **out of scope** (9.5 adds docs) |

### Out of scope

- User manual / README updates for generate guard — Story 9.5
- Plugin form changes — Stories 9.3–9.4
- Qt widget automated tests for dialog — manual smoke only (AD-6)
- Brownfield merge, partial overwrite, protected zones

### Project Structure Notes

- **Layer boundaries (AD-8):** Guard logic in `core/`; UI shows dialog + status in `app/main_window.py`
- **Clean code limits:** Guard functions ≤15 lines; extract exception class if needed
- **No comments policy:** no story/ticket references in code
- **Run:** `.venv/bin/python main.py`
- **Tests:** `.venv/bin/pytest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 9.2]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md §5 F4, AD-4]
- [Source: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §8 Story 9.2, §9.2]
- [Source: _bmad-output/implementation-artifacts/9-1-remove-open-project-scaffold-only-positioning.md — deferred overwrite]
- [Source: app/main_window.py — `_on_generate`, `_confirm_overwrite`]
- [Source: core/project_generator.py — `project_exists`, `generate`]
- [Source: core/project_writer.py — atomic write / rmtree on existing dir]
- [Source: tests/integration/test_round_trip.py — regenerate tests to remove]

## Dev Agent Guardrails

### Technical requirements

1. **Hard block only:** No « Continue anyway », no overwrite confirm — PO §5 F4 / FR10.
2. **Exact user message:** Single shared constant; status bar and dialog use the same string.
3. **Empty dir OK:** `mkdir` then Generate must succeed — regression test required.
4. **Core guard mandatory:** UI check alone is insufficient — `ProjectGenerator.generate()` must raise before `ProjectWriter.write()`.
5. **Do not regress 9.1/9.7:** No Open Project resurrection; no `accentColor` in sidecar; no Project-tab accent.
6. **Preferences untouched:** Generate still must not call `prefs.save()` (AD-5).

### Architecture compliance

| AD | Before (pre-9.2) | After (9.2) |
|----|------------------|-------------|
| AD-4 | Atomic write; overwrite via `_confirm_overwrite()` | Atomic write unchanged; **hard block** before write when target non-empty |
| AD-5 | Generate never writes prefs | Unchanged |
| AD-6 | pytest unit + integration; no Qt tests | Add unit guard tests; manual dialog smoke |
| AD-8 | core/app separation | Guard in core; QMessageBox in app |

Update `architecture-spine.md` AD-4 and `project-context.md` data flow + Known Issues #2.

### Library / framework requirements

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- **Qt:** `QMessageBox.warning(parent, title, message)` — not `confirm_yes_no`
- **pathlib:** `Path.iterdir()` for emptiness — no shelling out

### File structure requirements

| File | Action |
|------|--------|
| `core/project_generator.py` | Add guard + exception; block in `generate()`; remove `project_exists` |
| `app/main_window.py` | Replace `_confirm_overwrite` with guard + warning dialog |
| `tests/unit/test_generate_guard.py` | **New** — guard matrix |
| `tests/integration/test_round_trip.py` | Remove/rewrite regenerate tests |
| `tests/unit/test_project_writer.py` | Remove `test_regenerate_preserves_git_directory` |
| `_bmad-output/project-context.md` | Data flow + Known Issue #2 |
| `architecture-spine.md` | AD-4 revision |
| `_bmad-output/implementation-artifacts/deferred-work.md` | Close overwrite deferral |

**Do not modify:** `Templates/`, plugin characteristics UI, user manuals (`docs/user/`), README guard docs (9.5).

### Testing requirements

**Must pass before marking done:**
```bash
.venv/bin/pytest
grep -r "_confirm_overwrite\|Overwrite project" app/ core/ tests/
grep -r "project_exists" app/ core/ tests/  # should be zero after removal
```

**Manual smoke (required — AD-6):**
1. Generate into fresh folder → success status
2. Click Generate again **without** changing name → warning dialog + error status; **no** files destroyed
3. Create empty `MyPlugin/` under destination → Generate succeeds
4. Put a file in existing `MyPlugin/` → Generate blocked

### Previous story intelligence

**From 9.1 (done):**
- `_confirm_overwrite()` intentionally **left in place** until 9.2 — see 9.1 Review Findings « Defer »
- `ProjectWriter` still destructive when overwrite confirmed — 9.2 removes user access to that path
- `test_regenerate_*` rewritten in 9.1 to generation-only sidecar assertions but still test **successful regenerate** — 9.2 must fix

**From 9.7 (done):**
- No overlap with generate guard — touch `main_window.py` only for `_on_generate` / remove `_confirm_overwrite`; do not revert accent or tree connector work
- Full suite baseline: **240 passed, 3 skipped**

### Git intelligence

Recent Epic 9 commits:
- `a09f879` — Story 9.7: OS tree connectors + live accent theme
- `c163cf2` — Story 9.1: Remove Open Project, delete `project_reader`, prefs-only accent

Follow same patterns: co-locate guard in `core/`, minimal `main_window.py` diff, architecture doc update in same story, pytest green before done.

### Latest tech information

No new libraries. **pathlib** `Path.iterdir()` is the standard emptiness check (Python 3.14 unchanged). Hidden files count as non-empty — correct for macOS `.DS_Store` safety.

**PySide6 `QMessageBox.warning`:** Use for blocking informational errors; unlike `confirm_yes_no`, only an OK button — matches « no Continue anyway » requirement.

## Project Context Reference

Key rules from `_bmad-output/project-context.md`:
- Data flow: `MainWindow._on_generate()` → `ProjectGenerator.generate()` → `ProjectWriter.write()` — **insert guard between page spec and generate**
- AD-5: Generate never writes `preferences.json`
- AD-6: Unit tests for `core/` guard; manual Qt smoke for dialog
- Known Issue #2: destructive `ProjectWriter` — after 9.2, users cannot trigger overwrite on non-empty dirs; empty-dir replace remains internal
- Run via `.venv/bin/python main.py`

## Story Completion Status

- **Status:** done
- **Completion note:** Generate guard implemented — non-empty destination hard-blocked at UI and core layers; overwrite confirm removed; 245 tests pass; code review patches applied (unified PO message on status bar + dialog)
- **Next story after dev:** 9.3 (`9-3-decoupled-plugin-characteristics-and-projectspec`) per PO implementation order

## Dev Agent Record

### Agent Model Used

claude-4.6-sonnet-medium-thinking

### Debug Log References

- Full pytest: 245 passed, 3 skipped
- Grep `_confirm_overwrite|Overwrite project|project_exists` in app/core/tests: zero hits

### Completion Notes List

- Added `GENERATE_BLOCKED_MESSAGE`, `GenerateBlockedError`, `project_dir_for_spec()`, `destination_blocks_generate()` in `core/project_generator.py`
- `ProjectGenerator.generate()` raises `GenerateBlockedError` before `ProjectWriter.write()` when target is non-empty
- Removed `_confirm_overwrite()` and `project_exists()`; `_on_generate()` shows `QMessageBox.warning` + error status on block
- `_run_generation()` catches `GenerateBlockedError` as defense-in-depth
- Added 8 unit tests in `tests/unit/test_generate_guard.py`; removed 3 obsolete regenerate tests
- Updated AD-4 in architecture-spine, data flow + Known Issue #2 in project-context, closed deferred-work item

### File List

- `core/project_generator.py` (modified)
- `app/main_window.py` (modified)
- `tests/unit/test_generate_guard.py` (new)
- `tests/integration/test_round_trip.py` (modified)
- `tests/unit/test_project_writer.py` (modified)
- `_bmad-output/project-context.md` (modified)
- `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` (modified)
- `_bmad-output/implementation-artifacts/deferred-work.md` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

### Change Log

- 2026-07-04: Story 9.2 — hard block Generate on non-empty destination; remove overwrite confirm dialog; guard matrix tests; architecture docs updated
