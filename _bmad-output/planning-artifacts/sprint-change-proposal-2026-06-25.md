# Sprint Change Proposal — Epic 5: Project & Preferences Workflows

**Project:** Luthier  
**Date:** 2026-06-25  
**Author:** Correct Course workflow (Batch mode)  
**Change signal:** `correct-course-handoff-epic-5-workflows.md`  
**Product vision reference:** `Docs/USER-MANUAL.md` (PO-validated)  
**Scope classification:** **Moderate** — new epic, architecture invariant revisions, forward adjustment (no rollback)

---

## 1. Issue Summary

### 1.1 Problem Statement

Luthier currently **conflates the active project with global user settings**. After Epics 1–3, the implementation:

- Calls `prefs.update(spec)` + `prefs.save()` on **Open** and **Generate** success (`MainWindow`), writing project state into `preferences.json` (AD-5).
- Stores `juce_dir` **only** in Preferences and passes it separately to `build_context` — it is **not** on `ProjectSpec` or in `.luthier.json` (AD-7).
- Uses a **partial** `preferences.json` schema (identity + artefacts only; no plugin type, formats, or compilation defaults).
- Has UI buttons added ad hoc (Create New Project, Load/Save Preferences) without formal stories.

The **target product vision** (validated in `Docs/USER-MANUAL.md`) requires three strictly separated domains:

| Domain | Tab | Persistence | Open/Generate effect |
|--------|-----|-------------|----------------------|
| Active project | Project | Form + `.luthier.json` after Generate | Reads/writes project only |
| Global defaults | Preferences | `preferences.json` | **Never** modified by Open/Generate |
| Global templates | Templates | App config overrides | Read at Generate only |

### 1.2 Trigger Type

- **New product requirement** emerged after Epics 1–3 closure (not an isolated implementation bug).
- **Structural UX inconsistency** between coded behaviour and validated product vision.

### 1.3 Evidence

| Source | Finding |
|--------|---------|
| `Docs/USER-MANUAL.md` §4, §5, §6, §9 | Single source of defaults (`preferences.json`); Open/Generate must not write prefs; `juceDir` per project |
| `app/main_window.py` | `prefs.update` + `save` on open/generate (lines ~213–218, 237–242) |
| `core/project_spec.py` | No `juce_dir` field |
| `core/preferences.py` | Partial `_DEFAULTS`; no plugin type/formats/compilation |
| Handoff §3 | PO decision: Epic 5 before Epic 4 |

**No legacy user migration required** — app never shipped; sidecar round-trip can adopt `juceDir` without backward-compat burden.

---

## 2. Impact Analysis

### 2.1 Checklist Summary

| Section | Status | Notes |
|---------|--------|-------|
| 1 — Trigger & context | [x] Done | Handoff + USER-MANUAL provide full trigger; no re-interview needed |
| 2 — Epic impact | [x] Done | New Epic 5; Epic 4 deferred; Epics 1–3 remain **done** (superseded docs only) |
| 3 — Artifact conflicts | [x] Done | PRD F7/F8, AD-5, AD-7, epics.md, sprint-status |
| 4 — Path forward | [x] Done | Direct Adjustment + new epic (Option 1); Rollback rejected |
| 5 — Proposal components | [x] Done | This document |
| 6 — Final review | [x] Done | Approved by PO 2026-06-25 |

### 2.2 Epic Impact

| Epic | Status | Impact |
|------|--------|--------|
| Epic 1 — Core Architecture | **done** | Stories 1.3, 1.6 AC reference AD-5/AD-7 — **documentation supersession note** only; no code rollback |
| Epic 2 — Reliable Reload | **done** | Stories 2.1, 2.2 unaffected functionally; round-trip gains `juceDir` via Epic 5.3 |
| Epic 3 — Test Suite | **done** | Tests using `juce_dir=""` param updated in Epic 5.3 |
| **Epic 5 — Project & Preferences Workflows** | **new — backlog** | Addresses full vision gap |
| Epic 4 — Cross-Platform Distribution | **backlog — deferred** | Remains after Epic 5 per PO priority |

### 2.3 Story Impact (Historical — Superseded by Epic 5)

