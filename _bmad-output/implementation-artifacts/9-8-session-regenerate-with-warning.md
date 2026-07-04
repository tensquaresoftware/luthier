---
epic: 9
story: 8
story_key: 9-8-session-regenerate-with-warning
depends_on: [9-2]
blocks: [9-6]
implementation_order: 5
pivot_date: 2026-07-04
correct_course: sprint-change-proposal-2026-07-04-session-regenerate.md
baseline_commit: 97c808c1fc6705c277f1b5b196841ad289fbfe7c
---

# Story 9.8: Session Regenerate with Warning

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a JUCE developer,
I want to regenerate the project I just created in this session after fixing a form setting,
So that I can iterate on the scaffold without manually deleting the folder, while brownfield folders stay protected after I close the app.

## Context

**Correct Course (2026-07-04):** Story **9.2** (FR10) hard-blocks Generate on any non-empty `{destination}/{projectName}/`. PO smoke showed that blocks legitimate **same-session iteration** (Generate → tweak form → Generate again). Brownfield safety (Matrix-Control) must remain after app restart.

**FR10 (revised):** Hard-block on non-empty destination **except** session-only carve-out: same path as last successful Generate this session + explicit destructive confirmation. Replaces entire tree except `.git`. No Open/reload (9.1).

**Planning references:**
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-session-regenerate.md`
- `_bmad-output/planning-artifacts/epics.md` — Epic 9, Story 9.8
- `_bmad-output/implementation-artifacts/9-2-block-generate-non-empty-destination.md` — guard baseline (do not regress)

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.8 → 9.4 → 9.6 → 9.5`

### What changes vs what stays

| Area | Change (9.8) | Keep unchanged |
|------|--------------|----------------|
| Brownfield block | Still hard-block after app restart or unknown folder | `GENERATE_BLOCKED_MESSAGE`, `destination_blocks_generate()` semantics for non-session paths |
| Session iteration | Destructive confirm → regenerate same path | `ProjectWriter.write()` atomic replace + `.git` preservation |
| Open/reload | — | **No** `project_reader`, **no** reading disk into form |
| Generate source of truth | — | Current `ProjectSpec` from form; writer does not read existing `.cpp`/CMake |
| Empty dir / fresh path | — | First generate behaviour (9.2 AC2/AC3) |

### UX decision (PO default)

**Use the existing Generate Project button** — do **not** add a separate Regenerate button unless PO explicitly overrides during dev.

When the target is non-empty **and** matches the in-memory session target from the last successful Generate, show **`confirm_yes_no`** (destructive) instead of the FR10 `QMessageBox.warning` hard block.

**Suggested confirm copy:**

- **Title:** `Regenerate Project`
- **Message:** `This will replace everything in "{project_name}" except the .git folder. Any changes you made in Finder or your IDE since the last generation will be lost. Continue?`
- **Buttons:** Yes / No — **`default_yes=False`** (same safety posture as old overwrite dialog)

On success, status bar: `Project regenerated at {path}` (or keep existing success wording — pick one and use consistently).

## Acceptance Criteria

### AC1 — Session same-path regenerate with confirm

**Given** user successfully generated to `{destination}/{projectName}/` in this app session (folder now non-empty)  
**When** user clicks **Generate Project** with the **same** resolved `project_dir` (unchanged destination + project name)  
**Then** FR10 hard-block dialog does **not** appear  
**And** destructive `confirm_yes_no` appears (AC copy above)  
**And** on **Yes**, `_run_generation` runs and output reflects **current** `ProjectSpec` from the form  
**And** on **No**, generation does not start; disk unchanged

### AC2 — Post-session brownfield block unchanged (9.2 regression guard)

**Given** app freshly launched (new session — in-memory session target is empty)  
**When** target `{destination}/{projectName}/` exists and is non-empty  
**Then** Story 9.2 behaviour: `GENERATE_BLOCKED_MESSAGE` + `QMessageBox.warning`; no generate

### AC3 — Different non-empty path still blocked

**Given** user generated to path A this session  
**When** user points form at path B (different destination or project name) and B is non-empty  
**Then** Story 9.2 hard-block applies — **no** session carve-out, **no** destructive confirm

