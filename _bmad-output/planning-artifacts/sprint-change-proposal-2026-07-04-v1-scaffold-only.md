---
title: Sprint Change Proposal — v1.0 Scaffold-Only Pivot
status: approved
approved: 2026-07-04
approved_by: Guillaume DUPONT (PO)
created: 2026-07-04
author: Correct Course workflow (PO handoff)
handoff: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md
vision: docs/user/guide-juce-cmake-et-luthier.md  # EN: docs/user/juce-cmake-and-luthier-guide.md
target_version: 1.0.0
---

# Sprint Change Proposal — v1.0 Scaffold-Only Pivot

## 1. Issue Summary

### Problem statement

Luthier was built (Epics 1–8) around a **create → reopen → regenerate** lifecycle: Open Project… reloads `.luthier.json`, the user edits configuration, and Generate overwrites the project directory. PO validation (July 2026, documented in `docs/user/guide-juce-cmake-et-luthier.md`) concludes this model is **incompatible with real brownfield development** and with agentic IDE workflows (Cursor + CMake).

Key failures of the current model:

1. **Generate is destructive** — `ProjectWriter.write()` replaces the entire project tree; regenerating over Matrix-Control or any evolved CMake project would destroy user work.
2. **Reload/resync is Projucer-like** — maintaining round-trip fidelity, CMake merge zones, and sidecar migrations is disproportionate effort for the actual usage pattern (one-shot scaffold, then IDE/AI maintenance).
3. **Product positioning mismatch** — the public story should be: *Luthier generates the initial JUCE/CMake skeleton once; development continues in the IDE.*

### Context

- Epics 1–8 are **done** (`sprint-status.yaml`, last updated 2026-07-01).
- Repo is **private**, app **not yet publicly released**; version stays **1.0.0** (`app/version.py`).
- **No backward compatibility required** (PO §2.3): delete legacy reload paths; do not migrate pre-refactor sidecars or projects.
- **AUv3 excluded** from scope (PO decision); AU, VST3, Standalone only.

### Evidence

| Area | Current state | Desired v1.0.0 |
|------|---------------|------------------|
| Project tab actions | Create, **Open**, Generate | Create, Generate only |
| Generate on existing folder | Overwrite confirm dialog | **Hard block** if non-empty |
| `.luthier.json` | Read on Open + write on Generate | **Write-only** sidecar (reference metadata) |
| Plugin type | 3 exclusive presets, fixed flags | Presets + **independent characteristics** toggles |
| Accent colour | Project tab + sidecar + Preferences | **Preferences only** (Luthier UI theme) |
| Workspace/Artefacts OS rows | Left-margin indent only | **Tree connector lines** (§5.8.2) |
| Epic 2 | Done — Reliable Project Reload | **Superseded** by Epic 9 |

---

## 2. Impact Analysis

### Epic impact

| Epic | Impact |
|------|--------|
| **Epic 1** | Historical — generation pipeline remains; sidecar becomes write-only reference |
| **Epic 2** | **Superseded** — reload stories 2.1–2.2 obsolete; code and docs to be removed (Story 9.1) |
| **Epic 3** | Round-trip integration tests invalidated; Story 9.6 rewrites test suite |
| **Epic 5** | Open/Generate decoupling (5.4) remains valid; Open path removed entirely |
| **Epic 7** | Story 7.3 reload robustness partially obsolete; guard + characteristics replace reload edge cases |
| **Epic 8** | Workspace per-OS paths retained; UI enhanced with tree connectors (Story 9.7) |
| **Epic 9** | **New** — v1.0 Scaffold-Only Release (7 stories) |

### Story impact

| Story | Action |
|-------|--------|
| 9.1 | Remove Open Project, `project_reader`, reload wiring; scaffold-only positioning |
| 9.7 | Accent Preferences-only; remove `accentColor` from `ProjectSpec`; OS tree connectors |
| 9.2 | Block Generate on non-empty destination |
| 9.3 | Decoupled plugin characteristics + `ProjectSpec` fields |
| 9.4 | Template pipeline: audio I/O presets, MIDI counts, DESCRIPTION |
| 9.6 | Test suite regression pass (remove reload tests, add guard + characteristics) |
| 9.5 | Documentation EN/FR, README, guide cross-links, QA checklists |