| Story | Superseded aspect | Epic 5 resolution |
|-------|-------------------|-------------------|
| 1.3 | `prefs.update` + `save` on generate/open | Story 5.4 removes these calls |
| 1.6 | `juce_dir` Preferences-only, separate arg | Story 5.3 moves to `ProjectSpec` |
| 2.1, 2.2 | Implicit prefs sync on open | Story 5.4 decouples |
| 3.4 | `generator.generate(spec, juce_dir="")` | Story 5.3 updates signature |

### 2.4 Artifact Conflicts

| Artifact | Conflict | Resolution |
|----------|----------|------------|
| PRD F7 | Incomplete prefs scope; sync on open implied | Expand F7 (§4.1) |
| PRD F8 | Missing Create New Project, Import/Export, Choose…, per-tab action bar | Expand F8 (§4.2) |
| PRD F5 | States artefact paths "stored in Preferences" | Minor clarification: defaults in Preferences, values on Project at generate time (§4.3) |
| ARCHITECTURE-SPINE AD-5 | Save-on-open/generate | Replace (§4.4) |
| ARCHITECTURE-SPINE AD-7 | juce_dir not on ProjectSpec | Replace (§4.5) |
| ARCHITECTURE-SPINE AD-2 | Silent on seed vs project source | Clarify (§4.6) |
| epics.md | No Epic 5; FR7/FR8 mapped to Epic 1 | Add Epic 5; update FR map (§4.7) |
| sprint-status.yaml | No Epic 5 entries | Proposed update (§5) |
| UX | No formal UX doc | USER-MANUAL is authoritative reference |
| project-context.md | Documents AD-5/AD-7 as current | Update after Epic 5.4/5.3 implementation |

### 2.5 Technical Impact

| Area | Change |
|------|--------|
| `core/project_spec.py` | Add `juce_dir` field (`juceDir` in JSON) |
| `core/render_context.py` | `build_context(spec)` reads `spec.juce_dir`; deprecate `juce_dir=` param |
| `core/project_generator.py` | Remove `juce_dir` parameter |
| `core/preferences.py` | Extended schema; factory file creation; optional `lastUsedParentDir`; narrow/remove `update(spec)` |
| `app/main_window.py` | Decouple open/generate from prefs; Import/Export; saved indicator; Create New Project |
| `app/pages/*` | Preferences auto-save, Choose buttons, Project layout, seed from prefs |
| Tests | Round-trip includes `juceDir`; remove empty `juce_dir=""` workarounds |

**Risk:** Medium — round-trip regression, prefs/profile workflow edge cases.  
**Effort:** Medium — 5 stories, mostly app layer + one core model change.

---

## 3. Recommended Approach

### 3.1 Selected Path: **Direct Adjustment (Option 1)**

Add **Epic 5** with five stories implementing the validated USER-MANUAL vision. Revise architecture invariants AD-5 and AD-7 forward — **no rollback** of Epics 1–3 code.

### 3.2 Rejected Alternatives

| Option | Verdict | Rationale |
|--------|---------|-----------|
| Rollback Epics 1–3 | **Not viable** | Working generation/reload/test foundation; changes are additive/corrective |
| MVP scope reduction | **Not viable** | Vision is core product coherence, not optional polish |
| Fold into Epic 4 | **Rejected** | PO priority: UX workflows before PyInstaller distribution |

### 3.3 Priority Resequencing

**Epic 5 before Epic 4.** Distribution (PyInstaller) benefits from a stable, coherent product UX baseline.

### 3.4 Implementation Order (Recommended)

```
5.1 → 5.3 → 5.2 → 5.4 → 5.5
```

| Order | Rationale |
|-------|-----------|
| 5.1 first | Extended prefs schema + factory file is foundation for all seeding |
| 5.3 before 5.4 | Generate must read `spec.juce_dir` before decoupling prefs sync |
| 5.2 after 5.3 | Project UI can wire JUCE field knowing spec carries it |
| 5.4 after 5.2/5.3 | Remove prefs sync once project form is complete |
| 5.5 last | Create New Project depends on prefs seed + dirty tracking infrastructure |

### 3.5 MVP Impact

**MVP scope unchanged** — Epic 5 closes a gap between delivered code and stated product goals (F7/F8). FR9 (distribution) remains Epic 4, deferred until Epic 5 completes.

---

## 4. Detailed Change Proposals

### 4.1 PRD — F7 Preferences

