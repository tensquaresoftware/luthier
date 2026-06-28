# Sprint Change Proposal — Epic 7: Release Hardening

**Project:** Luthier  
**Date:** 2026-06-28  
**Author:** Correct Course workflow (Batch mode)  
**Change signal:** Post-MVP hardening before intensive manual testing (week of 2026-07-07)  
**Source registry:** `_bmad-output/implementation-artifacts/deferred-work.md` (resync 2026-06-28)  
**Scope classification:** **Moderate** — new epic, backlog extension, forward adjustment (no rollback)

---

## 1. Issue Summary

### 1.1 Problem Statement

Epics 1–6 are **complete** (`sprint-status.yaml`, `last_updated: 2026-06-26`). The planned MVP is delivered: generation, reload, test suite, distribution bundles, and UX polish workflows are in place.

Before intensive manual testing (target: week of **2026-07-07**), the codebase still carries **consolidated technical debt** documented in `deferred-work.md`. This debt does not invalidate the MVP but increases regression risk during manual QA and future maintenance:

| Area | Gap | PO priority |
|------|-----|-------------|
| **CI** | No GitHub Actions workflow; pytest runs locally only | **MUST** |
| **JSON persistence** | Non-atomic writes for `preferences.json` / `app_state.json`; silent fallback on corrupt JSON | **SHOULD** |
| **Core edge cases** | Special paths, loose `from_dict` typing, weak legacy reader errors, generation corner cases | **SHOULD** |
| **Test hygiene & UI** | Legacy `test_story_*.py` duplication; minor Templates/null-prefs UI gaps; optional coverage expansion | **NICE / defer** |

### 1.2 Trigger Type

- **Post-MVP quality gate** — deliberate hardening sprint after feature epics, not a requirement misunderstanding or strategic pivot.
- **Registry-driven** — items trace to `[Review][Defer]` notes consolidated in `deferred-work.md`; several items already addressed outside BMad (status bar 6-1, dirty guard dialog, StatusCapsule accessibility, logo, AD doc rename) and are **excluded** from Epic 7 scope.

### 1.3 Evidence

| Source | Finding |
|--------|---------|
| `sprint-status.yaml` | Epics 1–6 all `done`; no Epic 7 |
| `deferred-work.md` | Open items across Infrastructure, JSON, core, UI, tests |
| `.github/workflows/` | **Absent** — no CI pipeline |
| `core/preferences.py`, `core/app_state.py` | Direct `write_text()` — not atomic (contrast `ProjectWriter` AD-4) |
| `tests/test_story_*.py` | 3 legacy files overlap canonical `tests/unit/` and `tests/integration/` |
| `tests/integration/test_cmake_cross_platform.py` | Already skips when `cmake` / `JUCE_DIR` unavailable — CI-safe |
| PRD §9 | CI/CD listed out of MVP scope — **post-MVP addition**, not MVP scope change |

**Out of Epic 7 scope (already done or separate):** window geometry persistence, 6-1 status bar, StatusCapsule screen-reader labels, README logo, dirty-guard dialog accent, Windows JSON path normalization, preset JSON validation (4-3), 5-3/5-5 deliverables, `architecture-explained.md` rename.

---

## 2. Impact Analysis

### 2.1 Checklist Summary

| Section | Status | Notes |
|---------|--------|-------|
| 1 — Trigger & context | [x] Done | Post-MVP hardening; PO priorities explicit; deferred-work resync 2026-06-28 |
| 2 — Epic impact | [x] Done | New Epic 7; Epics 1–6 remain **done** (no rollback) |
| 3 — Artifact conflicts | [x] Done | PRD §9 CI out-of-scope → post-MVP addendum; architecture AD-4 pattern extends to JSON; epics.md + sprint-status |
| 4 — Path forward | [x] Done | Direct Adjustment + new epic (Option 1); Rollback rejected; MVP Review rejected |
| 5 — Proposal components | [x] Done | This document |
| 6 — Final review | [!] Action-needed | **Awaiting PO approval** |

### 2.2 Epic Impact