**Recommended implementation order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.4 → 9.6 → 9.5`

### Artifact conflicts

| Artifact | Required change |
|----------|-----------------|
| `prd.md` | Remove reload use cases/FR4; update G3, FR8, F1 formats; add characteristics, generate guard, accent scope, no backward compatibility |
| `architecture-spine.md` | AD-3 write-only sidecar; remove `project_reader` from data flow; AD-4 generate guard; Epic 2 superseded note; accent in `preferences.json` only |
| `epics.md` | Epic 2 superseded note; Epic 9 + stories 9.1–9.7; FR inventory updates |
| `sprint-status.yaml` | Epic 9 backlog entries |
| `project-context.md` | Remove `_on_open` / reload path (Story 9.1) |
| User manuals, README, QA checklists | Story 9.5 |

### Technical impact (planning only — not implemented in this proposal)

- **Delete:** `core/project_reader.py`, `tests/unit/test_project_reader.py`
- **Modify:** `app/main_window.py`, `app/pages/project.py`, `app/pages/plugin_type.py`, `core/project_spec.py`, `core/plugin_settings.py`, `core/render_context.py`, templates
- **Add:** `app/widgets/os_path_tree_group.py` (or equivalent), generate guard logic, characteristics UI
- **No migration code** — PO §2.3 explicitly forbids backward-compatibility shims

---

## 3. Recommended Approach

### Chosen path: **Direct Adjustment + MVP Review (scope reduction)**

This is not a rollback of Epics 1–8 deliverables. It is a **product pivot** implemented as Epic 9 on top of the existing codebase:

- **Remove** reload/Open paths and associated tests/docs
- **Add** generate guard, enriched plugin characteristics, UI polish
- **Reposition** v1.0.0 as first public release with scaffold-only semantics

### Rationale

| Alternative | Why rejected |
|-------------|--------------|
| Keep Open + add brownfield merge | Effort disproportionate; conflicts with agentic CMake workflow |
| Bump to 2.0.0 | PO decision: stay at 1.0.0; update `REVISION_DATE` only |
| Backward compatibility / sidecar migration | PO §2.3: no legacy support; repo private, test projects disposable |

### Effort estimate

| Story | Estimate |
|-------|----------|
| 9.1 | 1 dev session |
| 9.7 | 1–2 dev sessions (widget + accent simplification) |
| 9.2 | 0.5 dev session |
| 9.3 | 1–2 dev sessions |
| 9.4 | 1–2 dev sessions |
| 9.6 | 1 dev session |
| 9.5 | 1–2 dev sessions |
| **Total** | ~7–10 dev sessions |

### Risk assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Tests coupled to reload/round-trip | High | Story 9.6 dedicated; grep `read_project`, `Open Project` |
| UI overload (many toggles) | Medium | Collapsible characteristics section |
| `PluginProcessor.cpp` variant complexity | Medium | Max 4 `audio_io_preset` branches |
| Docs EN/FR divergence | Medium | Parallel structure; Story 9.5 last |
| OS tree connector HiDPI alignment | Low | Shared widget + `path_specs.py` constants |

### Timeline impact

Epic 9 blocks **public v1.0.0 release**. Epics 1–8 remain historically done; no reopening of closed epics except documentation supersession notes.

---

## 4. Detailed Change Proposals

### 4.1 PRD patches (`prd-Luthier-2026-06-22/prd.md`)

#### §1.2 Problem — OLD → NEW

**OLD:**
> …above all the ability to **reload and regenerate** an existing project after changing its configuration.

**NEW:**
> …a **one-shot scaffold generator** that produces a complete, portable CMake JUCE project. After generation, the developer maintains the project in their IDE (manually or via agentic tooling) — Luthier does **not** reload or regenerate existing projects.

#### §1.3 Solution — OLD → NEW

**OLD:**
> …allows developers to revisit and update project configuration at any point in the development lifecycle.

**NEW:**
> …generates a complete, portable CMake configuration **once** for a new project folder. Luthier writes a `.luthier.json` sidecar as a **metadata snapshot for humans and AI** — the application never reads it back.

#### §2.1 Goals — G3 OLD → NEW

**OLD (G3):**
> Support a complete project lifecycle: initial generation → development → reload → configuration change → regeneration.

**NEW (G3):**
> Support a **scaffold-only lifecycle**: initial generation → development in the IDE. Luthier does not reopen, reload, or regenerate existing projects.

#### §4 Primary Use Cases — UC2 and UC3

**UC2 — Reload and Regenerate:** **REMOVED**

**UC3 — Multi-OS Workflow:** **REVISED** — remove step 4 (open Luthier, load, regenerate). Replace with: configure/build via CMake presets on each OS; project changes live in Git and CMake, not in Luthier.

#### §5 F1 Formats row — OLD → NEW

**OLD:** `VST3, AU, AUv3, Standalone`

**NEW:** `VST3, AU, Standalone` (AUv3 explicitly out of scope)

#### §5 F1 — NEW rows (Plugin Characteristics)

Add after Plugin Type:

| Field | Type | Notes |
|-------|------|-------|
| Plugin is a Synth | Checkbox | Maps to `IS_SYNTH`; preset default + user override |
| Plugin MIDI Input | Checkbox | `NEEDS_MIDI_INPUT` |
| Plugin MIDI Output | Checkbox | `NEEDS_MIDI_OUTPUT` |
| MIDI Effect Plugin | Checkbox | `IS_MIDI_EFFECT`; incompatible with Synth |
| Editor Requires Keyboard Focus | Checkbox | `EDITOR_WANTS_KEYBOARD_FOCUS` |
| Audio I/O | Combo | `stereo` \| `mono` \| `synth_no_input` \| `midi_effect` |
| VST MIDI Inputs | Combo 1–16 | When MIDI Input enabled; default 16 |
| VST MIDI Outputs | Combo 1–16 | When MIDI Output enabled; default 16 |
| Plugin Description | Text | Maps to `DESCRIPTION` in `juce_add_plugin` |

**Validation:** `IS_SYNTH` + `IS_MIDI_EFFECT` → inline error. Preset radio change resets toggles to preset defaults (with dirty guard if form dirty).

#### §5 F4 — Round-Trip — **REMOVED**

Replace with:

#### §5 F4 — Generate Guard (NEW)

- Generate is **refused** if `{destination}/{projectName}/` exists and is **non-empty**, or contains `.luthier.json` or Luthier-signed `CMakeLists.txt`.
- No "Continue anyway" dialog in v1.0.
- User message: *"This folder already exists and is not empty. Luthier only creates new projects. Choose an empty folder or a different project name."*
- Allowed: parent destination exists but project subfolder does not yet exist.

#### §5 F7 — accent colour scope

**OLD:** (implicit Project tab accent + sidecar)

**NEW:** `accentColor` persists in `preferences.json` only (Preferences tab). Not stored in `ProjectSpec` or `.luthier.json`. Luthier theme uses single source: `prefs.accent_color` on all tabs.

#### §5 F8 — Action bar — OLD → NEW

**OLD (Project):** Create New Project, Open Project…, Generate Project

**NEW (Project):** Create New Project, Generate Project

Remove all references to Open Project…, `_load_project`, open dialog starting directories.

#### §5 F8 — NEW: OS tree connectors

Workspace and Artefacts sections display tree connector lines for Windows/macOS/Linux path groups per handoff §5.8.2. Decorative only; keyboard order unchanged.

#### §6 NF2 / NF3 — reload references

- Remove "project load, generation, reload" from smoke tests.
- Remove "missing field during reload must not corrupt" — replace with generate-guard and characteristics validation.

#### §8 Success Criteria — OLD → NEW

| OLD | NEW |
|-----|-----|
| Round-trip fidelity | **Scaffold fidelity** — Generate produces valid CMake project; `.luthier.json` written but not read by app |
| (implicit reload) | Generate blocked on non-empty destination |
| | Instrument + MIDI Output generates compilable project (Matrix-Control case) |

#### §9 Out of Scope — ADD

- Reopen / reload / regenerate existing projects
- Brownfield CMake merge or protected zones
- Backward compatibility with pre-refactor `.luthier.json` or Luthier projects
- AUv3, AAX, LV2, ARA, VST2, GUI App, free-text channel configs

#### §NEW — Backward Compatibility Policy (PO §2.3)

> **No backward compatibility required.** Remove dead code and upward-compatibility paths; do not migrate projects or `.luthier.json` sidecars created before this refactor.

---

### 4.2 Architecture spine patches (`architecture-spine.md`)

#### AD-3 — OLD → NEW

**OLD:** Sidecar for round-trip; `project_reader` sole deserialiser; CMake regex fallback.

**NEW (AD-3 — Write-only sidecar):**

- **Binds:** `ProjectWriter` only
- **Rule:** `ProjectWriter` writes `.luthier.json` (full `ProjectSpec` as JSON, **without `accentColor`**) at generation time. **No module reads `.luthier.json` at runtime.** The sidecar is reference metadata for humans and AI tools — not application input.
- **Removes:** `core/project_reader.py`, CMake regex fallback, round-trip reload invariant.
- **Supersedes:** Epic 2 stories 2.1, 2.2, Epic 8.2 sidecar-on-open requirement.

#### AD-4 — revision

**OLD:** Overwrite confirmed via `MainWindow._confirm_overwrite()`.

**NEW:** Generate refused if target project directory exists and is non-empty (or contains Luthier project markers). Atomic write semantics unchanged for allowed creates. `_confirm_overwrite` removed or restricted to parent-exists / child-not-yet-created cases only.

#### AD-2 — accent field

**Remove** `accent_color` from `ProjectSpec`. Accent colour lives in `preferences.json` (`accentColor`) only — Preferences tab auto-save.

#### Structural seed — OLD → NEW

**Remove from tree:**
```
project_reader.py          # .luthier.json first, CMake regex fallback
```

**Add to tree:**
```
app/widgets/os_path_tree_group.py   # shared tree connectors for Workspace/Artefacts
```

#### Data flow diagram — revision

**Remove:** `Open Project…` → `project_reader.read_project()` → `ProjectPage` populate path.

**Retain:**
```
ProjectPage.spec() → ProjectGenerator.generate(spec) → ProjectWriter.write() → [CMake + .luthier.json]
Preferences.accent_color → theme (all tabs)
```

#### Epic 2 superseded note (add to spine header or Deferred section)

> **Epic 2 (Reliable Project Reload)** — superseded 2026-07-04 by Epic 9 scaffold-only pivot. Reload code and documentation removed; no restoration planned unless a future Correct Course reopens brownfield merge scope.

---

### 4.3 Epics.md updates

See appended Epic 9 section in `epics.md` (this proposal's companion deliverable).

**FR inventory changes:**

| ID | Change |
|----|--------|
| FR4 | **Removed** — no project reload |
| FR8 | Project actions: Create, Generate only (no Open) |
| FR1 | Add plugin characteristics fields; remove AUv3 from formats |
| FR10 (new) | Generate hard-block on non-empty destination |
| FR11 (new) | Plugin characteristics: presets + independent toggles, validation |
| FR12 (new) | Accent colour Preferences-only; OS tree connectors in Workspace/Artefacts |

**Epic 2 header:** add superseded note referencing Epic 9.

---

### 4.4 sprint-status.yaml

Add Epic 9 and stories 9.1–9.7 as `backlog`. See updated file.

---

## 5. Implementation Handoff

### Scope classification: **Major**

Fundamental product replan (pivot) requiring PO-validated Epic 9 execution. Not a minor patch.

### Handoff recipients

| Role | Responsibility |
|------|----------------|
| **PO (Guillaume)** | Approve this proposal; manual smoke test before public release |
| **Create Story workflow** | Generate story files 9.1–9.7 from epics.md AC |
| **Dev agent** | Implement in order 9.1 → 9.7 → 9.2 → 9.3 → 9.4 → 9.6 → 9.5 |
| **Code review** | Per story; grep for `read_project`, `Open Project`, `accentColor` in sidecar |

### Success criteria (release v1.0.0)

1. No UI/code path for Open Project
2. Generate impossible on non-empty folder
3. Instrument + MIDI Output generates compilable project
4. Accent colour Preferences-only; absent from Project tab and `.luthier.json`
5. OS tree connectors visible in Workspace & Artefacts (Project + Preferences)
6. EN/FR manuals + README aligned; guide referenced
7. `pytest` green in CI
8. PO smoke: Create → Generate → open in Cursor → build Standalone
9. About: Version **1.0.0** unchanged; **Revision date** updated
10. Git tag `v1.0.0` **only on explicit PO request**

### Explicit non-goals (Epic 9)

- AUv3, AAX, LV2, ARA, GUI App, `.jucer` import
- PyInstaller rebuild (unless regression)
- Migration of pre-refactor projects or sidecars
- Reopen / resync / brownfield CMake merge

---

## 6. Checklist Status (Correct Course analysis)

| Section | Status | Notes |
|---------|--------|-------|
| Change trigger identified | [x] Done | PO handoff 2026-07-04 |
| PRD impact assessed | [x] Done | §4.1 patches |
| Architecture impact assessed | [x] Done | §4.2 patches |
| Epic/story impact assessed | [x] Done | Epic 9 defined |
| UX impact assessed | [x] Done | Accent + tree connectors §5.8 |
| Test impact assessed | [x] Done | Story 9.6 |
| Docs impact assessed | [x] Done | Story 9.5 |
| Backward compatibility policy | [x] Done | None — PO §2.3 |
| Versioning decision | [x] Done | Stay 1.0.0; REVISION_DATE only |
| Implementation order | [x] Done | 9.1→9.7→9.2→9.3→9.4→9.6→9.5 |

---

*Proposal approved by PO on 2026-07-04. Ready for Create Story → Dev → Review cycle (Epic 9).*