**File:** `_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md`  
**Section:** §5 F7 — Preferences

**OLD:**
```markdown
### F7 — Preferences

- Default values for all company identity fields.
- Default artefacts configuration (paths + mode).
- Preference values seed all fields when creating a new project.
```

**NEW:**
```markdown
### F7 — Preferences

Preferences hold **global reusable defaults** for the active machine. They are persisted in `preferences.json` under the OS application config directory.

**Scope — fields stored in Preferences (not project identity):**
- Company identity defaults: manufacturer, manufacturer code, plugin code, copyright, website, e-mail
- **Destination folder** — parent directory for new project folders (not the project path itself)
- **JUCE directory** — default SDK path used to **seed** new projects only
- Plugin type, formats, C++ standard, preprocessor definitions, header search paths
- Artefacts configuration: copy-to-system flag, copy-to-central flag, per-OS artefact paths (Windows, macOS, Linux)

**Factory defaults (first launch):** On the very first application run, Luthier creates `preferences.json` from hardcoded factory values in code (e.g. manufacturer "My Company", destination folder = Desktop via OS API, plugin type = Instrument, formats = AU + VST3 + Standalone, C++17, copy-to-central = off). After this one-time creation, **code factory defaults are never used again** — all Project seeding reads exclusively from `preferences.json`.

**Persistence rules:**
- Valid field edits in the Preferences tab are **auto-saved** immediately to `preferences.json`.
- **Import Preferences…** replaces the entire profile and writes `preferences.json`.
- **Export Preferences…** writes a copy to a user-chosen file; it does **not** modify `preferences.json`.
- **Open Project…** and **Generate Project** must **never** read from or write to `preferences.json`.

**Seeding rule:** Preferences values pre-fill matching Project fields at app startup, after **Create New Project**, and after **Import Preferences…** (Project tab is not modified by import — new values apply on next Create New Project or cold start).

**Design note — separation from project:** Changing Preferences does not push changes to an already-open project. Templates overrides remain global and are not included in Import/Export profiles.
```

**Rationale:** Aligns F7 with USER-MANUAL §4, §6, §9; defines complete profile schema and strict decoupling from Open/Generate.

---

### 4.2 PRD — F8 User Interface

**File:** `_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md`  
**Section:** §5 F8 — User Interface

**OLD:**
```markdown
### F8 — User Interface

- **Tab bar**: horizontal tab bar at the top of the window for navigation between the three views (Project, Preferences, Templates, About).
- **Project view**: scrollable form with sections (Project Info, Plugin Type, Formats, Compilation, Artefacts).
- **Preferences view**: same sections as a project, scoped to default values.
- **Templates view**: file selector combo, editor, Save Override / Load File / Reset buttons.
- **Bottom bar**: "Open Project…" button (loads an existing project) + "Generate Project" button (generates or regenerates).
- **Theme**: dark, with a configurable accent color (`kAccentColor` constant, finalized during UI polish phase).
```

**NEW:**
```markdown
### F8 — User Interface

- **Tab bar**: horizontal tab bar (Project, Preferences, Templates, About). A **transient saved indicator** (orange accent label) appears briefly in the tab bar after Preferences auto-save confirms persistence.

- **Per-tab action bar** (bottom of window, changes with active tab):
  - **Project:** Create New Project, Open Project…, Generate Project
  - **Preferences:** Import Preferences…, Export Preferences… (replaces Load/Save)
  - **Templates:** Load from file…, Reset to default, Save override
  - **About:** no actions

- **Project view**: scrollable form with sections (Project Info, Plugin Type, Formats, Compilation, Artefacts).
  - **Project Info order:** identity fields → Bundle ID → **Destination folder** * → **JUCE directory**
  - **Destination folder** and **JUCE directory** use layout: **label → Choose… → text field** (field remains editable). Choose… opens the native OS folder picker.
  - **Create New Project:** resets plugin identity (empty names, version 1.0.0); re-seeds all other fields from `preferences.json`; prompts for confirmation if the form is dirty; does **not** write `preferences.json`.
  - **Open Project…** updates Project tab only; Preferences and Templates unchanged. After open, Destination folder = parent of the opened project directory.
  - **Generate Project** reads Project tab only; after success, remembers last-used parent folder for Choose… / Open starting directory (Desktop fallback if invalid).

- **Preferences view**: same field families as Project (excluding project identity), scoped to global defaults.
  - Labels match Project (**Destination folder**, not "Default destination").
  - Choose… on Destination folder and JUCE directory only — **not** on Windows/macOS/Linux artefact path fields (cross-OS target paths).
  - Artefact section labels: **Windows**, **macOS**, **Linux**.
  - Auto-save on valid edit (no manual Save button).

- **Templates view**: file selector combo, editor, Load from file… / Reset to default / Save override buttons.

- **Theme**: dark, orange accent (`kAccentColor`).

**Design note — Destination folder as form field (not Generate modal):** Keeping destination visible and editable (rather than a mandatory folder dialog on every Generate) supports one-click regeneration after Open and clean Import/Export profiles per client. Generate may still prompt Choose… when destination is empty or invalid.
```