### AC4 — Session target tracking (in-memory only)

**Given** successful Generate to `project_dir`  
**Then** app records `last_generated_project_dir` (resolved `Path`) for this session only  
**And** field is **not** written to `app_state.json` (quit app → session ends → brownfield protection restored)  
**And** updated after each successful generate/regenerate to the same canonical resolved path

**Suggested API:** `AppState` holds `_last_generated_project_dir: Path | None = None` with `remember_generated_project(project_dir: Path)` / `last_generated_project_dir() -> Path | None` — **exclude from `save()`/`load()`**.

Alternative acceptable: `MainWindow._last_generated_project_dir` if dev keeps session state out of `AppState` — prefer `AppState` in-memory field for testability.

### AC5 — Core defense-in-depth

**Given** `ProjectGenerator.generate(spec)` without overwrite permission  
**When** target non-empty  
**Then** still raises `GenerateBlockedError` (9.2 unchanged)

**Given** `ProjectGenerator.generate(spec, allow_overwrite=True)` (or equivalent keyword)  
**When** target non-empty  
**Then** guard skipped; `ProjectWriter.write()` runs (existing replace semantics)

**Given** direct API call with `allow_overwrite=True` bypassing UI  
**Then** allowed at core level — UI is responsible for confirm; document in dev notes

### AC6 — `.git` preserved on regenerate

**Given** project directory contains `.git/` from user init  
**When** session regenerate confirmed and succeeds  
**Then** `.git` directory still present (existing `ProjectWriter` `_relocate_git_directory` — **no writer changes required** unless tests fail)

### AC7 — Tests

**Given** `tests/unit/test_generate_guard.py` (extend) or adjacent module  
**Then** cover at minimum:
- First generate + second `generate(spec, allow_overwrite=True)` succeeds; sidecar/files updated
- Second `generate(spec)` without flag still raises `GenerateBlockedError`
- `session_same_path(project_dir, last_generated)` helper logic: match → carve-out eligible; mismatch → not eligible
- Optional integration-style: simulate fresh `AppState()` → non-empty dir blocked at UI decision layer (unit-test the predicate function extracted from `_on_generate`)

**And** existing 9.2 tests remain green (non-empty block without session flag).

### AC8 — Architecture docs

**Given** story complete  
**Then** `_bmad-output/project-context.md` data flow reflects session branch (already drafted in Correct Course — verify matches implementation)  
**And** `architecture-spine.md` AD-4 mentions session carve-out (already drafted — verify)

## Tasks / Subtasks

- [x] **Session target state** (AC: 4)
  - [x] Add in-memory `last_generated_project_dir` on `AppState` (not persisted) with remember/query helpers
  - [x] Call `remember_generated_project(project_dir.resolve())` in `_run_generation` after successful generate
- [x] **UI flow in `_on_generate`** (AC: 1, 2, 3)
  - [x] Extract predicate e.g. `session_regenerate_eligible(project_dir, last_generated) -> bool` (same resolved path)
  - [x] If `destination_blocks_generate(project_dir)`:
    - If session eligible → `confirm_yes_no` → on Yes call `_run_generation(spec, allow_overwrite=True)`; on No return
    - Else → existing FR10 warning + return
  - [x] If not blocked → `_run_generation(spec)` as today
- [x] **Core flag** (AC: 5)
  - [x] Add `allow_overwrite: bool = False` to `ProjectGenerator.generate()`; skip guard when True
  - [x] Thread flag through `_run_generation` from UI
- [x] **Tests** (AC: 6, 7)
  - [x] Extend `test_generate_guard.py` per AC7
  - [x] Run `.venv/bin/pytest` — full suite green
- [x] **Docs verify** (AC: 8)
  - [x] Confirm project-context + architecture-spine match shipped behaviour

### Review Findings