| Epic | Status | Impact |
|------|--------|--------|
| Epic 1 — Core Architecture | **done** | Stories unchanged; 7.3 may tighten `from_dict`, CMake emission, `ProjectWriter` edge cases |
| Epic 2 — Reliable Reload | **done** | 7.3 improves `project_reader` error discrimination and sidecar validation |
| Epic 3 — Test Suite | **done** | 7.1 adds CI; 7.4 consolidates legacy tests; optional coverage |
| Epic 4 — Distribution | **done** | Optional PyInstaller smoke tests in 7.4 only |
| Epic 5 — Workflows | **done** | 7.2 hardens prefs persistence; 7.4 minor import/null UI |
| Epic 6 — UX Polish | **done** | No functional rollback; 7.4 minor Templates editor polish |
| **Epic 7 — Release Hardening** | **new — backlog** | Addresses open deferred-work before manual QA week |

### 2.3 PRD / MVP Impact

**MVP scope unchanged.** All FR1–FR9 and NFR1–NFR5 remain satisfied by Epics 1–6.

Epic 7 is **post-MVP engineering quality**:

- CI was explicitly out of MVP scope (PRD §9) but is now a **PO must-have** for regression safety before manual testing.
- Hardening items do not add user-facing features; they improve reliability, observability, and maintainability.

**Optional PRD addendum (post-approval, low priority):** Add a short §10 *Post-MVP Quality* bullet referencing automated CI and persistence hardening — or document solely in epics.md / CONTRIBUTING.md without PRD edit.

### 2.4 Architecture Impact

| Invariant / area | Change |
|------------------|--------|
| **AD-4 pattern** | Extend atomic write discipline to `preferences.json` and `app_state.json` (7.2) — same temp-then-rename semantics as `ProjectWriter` |
| **AD-6** | Unchanged tier rules; CI enforces existing pytest suite; still no Qt widget tests |
| **Error propagation** | 7.2/7.3: corrupt JSON and reader failures surface user-visible messages via existing status bar / dialog patterns (Epic 6) |
| **Consistency conventions** | UTF-8 on all JSON I/O (already convention); no new layer boundaries |

**Proposed architecture-spine addendum (optional, Story 7.2 AC):**

```markdown
### AD-10 — Atomic JSON persistence for app config

- **Binds:** `Preferences`, `AppState`
- **Prevents:** truncated or corrupt `preferences.json` / `app_state.json` after crash mid-write
- **Rule:** config JSON files are written via a sibling temp file then atomically replaced — same commit semantics as AD-4. On read failure, fall back to in-memory defaults and notify the user; never silently pretend a corrupt file loaded successfully. [PROPOSED — Epic 7.2]
```

### 2.5 Technical Impact

| Module / area | Stories | Change |
|---------------|---------|--------|
| `.github/workflows/` | 7.1 | New pytest CI workflow |
| `core/preferences.py`, `core/app_state.py` | 7.2 | Atomic save; corrupt-load feedback hook |
| `app/main_window.py` or prefs bootstrap | 7.2 | Surface corrupt-file message on startup |
| `core/project_spec.py` | 7.3 | Bool coercion in `from_dict`; sidecar type validation |
| `core/render_context.py`, CMake templates | 7.3 | Special-char quoting; `CACHE BOOL` + `FORCE` |
| `core/project_reader.py` | 7.3 | Discriminative errors; empty sidecar warning |
| `core/project_writer.py`, `core/project_generator.py` | 7.3 | Rename safety; explicit unknown plugin type |
| `app/pages/templates_page.py`, prefs UI | 7.4 | Minor UX fixes |
| `tests/` | 7.1, 7.4 | CI config; merge/remove `test_story_*.py`; optional parametrization |
| `CONTRIBUTING.md` | 7.1 | CI badge / “checks run on PR” note |

**Risk:** Low–medium — mostly isolated hardening; highest risk in 7.3 (generation/reload edge cases).  
**Effort:** Medium — 4 stories, ~1 dev session each.  
**Timeline:** Fits one focused sprint before 2026-07-07 manual QA week.

---

## 3. Recommended Approach

### 3.1 Selected Path: **Direct Adjustment (Option 1)**

Add **Epic 7: Release Hardening** with **four stories** grouped from `deferred-work.md` by PO priority. Forward-only extension — **no rollback** of Epics 1–6.

### 3.2 Rejected Alternatives

