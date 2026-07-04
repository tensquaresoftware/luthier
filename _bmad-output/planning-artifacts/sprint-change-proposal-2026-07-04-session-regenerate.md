# Sprint Change Proposal — Session Regenerate Carve-Out (FR10)

**Date:** 2026-07-04  
**Project:** Luthier  
**Trigger:** Story 9.2 (FR10) implemented — PO smoke reveals overly strict same-session workflow  
**Author:** Correct Course workflow  
**PO approval:** Validated (Guillaume, 2026-07-04)

---

## 1. Issue Summary

### Problem statement

Story **9.2** hard-blocks **Generate** when `{destination}/{projectName}/` exists and is non-empty. That correctly protects brownfield folders (e.g. Matrix-Control) but blocks a legitimate scaffold-only workflow: after a **first successful Generate in the same session**, the user adjusts a form setting (plugin characteristics, JUCE path, etc.) and wants to **regenerate the same skeleton** without changing destination or project name.

Today the second click shows the FR10 warning and stops — no recovery path until the user manually deletes the folder or picks a new name. That is too strict for the **same-session, same-path** case while the app remains open.

### Context and evidence

- **9.2 done:** `destination_blocks_generate()` + `GenerateBlockedError` in `core/project_generator.py`; UI guard in `MainWindow._on_generate()`.
- **PO smoke:** Create → Generate → tweak form → Generate again → blocked (expected per 9.2 AC, undesired per product intent).
- **Brownfield case unchanged:** Opening Luthier fresh and pointing at an existing non-empty project folder must **still** hard-block (Matrix-Control safety).
- **Technical fact:** `ProjectWriter.write()` is driven by current `ProjectSpec` from the form; it does not read existing project files (except `.git` preservation). Finder/IDE edits between generates are overwritten — user must be warned explicitly.

### Trigger story

| ID | Title | Status |
|----|-------|--------|
| 9.2 | Block Generate on Non-Empty Destination | done |
| 9.3 | Decoupled Plugin Characteristics and ProjectSpec | review |

---

## 2. Impact Analysis

### Epic impact

| Epic | Impact |
|------|--------|
| **Epic 9** | **Direct adjustment** — add Story **9.8**; amend FR10; no rollback of 9.2 |
| Epics 1–8 | No change |
| Future epics | None invalidated |

Epic 9 can still complete as planned. Implementation order becomes:

`9.1 → 9.7 → 9.2 → 9.3 → 9.8 → 9.4 → 9.6 → 9.5`

(9.8 before 9.6 so test-suite story can reference session-regenerate semantics.)

### Story impact

| Story | Change |
|-------|--------|
| **9.2** | AC unchanged for brownfield; carve-out delegated to 9.8 — no code revert |
| **9.8** (new) | Session regenerate with destructive confirm |
| **9.6** | Add/adjust tests: session regenerate allowed; post-session block preserved |
| **9.5** | Docs: mention same-session regenerate + destructive warning (minor, during 9.5) |

### Artifact conflicts

| Artifact | Update needed |
|----------|---------------|
| **FR10** (`epics.md`) | Amend — session carve-out with explicit confirm |
| **epics.md** | Add Story 9.8; update planning summary order |
| **architecture-spine.md** AD-4 | Note session carve-out; still no Open/reload |
| **project-context.md** | Data-flow branch for session regenerate |
| **PRD** (`prd.md`) | Stale on Open/reload (Epic 9 superseded); optional FR10 note in deferred-work — **not blocking** |
| **UX** | No wireframes; destructive confirm reuses `confirm_yes_no` pattern |

### Technical impact

| Area | Impact |
|------|--------|
| `core/project_generator.py` | Optional bypass flag on generate (defense-in-depth when UI confirms) |
| `app/main_window.py` | Session target tracking; confirm before `_run_generation` |
| `core/app_state.py` | In-memory `last_generated_project_dir` ( **not** persisted — session ends on quit) |
| `core/project_writer.py` | **No change** — existing atomic replace + `.git` preservation |
| Tests | Extend `test_generate_guard.py`; session vs brownfield matrix |

**Out of scope:** Re-open Open/reload (9.1), brownfield merge, reading disk into `ProjectSpec`.

---

## 3. Recommended Approach

**Selected path:** **Option 1 — Direct Adjustment** (add Story 9.8 within Epic 9)