**Rationale:** Captures full validated UX from USER-MANUAL §3, §5, §6; formalizes per-tab actions and Choose… patterns.

---

### 4.3 PRD — F5 Clarification (Optional but Recommended)

**Section:** §5 F5 — Artefacts System

**OLD (partial):**
```markdown
- Paths are stored in Preferences and injected into `CMakeUserPresets.json`.
```

**NEW (replace last bullet in central artefacts mode):**
```markdown
- Default artefact paths and copy flags are stored in **Preferences** and seed new projects.
- At generation time, artefact values on the **Project** tab (which may differ from Preferences after Open or manual edit) are written to `CMakeUserPresets.json`.
```

**Rationale:** Resolves F5/F7 overlap; Project tab owns values at generate time per USER-MANUAL §5.5.

---

### 4.4 Architecture — AD-5 (REPLACE)

**File:** `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md`

**OLD:**
```markdown
### AD-5 — Preferences save-on-update; save is app-layer only

- **Binds:** `MainWindow`, `Preferences`
- **Prevents:** in-memory preference state diverging from disk; `core/` acquiring a hidden app-layer side-effect
- **Rule:** every call to `prefs.update(spec)` at a user-facing commit point (generate success, open success) is immediately followed by `prefs.save()`. Both calls are made by `MainWindow` only — `core/` never calls `prefs.save()` directly (would violate AD-8 and introduce a hidden side-effect in generation logic). [ADOPTED]
```

**NEW:**
```markdown
### AD-5 — Preferences persistence is Preferences-driven only; save is app-layer only

- **Binds:** `MainWindow`, `PreferencesPage`, `Preferences`
- **Prevents:** global defaults being overwritten by project-specific state; `core/` acquiring hidden app-layer side-effects
- **Rule:** `preferences.json` is written **only** by: (1) first-launch factory file creation, (2) Preferences tab auto-save on valid edit, (3) successful Import Preferences. `MainWindow` calls `prefs.save()` only after auto-save or import — **never** after Open Project or Generate Project. Open and Generate must not call `Preferences.update(ProjectSpec)`. `core/` never calls `prefs.save()` directly. [ADOPTED — revised 2026-06-25, supersedes Epic 1 Story 1.3 AD-5 AC]
```

**Rationale:** Separates global profile from project lifecycle per validated product vision.

---

### 4.5 Architecture — AD-7 (REPLACE)

**OLD:**
```markdown
### AD-7 — `juce_dir` is Preferences-only

- **Binds:** `ProjectSpec`, `Preferences`, `render_context`
- **Prevents:** per-project JUCE path drift and unnecessary sidecar bloat
- **Rule:** `juce_dir` is never a field on `ProjectSpec`. It describes the dev environment, not the plugin. It is read from `Preferences` at generation time and passed separately to `render_context`; it does not participate in the round-trip. [ADOPTED]
```

**NEW:**
```markdown
### AD-7 — `juce_dir` is a ProjectSpec field; Preferences holds the default seed only

- **Binds:** `ProjectSpec`, `Preferences`, `render_context`, `ProjectWriter`, `project_reader`
- **Prevents:** per-project JUCE version pinning being lost on reload; environment default conflated with project configuration
- **Rule:** `ProjectSpec` includes `juce_dir` (JSON key `juceDir`). It is written to `.luthier.json` and participates in round-trip. `render_context.build_context(spec)` reads `spec.juce_dir` — no separate `juce_dir=` parameter. `Preferences.juce_dir` is the **default seed** only: copied into new Project forms at startup and Create New Project, not read at Generate time. [ADOPTED — revised 2026-06-25, supersedes Epic 1 Story 1.6 AD-7 AC]
```