| Option | Verdict | Rationale |
|--------|---------|-----------|
| Rollback Epics 1–6 | **Not viable** | MVP delivered and stable; debt is incremental hardening |
| MVP scope reduction | **Not viable** | No scope conflict; hardening is post-MVP |
| One story per deferred line | **Rejected** | PO asked for 3–5 deliverable stories, not micro-stories |
| Qt widget tests | **Rejected** | AD-6 invariant; manual QA covers UI |

### 3.3 Priority Classification (PO)

| Priority | Epic 7 coverage |
|----------|-----------------|
| **MUST** | Story 7.1 — GitHub Actions CI for pytest |
| **SHOULD** | Stories 7.2, 7.3 — JSON persistence + core robustness |
| **NICE / defer** | Story 7.4 — test consolidation, minor UI, optional test expansion |

### 3.4 Implementation Order

```
7.1 → 7.2 → 7.3 → 7.4
```

| Order | Rationale |
|-------|-----------|
| **7.1 first** | CI safety net before subsequent hardening commits |
| **7.2 second** | Persistence is isolated; reduces data-loss risk during QA |
| **7.3 third** | Core edge cases benefit from CI catching regressions |
| **7.4 last** | Nice-to-have cleanup; optional items skippable if time-constrained |

**Parallelization note:** 7.2 and 7.3 are loosely coupled; a second developer could work 7.3 after 7.1 if schedule is tight. PO order above is recommended for a single developer.

---

## 4. Epic 7 Proposal

### Epic 7: Release Hardening

**Goal:** Reduce regression and data-loss risk before intensive manual testing by adding automated CI, hardening JSON persistence, closing core edge-case gaps from the deferred-work registry, and optionally cleaning up legacy tests and minor UI rough edges.

**FRs covered:** — (quality / NFR reinforcement; reinforces NFR2, NFR3 observability)  
**Priority:** Post-MVP gate before manual QA week (2026-07-07)

---

#### Story 7.1: GitHub Actions CI for pytest — **MUST**

As a contributor,
I want pytest to run automatically on every push and pull request,
So that regressions in unit and integration tests are caught before merge without relying on local runs only.

**Acceptance Criteria:**

**Given** a push or pull request to the default branch,
**When** GitHub Actions runs,
**Then** a workflow installs Python, creates a venv, installs `requirements-dev.txt`, and runs `pytest`.

**Given** the CI runner (e.g. `ubuntu-latest` or `macos-latest`),
**When** pytest executes,
**Then** all tests under `tests/unit/` and `tests/integration/` are collected and run.

**Given** tests requiring unavailable tooling,
**When** CI runs without CMake, JUCE, or a built PyInstaller bundle,
**Then** those tests skip cleanly (existing `pytest.skip` / markers for `test_cmake_cross_platform.py`, `test_frozen_bundle.py`) — CI does **not** fail because optional environment deps are absent.

**Given** a failing test,
**When** CI completes,
**Then** the workflow exits non-zero and the PR check shows failure.

**Given** `CONTRIBUTING.md`,
**When** Epic 7.1 is complete,
**Then** it documents that CI runs on PRs (and optionally includes a status badge).

**Deferred-work items addressed:** Infrastructure — CI.

---

#### Story 7.2: Atomic JSON Persistence & Corrupt-File Feedback — **SHOULD**

As a JUCE developer,
I want my preferences and app state saved safely and reported clearly when a config file is corrupt,
So that a crash during save never leaves me with a broken profile and I know when defaults were restored.

**Acceptance Criteria:**

**Given** `Preferences.save()` or `AppState.save()` is called,
**When** the file is written,
**Then** content is written to a sibling temp file and atomically replaced (same pattern as `ProjectWriter` AD-4) — a crash mid-write leaves the previous file intact.

**Given** a corrupt or truncated `preferences.json` on startup,
**When** Luthier loads preferences,
**Then** in-memory state falls back to factory defaults **and** a user-visible message explains that the file was reset (status bar or dialog — consistent with Epic 6 patterns).

**Given** a corrupt `app_state.json`,
**When** Luthier loads app state,
**Then** defaults apply and the user is notified similarly.

**Given** unit tests with `tmp_path`,
**When** a simulated crash occurs after temp write but before rename,
**Then** the original JSON file content is unchanged.

**Given** Epic 7.2 completion,
**When** architecture docs are updated,
**Then** AD-10 (or AD-4 cross-reference) documents atomic JSON persistence for app config.

**Explicitly deferred within this story:** schema `version` field for migrations — track in `deferred-work.md` if not implemented; not blocking QA week.