| Criterion | Assessment |
|-----------|------------|
| Effort | **Low–Medium** (~1 story) |
| Risk | **Low** — narrow carve-out; 9.2 guard remains default |
| Timeline | Minimal slip; insert before 9.6 |
| Rollback (Option 2) | **Not viable** — would restore destructive overwrite for all paths |
| MVP review (Option 3) | **Not needed** — MVP unchanged |

**Rationale:** PO-validated carve-out preserves Matrix-Control safety (post-session / unknown folder) while fixing the scaffold iteration loop. Reuses existing `ProjectWriter` overwrite semantics with explicit user consent — no new reload model.

---

## 4. Detailed Change Proposals

### 4.1 FR10 — `epics.md` (Functional Requirements section)

**OLD:**
```
FR10: Generate is **hard-blocked** when the target project directory exists and is non-empty (or contains Luthier project markers). No overwrite-with-confirmation in v1.0.
```

**NEW:**
```
FR10: Generate is **hard-blocked** when the target project directory exists and is non-empty, **except** a **session-only carve-out**: after a successful Generate in the same app session, the user may regenerate to the **same** `{destination}/{projectName}/` path via **explicit destructive confirmation** (replaces the entire tree except `.git`; Finder/IDE edits since last generate are lost). Brownfield protection applies on fresh app launch or when the target was not produced by Luthier in this session. No Open/reload workflow (Epic 9.1).
```

**Rationale:** Codifies PO decision; distinguishes session iteration from brownfield safety.

---

### 4.2 Story 9.8 — `epics.md` (new section after 9.3)

See appended Story 9.8 in `epics.md`.

---

### 4.3 Architecture spine — AD-4 rule

**OLD (excerpt):**
```
Generate is **hard-blocked** when the target project directory exists and is non-empty (`destination_blocks_generate()` …)
```

**NEW (excerpt):**
```
Generate is **hard-blocked** when the target project directory exists and is non-empty (`destination_blocks_generate()`), **unless** the UI session carve-out applies (same path as last successful Generate this session + user confirms destructive replace). Core `ProjectGenerator.generate()` accepts an explicit overwrite flag only after UI confirmation. Post-session or unknown folders remain hard-blocked.
```

---

### 4.4 `project-context.md` — data flow

Insert after guard check:

```
→ same path as in-memory lastGeneratedProjectDir?
    → confirm_yes_no (destructive) → generate(allow_overwrite=True)
    → else: hard block (9.2)
```

---

### 4.5 `sprint-status.yaml`

Add:

```yaml
9-8-session-regenerate-with-warning: backlog  # → ready-for-dev after create-story
```

Update Epic 9 comment implementation order.

---

### 4.6 Story 9.6 — test suite note (non-blocking for 9.8)

Add to **Add:** bullet list:

- Session regenerate: second generate same path in session succeeds after confirm; fresh session / different path still blocked

---

## 5. Implementation Handoff

### Scope classification: **Minor**

Single story; no epic replan. Developer agent implements 9.8 after 9.3 review lands (or in parallel if no conflict in `main_window.py`).

### Handoff

| Role | Action |
|------|--------|
| **PO** | Approved this proposal |
| **Create Story** | Generate `9-8-session-regenerate-with-warning.md` |
| **Dev agent** | Implement per story AC; run full `pytest` |
| **Code review** | Verify brownfield block unchanged; no Open/reload regression |

### Success criteria

1. First Generate → success; form tweak → second Generate same path → destructive confirm → success; tree reflects new `ProjectSpec`.
2. Quit app → reopen → Generate same non-empty path → **hard block** (9.2 message).
3. Generate into unrelated non-empty folder (never generated this session) → **hard block**.
4. `.git` preserved on session regenerate (existing `ProjectWriter` behaviour).
5. Full `pytest` green; 9.2 guard tests still pass for non-session paths.

---

## 6. Checklist Summary

| Section | Status |
|---------|--------|
| 1 — Trigger & context | [x] Done |
| 2 — Epic impact | [x] Done |
| 3 — Artifact conflicts | [x] Done |
| 4 — Path forward | [x] Done — Option 1 |
| 5 — Proposal components | [x] Done |
| 6 — Review & handoff | [x] Done — PO pre-approved |

---

**Correct Course workflow complete, Guillaume.**

Next: Story file `9-8-session-regenerate-with-warning.md` (create-story).