**Rationale:** Enables per-project JUCE versions (USER-MANUAL §5.1, §8.2) with full sidecar round-trip.

---

### 4.6 Architecture — AD-2 (CLARIFY)

**OLD (Rule only):**
```markdown
- **Rule:** `ProjectSpec` carries both identity fields (plugin name, type, formats…) and artefact config fields (copy flags, per-OS paths). `ProjectPage.spec()` replaces `values()` + `config()`. [ADOPTED]
```

**NEW (append to Rule):**
```markdown
- **Rule:** `ProjectSpec` carries both identity fields (plugin name, type, formats…) and artefact config fields (copy flags, per-OS paths), **including `juce_dir` and destination folder**. The same field set appears on Project and Preferences tabs, but **sources differ**: an opened or generated project populates Project from disk/sidecar; a new project seeds from `preferences.json`. `ProjectPage.spec()` replaces `values()` + `config()`. [ADOPTED]
```

**Rationale:** Documents dual-source seeding without splitting the data model.

---

### 4.7 epics.md — Additional Requirements & FR Map

**Section:** Additional Requirements (AD-5, AD-7 lines)

**OLD:**
```markdown
- **AD-5 — Preferences save-on-update**: Every `prefs.update(spec)` at a user-facing commit point is immediately followed by `prefs.save()`. Both calls are made only in `MainWindow`.
...
- **AD-7 — juce_dir Preferences-only**: `juce_dir` is never a field on `ProjectSpec`. Read from `Preferences` at generation time, passed separately to `render_context`.
```

**NEW:**
```markdown
- **AD-5 — Preferences persistence is Preferences-driven only**: `preferences.json` is written only by first-launch factory creation, Preferences auto-save, and Import Preferences. Open/Generate never call `prefs.update(spec)` or `prefs.save()`. Save is app-layer only (`MainWindow` / `PreferencesPage`).
...
- **AD-7 — juce_dir on ProjectSpec; Preferences seed only**: `juce_dir` is a field on `ProjectSpec` (JSON `juceDir`), included in sidecar round-trip. `build_context(spec)` reads `spec.juce_dir`. Preferences holds the default seed for new projects.
```

**FR Coverage Map — add/update lines:**

**OLD:**
```markdown
FR7: Epic 1 — Preferences avec juce_dir exposé dans l'UI
FR8: Epic 1 — Ajustements UI mineurs (spec() contract)
```

**NEW:**
```markdown
FR7: Epic 1 (baseline) + Epic 5 (full profile, Import/Export, auto-save, decouple from Open/Generate)
FR8: Epic 1 (baseline tabs/form) + Epic 5 (Create New Project, Choose…, per-tab actions, layout, saved indicator)
```

**Supersession note to add after Epic List header:**

```markdown
> **Epic 5 supersession (2026-06-25):** Stories 1.3, 1.6, 2.1, 2.2, and 3.4 remain **done** historically. Epic 5 amends AD-5/AD-7 behaviour and extends F7/F8 — not a rollback of Epics 1–3.
```

---

### 4.8 epics.md — New Epic 5 (FULL INSERT)

Insert **before** Epic 4 in the Epic List and add full story block:

```markdown
### Epic 5: Project & Preferences Workflows
A JUCE developer can manage global defaults and the active project as separate concerns: full Preferences profile with Import/Export, per-project JUCE path with round-trip, Choose… folder pickers, and Create New Project — aligned with the validated user manual.
**FRs covered:** F7 (extended), F8 (extended)
**Priority:** Before Epic 4 (PO decision 2026-06-24)
```

#### Story 5.1: Preferences Model & Profile Workflow

As a JUCE developer,
I want a complete Preferences profile with auto-save and Import/Export,
So that my global defaults (identity, paths, plugin type, formats, compilation, artefacts) persist independently of any open project.

**Acceptance Criteria:**

**Given** first application launch (no existing `preferences.json`),
**When** Luthier starts,
**Then** `preferences.json` is created with factory defaults (Desktop destination, Instrument/Synth, AU+VST3+Standalone, C++17, copy-to-central off, empty artefact paths, empty JUCE dir with OS placeholder in UI).