- [x] [Review][Patch] Path resolution split breaks session carve-out for `~` destinations — UI uses `resolved_project_dir_for_spec()` (expanduser+resolve) but `ProjectGenerator.generate()` still writes via `project_dir_for_spec()`; `remember_generated_project()` resolves without expanduser, so `~/Projects/MyPlugin` ≠ `/Users/.../Projects/MyPlugin` and regenerate eligibility fails (AC1, AC4, path-resolution note). [`core/project_generator.py:81`, `core/app_state.py:152`, `app/main_window.py:471`]
- [x] [Review][Patch] Hard-block status bar regressed to short `GENERATE_BLOCKED_STATUS` — Story 9.2 review fixed this to use full `GENERATE_BLOCKED_MESSAGE` in `_set_status`; diff reintroduces short status while dialog keeps full message (AC2, 9.2 regression). [`app/main_window.py:489`, `app/main_window.py:509`, `core/project_generator.py:20`]
- [x] [Review][Patch] Missing tilde path test for session memory vs eligibility — no test that `remember_generated_project(generate(spec))` + `session_regenerate_eligible(resolved_project_dir_for_spec(spec), …)` stays true when `host_destination_dir` contains `~` (AC7). [`tests/unit/test_generate_guard.py`]
- [x] [Review][Defer] Non-directory project path on session regenerate — if path exists as a file after first generate, carve-out offers destructive confirm then `ProjectWriter` fails with generic error instead of clean block. [`app/main_window.py:472`, `core/project_generator.py:83`] — deferred, rare edge
- [x] [Review][Defer] TOCTOU between eligibility check and confirm dialog — folder state can change while modal is open; no re-check before `generate(allow_overwrite=True)`. [`app/main_window.py:474-487`] — deferred, desktop low-risk
- [x] [Review][Defer] Double-click Generate race — no guard against overlapping `_run_generation(allow_overwrite=True)` calls. [`app/main_window.py:487`] — deferred, pre-existing pattern
- [x] [Review][Defer] Partial success if `save()` fails after generate — `remember_generated_project` already updated but parent-dir memory failed; ambiguous retry UX. [`app/main_window.py:517-527`] — deferred, pre-existing pattern
- [x] [Review][Defer] AC3 session scenario test gap — different-path block tested at helper level only, not with `AppState.remember_generated_project(A)` + target B. [`tests/unit/test_generate_guard.py:24-29`] — deferred, helper coverage sufficient for now

## Dev Notes

### Current state — files to modify

#### `app/main_window.py` — `_on_generate` / `_run_generation`

```454:508:app/main_window.py
    def _on_generate(self) -> None:
        ...
        project_dir = project_dir_for_spec(spec)
        if destination_blocks_generate(project_dir):
            self._set_status(GENERATE_BLOCKED_MESSAGE, ok=False)
            QMessageBox.warning(self, "Generate Project", GENERATE_BLOCKED_MESSAGE)
            return
        self._run_generation(spec)

    def _run_generation(self, spec: ProjectSpec) -> None:
        try:
            project_dir = self._generator.generate(spec)
        ...
        self._project_page.load(spec)
        self._app_state.remember_parent(spec.host_destination_dir())
```

**Target `_on_generate` flow:**
1. Destination picker + validity (unchanged)
2. `project_dir = project_dir_for_spec(spec).resolve()` (match 9.2 review note on tilde — use same resolution as guard if `resolve_dir` available on host path)
3. If `destination_blocks_generate(project_dir)`:
   - If `project_dir == self._app_state.last_generated_project_dir()` (or helper): show destructive confirm → `_run_generation(spec, allow_overwrite=True)` or return
   - Else: FR10 warning (unchanged)
4. Else: `_run_generation(spec)`

**Preserve after success:** `ProjectPage.load(spec)`, `remember_parent`, `remember_generated_project`, status OK.

#### `core/project_generator.py` — guard bypass

```60:67:core/project_generator.py
    def generate(self, spec: ProjectSpec) -> Path:
        project_dir = project_dir_for_spec(spec)
        if destination_blocks_generate(project_dir):
            raise GenerateBlockedError()
        ...
```

Add optional `allow_overwrite: bool = False`. When False, behaviour identical to 9.2. When True, skip `destination_blocks_generate` check only — still build context and call writer.

**Do not** add session logic to core — session is UI/`AppState` concern; core only exposes explicit overwrite permission after UI confirm.

#### `core/app_state.py` — session field

Current persisted fields: `lastUsedParentDir`, `lastPrefsProfileDir`, window geometry. Add:

```python
self._last_generated_project_dir: Path | None = None  # NOT in _default_data / save / load
```

#### `core/project_writer.py` — **no behavioural change expected**

```66:87:core/project_writer.py
    def write(self, context: dict, tokens: dict, spec: ProjectSpec) -> None:
        ...
            if self._project.exists():
                git_src = self._project / ".git"
                if git_src.is_dir():
                    ...
                _robust_rmtree(self._project)
            tmp.rename(self._project)
```

Regenerate is exactly this path — writer never reads existing sources except relocating `.git`.

#### `app/confirm.py` — reuse

Use existing `confirm_yes_no(parent, title, message, default_yes=False)` — same pattern as pre-9.2 overwrite (removed in 9.2).

### Anti-patterns (do NOT)

- **Do not** reintroduce Open Project or read `.luthier.json` / CMake into the form
- **Do not** persist `lastGeneratedProjectDir` to `app_state.json` (would weaken post-restart brownfield guard)
- **Do not** allow session carve-out for empty-path changes that happen to point at another user's folder
- **Do not** auto-regenerate without confirm
- **Do not** weaken `destination_blocks_generate()` itself — keep pure Path predicate; session is layered in UI

### Path resolution note

9.2 deferred tilde expansion in `project_dir_for_spec()`. For session compare, use **consistent** resolution on both sides (e.g. `Path(spec.host_destination_dir()).expanduser().resolve() / spec.project_name` if host path valid, or compare via shared helper). Mismatch between guard path and session path breaks carve-out.

### Previous story intelligence (9.2)

- `GENERATE_BLOCKED_MESSAGE` is single source for hard-block copy — do not reuse for destructive confirm
- `test_generate_blocked_on_non_empty` must still pass without `allow_overwrite`
- Review patched status bar to use full `GENERATE_BLOCKED_MESSAGE` — keep that for hard-block only
- Story 9.6 will broaden test matrix — 9.8 must not leave CI red

### Testing standards

- Unit tests in `tests/unit/` with `tmp_path`, `make_spec` from `tests/conftest.py`
- Run full suite: `.venv/bin/pytest`
- No Qt widget integration tests required (AD-6 pattern from 9.2)

### Project Structure Notes

- Core guard in `core/project_generator.py`
- UI confirm in `app/main_window.py`
- Session state in `core/app_state.py` (in-memory)
- Tests extend `tests/unit/test_generate_guard.py`

### References

- [Source: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-session-regenerate.md`]
- [Source: `_bmad-output/implementation-artifacts/9-2-block-generate-non-empty-destination.md`]
- [Source: `core/project_writer.py` — atomic write + `.git` preservation]
- [Source: `app/confirm.py` — `confirm_yes_no`]
- [Source: `_bmad-output/project-context.md` — Data Flow]

## Dev Agent Record

### Agent Model Used

Composer (Cursor)

### Debug Log References

### Completion Notes List

- Added in-memory `AppState.remember_generated_project()` / `last_generated_project_dir()` — excluded from JSON persistence.
- Added `session_regenerate_eligible()`, `resolved_project_dir_for_spec()`, and `allow_overwrite` on `ProjectGenerator.generate()`.
- `_on_generate` shows destructive `confirm_yes_no` for same-session same-path targets; FR10 hard-block unchanged for brownfield/different paths.
- Status bar: "Project regenerated at …" on overwrite success.
- Tests: 291 passed, 3 skipped. Docs verified (project-context data flow + architecture-spine AD-4 already reflect session carve-out).
- Code review patches: unified path resolution via `resolved_project_dir_for_spec()` in `generate()` + `expanduser().resolve()` in session memory/compare; restored full `GENERATE_BLOCKED_MESSAGE` in status bar; added tilde session eligibility test.

### File List

- `core/app_state.py`
- `core/project_generator.py`
- `app/main_window.py`
- `tests/unit/test_generate_guard.py`
- `tests/unit/test_app_state.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/9-8-session-regenerate-with-warning.md`

### Change Log

- 2026-07-04: Story 9.8 — session regenerate with destructive confirm; core `allow_overwrite` flag; in-memory session target tracking.