**Deferred-work items addressed:** JSON — non-atomic write, silent corrupt load.

---

#### Story 7.3: Core Generation & Reload Robustness — **SHOULD**

As a JUCE developer,
I want generation and project reload to handle edge-case inputs and legacy projects gracefully,
So that unusual paths, hand-edited sidecars, and legacy CMake projects fail with clear, actionable messages instead of silent corruption or raw exceptions.

**Acceptance Criteria:**

**Given** a `juce_dir` containing quotes, `$`, or spaces,
**When** `CMakeLists.txt` is generated,
**Then** the `set(JUCE_DIR ...)` line is correctly quoted/escaped for CMake.

**Given** artefact JSON path fields with quotes or control characters,
**When** presets are rendered,
**Then** output remains valid JSON (beyond existing backslash normalization).

**Given** a sidecar or dict with string booleans (`"ON"`, `"false"`, `"true"`, `"OFF"`),
**When** `ProjectSpec.from_dict()` runs,
**Then** copy flags and similar bool fields coerce to proper `bool` values.

**Given** a hand-edited `.luthier.json` with wrong types or `null` for required fields,
**When** `read_project()` loads the sidecar,
**Then** validation fails explicitly (returns `None` or raises a typed error) — no silent partial load.

**Given** an empty but syntactically valid `.luthier.json` (`{}`),
**When** `read_project()` runs,
**Then** load fails with a warning/error distinguishing empty sidecar from parse failure (not silent defaults).

**Given** CMake cache variables for bool plugin options in the template,
**When** a project is regenerated,
**Then** `CACHE BOOL` entries use `FORCE` so cached values do not block updates.

**Given** an unknown `pluginType` string,
**When** generation or context build runs,
**Then** a clear validation error is raised — not a raw `KeyError`.

**Given** `ProjectWriter.write()` when atomic rename fails after old directory removal,
**When** the failure path executes,
**Then** behaviour is documented and tested for the rare case (temp preserved or explicit error; no silent data loss).

**Given** a legacy project without sidecar,
**When** CMake fallback fails,
**Then** the error message distinguishes: (a) sidecar parse error, (b) empty/invalid sidecar, (c) CMake parse failure — listing missing fields where applicable (extends Story 2.2 intent).

**Given** CMake with escaped quotes in parsed values,
**When** regex fallback runs,
**Then** parsing handles escaped quotes or fails with a clear message (not silent wrong values).

**Given** unit/integration tests,
**When** pytest runs,
**Then** new edge-case tests cover the above without Qt imports.

**Deferred-work items addressed:** Génération/rechargement — chemins spéciaux, booléens, sidecar manuel, CACHE FORCE, plugin type, rename, messages legacy.

---

#### Story 7.4: Test Hygiene & Minor UI Hardening — **NICE / defer**

As a contributor and daily user,
I want redundant legacy tests removed and minor UI rough edges polished,
So that the test suite stays maintainable and small UX gaps do not distract during manual QA.

**Acceptance Criteria:**

**Given** `tests/test_story_1_2.py`, `tests/test_story_2_1.py`, `tests/test_story_2_2.py`,
**When** Epic 7.4 runs,
**Then** their coverage is merged into canonical `tests/unit/` or `tests/integration/` modules (or files removed if fully redundant) — no duplicate test classes remain.

**Given** the Templates tab after **Load from file…**,
**When** a file loads successfully,
**Then** the editor state label reflects the loaded source; invalid file types are rejected with a clear message; unreadable files show an error instead of failing silently.

**Given** `null` JSON values in imported preferences for path fields,
**When** the Preferences or Project UI renders,
**Then** fields show empty string — not the literal `"None"`.

**Given** Import Preferences with a profile that triggers certain `ValueError` paths,
**When** import fails,
**Then** rollback restores the previous in-memory profile completely (no partial state).

**Optional (implement if time permits; skip without blocking Epic 7 done):**

- Parametrize integration round-trip tests across all three `plugin_type` values (effect / instrument / midi).
- Additional edge-case tests: validation boundaries, templates store, render_context, PyInstaller bundle smoke (timeout, encoding, `_internal` layout) — following existing skip patterns when bundle absent.
- Preferences widget coupling refactor (internal attribute access) — **defer** unless needed for 7.4 UI fixes.