**Given** the extended schema in `core/preferences.py`,
**When** `preferences.json` is read/written,
**Then** it includes: identity fields, destination folder, juceDir, pluginType, pluginFormats, cxxStandard, preprocessorDefinitions, headerSearchPaths, copy flags, and per-OS artefact paths.

**Given** the Preferences tab,
**When** I view it,
**Then** sections include Plugin Type, Formats, Compilation; labels read **Destination folder**, artefact paths labeled **Windows**, **macOS**, **Linux**; Choose… buttons appear on Destination folder and JUCE directory only.

**Given** I edit any valid Preferences field,
**When** validation passes,
**Then** `preferences.json` is auto-saved and a transient orange saved indicator appears in the tab bar.

**Given** I click **Import Preferences…** and select a valid JSON file,
**When** import succeeds,
**Then** the entire profile is replaced, `preferences.json` is written, and Preferences UI refreshes; the Project tab is **not** modified.

**Given** I click **Export Preferences…**,
**When** I choose a destination file,
**Then** the current profile is written to that file and `preferences.json` is unchanged.

**Given** import fails (invalid JSON or validation error),
**When** the error is shown,
**Then** the previous profile and `preferences.json` remain unchanged.

---

#### Story 5.2: Project UI, Choose Buttons & Layout

As a JUCE developer,
I want Choose… buttons and consistent labels on the Project tab,
So that I can pick local folders easily while keeping cross-OS artefact paths as typed text.

**Acceptance Criteria:**

**Given** the Project Info section,
**When** I view it,
**Then** field order is: identity fields → Bundle ID → **Destination folder** * → **JUCE directory**; both path fields use **label → Choose… → text field** layout.

**Given** I click Choose… on Destination folder or JUCE directory,
**When** I select a folder in the native dialog,
**Then** the text field is populated with an OS-valid path and remains editable.

**Given** artefact path fields on Project (when copy-to-central is enabled),
**When** I view them,
**Then** labels are **Windows**, **macOS**, **Linux** with **no** Choose… buttons.

**Given** app startup or successful Preferences import,
**When** Project is in "new project" state,
**Then** all seedable fields (except empty identity) reflect current `preferences.json` values including plugin type, formats, and compilation.

---

#### Story 5.3: juceDir on ProjectSpec & Generation Pipeline

As a JUCE developer,
I want the JUCE directory stored on my project and round-tripped in `.luthier.json`,
So that each project can target a different JUCE version and reload faithfully.

**Acceptance Criteria:**

**Given** `ProjectSpec`,
**When** serialized via `to_dict()` / `.luthier.json`,
**Then** `juceDir` is included and restored by `from_dict()`.

**Given** a non-empty `spec.juce_dir`,
**When** `ProjectGenerator.generate(spec)` runs,
**Then** `render_context.build_context(spec)` emits the `set(JUCE_DIR "...")` line from `spec.juce_dir` — no separate `juce_dir=` argument.

**Given** empty `spec.juce_dir`,
**When** generation runs,
**Then** no preference-injected JUCE line appears (CMake discovery applies).

**Given** generate → open → regenerate without changes,
**When** `.luthier.json` is compared,
**Then** `juceDir` round-trips with empty diff on all sidecar fields.

**Given** unit and integration tests,
**When** pytest runs,
**Then** tests use `generate(spec)` without `juce_dir=` parameter; AD-7 empty-string workarounds removed where obsolete.

---

#### Story 5.4: Decouple Open/Generate from preferences.json

As a JUCE developer,
I want Open and Generate to leave my global Preferences untouched,
So that working on one project never overwrites my default profile.

**Acceptance Criteria:**

**Given** I open or generate a project successfully,
**When** the operation completes,
**Then** `preferences.json` is **not** modified (no `prefs.update(spec)`, no `prefs.save()` in `_load_project` or `_run_generation`).

**Given** a successful Generate,
**When** generation completes,
**Then** the last-used **parent** destination folder is remembered for subsequent Choose… and Open Project… starting directories.

**Given** the remembered parent path is missing or invalid,
**When** Choose… or Open needs a default,
**Then** Desktop (via OS API) is used as fallback.

**Given** destination folder is empty or invalid before Generate on a new project,
**When** I click Generate,
**Then** Luthier may prompt via Choose… or folder dialog before continuing.

**Given** AD-5 in architecture-spine.md,
**When** Epic 5.4 is complete,
**Then** the revised AD-5 rule is satisfied and `project-context.md` reflects the new persistence model.

---

#### Story 5.5: Create New Project (Full Reset + Dirty Guard)

As a JUCE developer,
I want Create New Project to reset the form from my current Preferences profile,
So that I can start a fresh plugin without affecting global settings or an previously opened project config.

**Acceptance Criteria:**

**Given** I click **Create New Project**,
**When** the form is clean (no unsaved edits since last stable state),
**Then** project name and display name are cleared, version set to `1.0.0`, and all other fields re-seeded from `preferences.json`.

**Given** the Project form has unsaved edits (dirty),
**When** I click **Create New Project**,
**Then** a confirmation dialog warns before discarding changes.

**Given** Create New Project completes,
**When** I inspect `preferences.json`,
**Then** it is unchanged (read-only use of prefs for seeding).

**Given** dirty-state tracking,
**When** I load a project, edit fields, or reset,
**Then** baseline updates appropriately so the dirty guard reflects real user edits.

---

## 5. Proposed sprint-status.yaml Update

**File:** `_bmad-output/implementation-artifacts/sprint-status.yaml`

Add after Epic 3 block, **before** Epic 4:

```yaml
  # Epic 5: Project & Preferences Workflows (priority before Epic 4)
  epic-5: backlog
  5-1-preferences-model-profile-workflow: backlog
  5-2-project-ui-choose-buttons-layout: backlog
  5-3-jucedir-on-projectspec-generation-pipeline: backlog
  5-4-decouple-open-generate-from-preferences-json: backlog
  5-5-create-new-project-full-reset-dirty-guard: backlog
  epic-5-retrospective: optional
```

Update header comment:

```yaml
last_updated: 2026-06-25 # epic 5 added via correct-course
```

**Note:** Epic 4 entries remain `backlog` — execution order Epic 5 → Epic 4.

---

## 6. Implementation Handoff

### 6.1 Scope Classification: **Moderate**

Requires backlog reorganization (new epic, priority swap) and coordinated doc + code updates across app and core layers.

### 6.2 Handoff Recipients

| Role | Responsibility |
|------|----------------|
| **PO (Guillaume)** | Approve this proposal; validate against USER-MANUAL §12 checklist after Epic 5 |
| **Create Epics and Stories `[CE]`** | Apply approved edits to PRD, ARCHITECTURE-SPINE, epics.md; create story files 5.1–5.5 |
| **Dev Story `[DS]`** | Implement in order 5.1 → 5.3 → 5.2 → 5.4 → 5.5 |
| **Architect (Winston)** | Review AD-5/AD-7 revision during 5.3/5.4 if needed |

### 6.3 Post-Approval Actions (Not Applied Until PO Approves)

1. Update `prd.md` (F5, F7, F8)
2. Update `architecture-spine.md` (AD-2, AD-5, AD-7; structural seed comment for `juce_dir`)
3. Update `epics.md` (Epic 5 block, FR map, supersession note, AD bullets)
4. Update `sprint-status.yaml` (Epic 5 entries)
5. Run `[CE]` to generate story spec files under `implementation-artifacts/`

### 6.4 Success Criteria (Epic 5 Done)

1. `Docs/USER-MANUAL.md` §12 items implemented and verified
2. Open → Generate does not modify `preferences.json` (automated or documented manual test)
3. Import profile → Create New Project seeds all fields including type, formats, compilation
4. `juceDir` round-trip in `.luthier.json` (generate → open → regenerate, empty sidecar diff)
5. Choose… on destination and JUCE; no Choose on artefact OS paths
6. Moved project + Open → destination folder = new parent
7. Full pytest suite green

---

## 7. Approval

| Field | Value |
|-------|-------|
| Proposal status | **Approved** |
| Approved by | Guillaume (PO), 2026-06-25 |
| Artifacts updated | PRD (F5/F7/F8), ARCHITECTURE-SPINE (AD-2/5/7), epics.md, sprint-status.yaml |

---

*Generated by bmad-correct-course — Batch mode — 2026-06-25*