**Explicitly out of scope:** Qt widget tests for `MainWindow` (AD-6).

**Deferred-work items addressed:** Tests legacy, Interface mineur (Templates, null prefs, import rollback); optional Tests durcissement.

---

## 5. Proposed Artifact Updates (Post-Approval Only)

### 5.1 epics.md — Epic List insert

Add after Epic 6:

```markdown
### Epic 7: Release Hardening
Post-MVP quality gate: CI for pytest, atomic JSON persistence, core edge-case robustness, and optional test/UI cleanup before intensive manual testing.
**FRs covered:** — (reinforces NFR2, NFR3)
**Priority:** Post-MVP (2026-06-28 correct-course)
```

Insert full story blocks 7.1–7.4 (from §4 above) in epics.md body.

### 5.2 sprint-status.yaml — Proposed entries

```yaml
  # Epic 7: Release Hardening (post-MVP quality gate)
  epic-7: backlog
  7-1-github-actions-ci-for-pytest: backlog
  7-2-atomic-json-persistence-corrupt-file-feedback: backlog
  7-3-core-generation-reload-robustness: backlog
  7-4-test-hygiene-minor-ui-hardening: backlog
  epic-7-retrospective: optional
```

Update header: `last_updated: 2026-06-28 # epic 7 added via correct-course`

### 5.3 deferred-work.md

After each story completes, strike or remove addressed items; leave explicitly deferred items (schema version, widget coupling refactor) documented.

### 5.4 CONTRIBUTING.md

Add CI section (Story 7.1).

### 5.5 architecture-spine.md

Add AD-10 (Story 7.2) if approved.

---

## 6. Implementation Handoff

### 6.1 Scope Classification: **Moderate**

Requires backlog reorganization (new epic), CI infrastructure, and coordinated core + app-layer hardening. No strategic replan.

### 6.2 Handoff Recipients

| Role | Responsibility |
|------|----------------|
| **PO (Guillaume)** | **Approve this proposal**; confirm MUST/SHOULD/NICE boundaries; decide if 7.4 optional items run before or after manual QA week |
| **Create Epics and Stories `[CE]`** | Apply approved edits to `epics.md`, `sprint-status.yaml`, architecture AD-10; generate story spec files 7.1–7.4 |
| **Dev Story `[DS]`** | Implement in order 7.1 → 7.2 → 7.3 → 7.4 |
| **Architect (Winston)** | Review AD-10 and 7.3 CMake/JSON edge-case approach if needed |

### 6.3 Post-Approval Actions (Not Applied Until PO Approves)

1. Update `epics.md` (Epic 7 block + story AC)
2. Update `sprint-status.yaml` (Epic 7 entries)
3. Optionally update `architecture-spine.md` (AD-10)
4. Run `[CE]` to generate story files under `implementation-artifacts/`
5. Begin `[DS]` with story **7.1**

### 6.4 Success Criteria (Epic 7 Done)

1. GitHub Actions pytest workflow green on PR (unit + integration; optional tests skip cleanly)
2. `preferences.json` / `app_state.json` atomic writes verified by test
3. Corrupt config file on startup shows user-visible feedback
4. Core edge-case tests pass (special paths, bool coercion, reader error discrimination)
5. No `tests/test_story_*.py` files remain (or PO accepts explicit keep with rationale)
6. Full pytest suite green locally and in CI
7. Manual QA week can proceed without known MUST/SHOULD debt from `deferred-work.md`

### 6.5 Time-Box Guidance

If schedule is tight before 2026-07-07:

| Story | Minimum viable |
|-------|----------------|
| 7.1 | **Required** — full AC |
| 7.2 | **Required** — atomic write + corrupt prefs feedback (app_state feedback may follow in same PR) |
| 7.3 | **Required subset** — bool coercion, reader messages, JUCE quoting; rename edge case + CACHE FORCE if time |
| 7.4 | **Optional** — at minimum merge `test_story_*.py`; UI polish skippable |

---

## 7. Approval

| Field | Value |
|-------|-------|
| Proposal status | **Approved** |
| Approved by | Guillaume (PO), 2026-06-28 |
| Artifacts updated | epics.md, sprint-status.yaml, architecture-spine.md (AD-10), story files 7.1–7.4 |

---

*Generated by bmad-correct-course — Batch mode — 2026-06-28*
