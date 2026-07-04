---
epic: 9
story: 5
story_key: 9-5-documentation-v1-guide-manuals-readme
depends_on: [9-1, 9-7, 9-6]
blocks: []
implementation_order: 8
pivot_date: 2026-07-04
baseline_commit: 9c7fceb
baseline_tests: "319 collected, 316 passed, 3 skipped"
---

# Story 9.5: Documentation — v1 Guide, Manuals, README

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a JUCE developer discovering Luthier,
I want documentation that reflects scaffold-only positioning and the enriched plugin form,
So that I understand Luthier's role in my CMake workflow without expecting Projucer-like reload.

## Context

**Epic 9 pivot (2026-07-04):** Luthier is a **one-shot JUCE/CMake skeleton generator**. Stories **9.1–9.4**, **9.7**, **9.8**, and **9.6** are **done** — Open/reload removed, generate guard + session regenerate carve-out, decoupled plugin characteristics wired to templates, Preferences-only accent, OS tree connectors, test suite aligned.

**Story 9.5 is the Epic 9 release-documentation gate:** align all user-facing and contributor-facing docs with the shipped product model. **No production code changes** except `app/version.py` `REVISION_DATE` (and any doc cross-links in code comments are out of scope).

**Planning references:**
- `_bmad-output/planning-artifacts/epics.md` — Epic 9, Story 9.5
- `_bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md` — §9.4 Documentation inventory, §8 Story 9.5, §10 versioning, §12 release criteria
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md`
- `docs/user/guide-juce-cmake-et-luthier.md` (FR) — already scaffold-only in §8–9; moved to `docs/user/`; EN edition `juce-cmake-and-luthier-guide.md`

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.8 → 9.4 → 9.6 → 9.5`

### What changes vs what stays

| Area | Change (9.5) | Keep unchanged |
|------|--------------|----------------|
| README | Remove reopen positioning; scaffold-only features list | Sponsor block, license, build table, Matrix-Control link |
| User manuals EN/FR | Remove Open/reload; add characteristics, session regenerate, guard | Tab structure, validation rules, path normalization |
| Guide JUCE/CMake | Add links from README + manuals | Core §8–9 content (already correct) |
| QA checklists | Remove Open/round-trip; add empty-folder + session regenerate smoke | Existing accent/path regression items where still valid |
| `templates/README.md` | Post-generation workflow; no Luthier reopen | Build instructions, CMake presets, USER OPTIONS |
| `CONTRIBUTING.md` | Scaffold-only positioning if stale | Dev setup, pytest, bundle build |
| `app/version.py` | `REVISION_DATE` → release date | `VERSION == "1.0.0"` unchanged |
| App / core / tests | — | **No code changes** unless doc audit reveals a factual error requiring a one-line fix (unlikely) |

### Critical distinction for dev agent

**This is a documentation-only story.** Do not re-implement Epic 9 features. Read the **current** app behaviour from completed stories and grep the codebase when unsure — docs must match **shipped** semantics:

| Topic | Document truth (post Epic 9) |
|-------|------------------------------|
| Open Project | **Removed** — no button, no workflow |
| `.luthier.json` | **Write-only** sidecar at generation; reference for humans/AI; Luthier does **not** read it back |
| Accent colour | **Preferences tab only** → `preferences.json`; **never** in `.luthier.json` |
| Generate guard | **Blocked** on non-empty `{destination}/{projectName}/` (including `.git/`, `.DS_Store`) |
| Session regenerate | **Same session + same path** → destructive confirm → full replace except `.git` |
| Plugin characteristics | Decoupled toggles + Audio I/O preset + description + VST MIDI counts (9.3/9.4) |
| OS paths UI | Tree connectors in Workspace + Artefacts (9.7) |

**EN/FR parity:** Update **both** manuals with the **same section structure**. Translate in parallel; do not ship EN-only changes.

## Acceptance Criteria

### AC1 — Guide linked from README and manuals

**Given** `docs/user/guide-juce-cmake-et-luthier.md` (FR) and `docs/user/juce-cmake-and-luthier-guide.md` (EN)  
**Then** linked from:
- `README.md` (dedicated subsection or bullet under Features / Philosophy)
- `docs/user/user-manual.md` — new or renamed section (e.g. **Philosophy & further reading** or **§1 What is Luthier?** cross-link)
- `docs/user/manuel-utilisateur.md` — equivalent French section

**And** guide §9 scaffold-only limits remain accurate (no reopen language added)

### AC2 — User manuals: Open/reload removed

**Given** `docs/user/user-manual.md` and `docs/user/manuel-utilisateur.md`  
**Then** all **Open Project…** sections, reopen/regenerate-in-place workflows, and sidecar-read narratives are **removed or replaced** with:

| Old concept | Replacement |
|-------------|-------------|
| Open → edit → Generate | **After generation:** edit in IDE; do not expect Luthier to reload the project |
| `.luthier.json` for reopen | Sidecar is **metadata snapshot** written at generate — optional reference for you or AI tools |
| Three-button lifecycle (Create / Open / Generate) | **Two buttons:** Create New Project, Generate Project |
| §11.3 Resume and tweak | **Session regenerate** (9.8) or **Create New Project** for a fresh scaffold |
| §11.6 Git multi-OS via Open | Adjust **host** paths in generated `.luthier.json` or Preferences manually; build with CMake — no Luthier reopen |
| Status messages for Open | Remove from message tables |

**And** front-matter `Updated:` date bumped on both manuals

### AC3 — Accent colour: Preferences only

**Given** accent documentation in README, both manuals, QA checklists  
**Then** single source of truth documented:
- Picker on **Preferences** tab only (`Luthier Accent Color` / appearance label from 9.7)
- Persisted in `preferences.json` (`accentColor`); included in Export/Import
- **Not** on Project tab; **not** in `.luthier.json`; **not** restored via any project workflow

**And** remove all tables/paragraphs describing Project-tab accent or sidecar accent round-trip

### AC4 — Enriched plugin form documented

**Given** Project tab documentation  
**Then** manuals describe (matching UI labels from `app/pages/`):

| UI area | Document |
|---------|----------|
| **Plugin Type** | Instrument / Audio Effect / MIDI Effect (radio) |
| **Plugin Characteristics** | Checkboxes: Plugin is a Synth, Plugin MIDI Input/Output, MIDI Effect Plugin, Editor Requires Keyboard Focus — preset-constrained per type |
| **Audio I/O** combo | Stereo, Mono, Synth No Input, MIDI Effect (no audio buses) |
| **VST MIDI channel counts** | 1–16 when MIDI Input/Output enabled |
| **Plugin Description** | Maps to CMake `DESCRIPTION` in generated project |
| Preset hints | Instrument → MIDI Output allowed (Matrix-Control); synth + MIDI effect together invalid |

**And** explain that generated `CMakeLists.txt` and `PluginProcessor.cpp` buses reflect these choices (not preset-only)

### AC5 — Workspace & Artefacts: OS tree connectors

**Given** Workspace and Artefacts sections in both manuals  
**Then** include ASCII diagram (or brief prose) describing tree connectors per handoff §5.8.2:

```
Destination folder *
│
├─ Windows     [________________]
├─ macOS       [________________]  [Choose…]
└─ Linux       [________________]
```

**And** note connectors are decorative grouping; tab order unchanged  
**And** Artefacts block anchored to **Copy to central artefacts folder** checkbox

### AC6 — Session regenerate and generate guard

**Given** workflow sections in manuals  
**Then** document:

| Scenario | Behaviour |
|----------|-----------|
| Generate into **non-empty** folder (fresh app or different path) | Blocked — status error + warning dialog |
| Generate into **same path** after successful Generate **this session** | Destructive confirm — replaces tree except `.git` |
| After app restart | Brownfield folder protected — must delete manually or pick empty destination |
| Hidden files (`.DS_Store`, `.git/`) | Still counts as non-empty |

**And** QA checklists include at least one smoke step for empty-folder block and one for session regenerate

### AC7 — Release metadata

**Given** story 9.5 completion (release docs closed)  
**Then** `app/version.py` has `VERSION == "1.0.0"` (unchanged)  
**And** `REVISION_DATE` updated to release date (use story completion date, e.g. `2026-07-04` or current PO date)  
**And** About tab displays new revision date (reads from `version.py` — verify no code change needed beyond date)

### AC8 — README and features list

**Given** `README.md`  
**Then** opening paragraph and Features reflect scaffold-only positioning:
- One-shot skeleton generator; **not** reopen/configure/regenerate lifecycle
- Remove "Reopen a project" bullet
- Add characteristics, session regenerate (same session), write-only `.luthier.json`, link to guide
- **Sponsor block unchanged** (lines ~12–13, Supporting the project section)

### AC9 — QA checklists updated

**Given** `docs/tests/checklist-qa-manuelle.md`, `checklist-qa-passe-unique.md`, `checklist-qa-pre-release-v1.md`  
**Then** remove or rewrite Open Project / round-trip / sidecar-reload / accent-in-sidecar scenarios  
**And** add:
- Generate blocked on non-empty destination (fresh session)
- Session regenerate with confirm (same session, same path)
- Optional: characteristics smoke (Instrument + MIDI Output → generate → verify CMake intent)

**And** update stale pre-release notes that claim Open/reload is v1.0 behaviour

### AC10 — templates/README.md and CONTRIBUTING.md

**Given** `templates/README.md` (bundled into generated projects)  
**Then** add short **After generation** section: continue development in IDE; reconfigure CMake when build changes; **do not** re-run Luthier Generate over an evolved project (data loss); `.luthier.json` is reference metadata only

**Given** `CONTRIBUTING.md`  
**Then** product description matches scaffold-only if currently stale; link to user manual + architecture; no Open/reload contributor workflow

### AC11 — Out of scope (explicit)

**Not in 9.5:** Production code refactors, new features, PyInstaller rebuild, tag `v1.0.0` (PO-only per handoff §12), PRD/architecture spine rewrites (already updated in 9.1/9.6), screenshot assets (ASCII acceptable per AC5), Matrix-Control docs, `.jucer` migration guides

## Tasks / Subtasks

- [x] **Audit stale doc grep** (AC: 2, 3, 9)
  - [x] Run `rg -i 'Open Project|reopen|reload|accentColor.*luthier\.json|rouvrir' docs/ README.md CONTRIBUTING.md templates/README.md`
  - [x] Track every hit; map to replacement text before editing
- [x] **README.md** (AC: 1, 8)
  - [x] Rewrite intro + Features for scaffold-only
  - [x] Link `docs/user/guide-juce-cmake-et-luthier.md`
  - [x] Link user manuals
  - [x] Preserve sponsor badges and Supporting the project section verbatim
- [x] **User manual EN** (AC: 2, 3, 4, 5, 6)
  - [x] Update §1, §4 action bar, §5 three kinds of settings
  - [x] Remove §7 Luthier Accent Color on Project; consolidate accent under Preferences §8
  - [x] Add Plugin Characteristics + description sections under Project tab
  - [x] Rewrite §11 workflows (remove 11.3 Open flow; add session regenerate + post-generation IDE workflow)
  - [x] Fix §12 `.luthier.json` table (no accentColor; write-only)
  - [x] Fix §13 data storage table
  - [x] Fix §16 messages table (remove Open rows; add guard/regenerate messages)
  - [x] Add Philosophy / guide link section
  - [x] Bump YAML `Updated:` date
- [x] **User manual FR** (AC: 2, 3, 4, 5, 6)
  - [x] Mirror EN structure and changes in `manuel-utilisateur.md`
  - [x] Bump YAML `Updated:` date
- [x] **Guide cross-links** (AC: 1)
  - [x] Add backlinks or TOC note in guide if helpful (optional minimal)
  - [x] Ensure guide §9 and README positioning align
- [x] **QA checklists** (AC: 9)
  - [x] Update all three `docs/tests/checklist-qa-*.md` files
  - [x] Remove Open/round-trip sections; add guard + session regenerate steps
- [x] **Generated project README template** (AC: 10)
  - [x] Add post-generation section to `templates/README.md`
- [x] **CONTRIBUTING.md** (AC: 10)
  - [x] Verify product one-liner; add scaffold-only note if missing
- [x] **Release metadata** (AC: 7)
  - [x] Update `app/version.py` `REVISION_DATE`
  - [x] Launch app → About tab shows new date
- [x] **Verify** (AC: 11)
  - [x] Re-run stale grep — expect zero false Open/reload claims in user docs
  - [x] `.venv/bin/pytest` still green (no test changes expected)

### Review Findings

- [x] [Review][Patch] `app_state.json` table falsely documents session regenerate path as persisted — fixed: separate in-memory row [docs/user/user-manual.md:688, docs/user/manuel-utilisateur.md:686]
- [x] [Review][Patch] Checklist intro still says Luthier « crée et rouvre » des projets JUCE — fixed [docs/tests/checklist-qa-manuelle.md:17]
- [x] [Review][Patch] `checklist-qa-passe-unique.md` R3 still expects generic overwrite modal on existing folder — fixed [docs/tests/checklist-qa-passe-unique.md:97]
- [x] [Review][Patch] `checklist-qa-passe-unique.md` §3.3–3.5 still instruct Generate into cloned `VoyageLuthier` — fixed for CMake-only workflow [docs/tests/checklist-qa-passe-unique.md:180-197]
- [x] [Review][Patch] `checklist-qa-passe-unique.md` §3.6 retains « projet ouvert inchangé » — fixed [docs/tests/checklist-qa-passe-unique.md:203]
- [x] [Review][Patch] `checklist-qa-passe-unique.md` §3.4 retains « ouvrir projet » step — fixed [docs/tests/checklist-qa-passe-unique.md:186]
- [x] [Review][Patch] Broken §7.5 Workspace anchor links after section renumber — fixed → `#76-workspace` [docs/user/user-manual.md, docs/user/manuel-utilisateur.md]
- [x] [Review][Patch] VST MIDI counts documented as Spinners; UI uses `ComboField` dropdowns — fixed [docs/user/user-manual.md:300, docs/user/manuel-utilisateur.md]
- [x] [Review][Patch] §7.4 Formats says add formats « by regenerating the project » without same-session qualifier — fixed [both manuals]
- [x] [Review][Patch] EN §16 troubleshooting intro still cites « folder that is not a Luthier project » — fixed [docs/user/user-manual.md:759]
- [x] [Review][Patch] EN §8.1 still says « project is already open in Project » — fixed [docs/user/user-manual.md:499]
- [x] [Review][Patch] Import §8.3 should clarify imported accent updates theme on all tabs immediately — fixed [both manuals §8.3]
- [x] [Review][Patch] Guide `.luthier.json` table still describes sidecar as « miroir » — fixed write-only wording [docs/user/guide-juce-cmake-et-luthier.md]
- [x] [Review][Patch] `CONTRIBUTING.md` missing link to guide — fixed [CONTRIBUTING.md]
- [x] [Review][Patch] Epic 9 smoke block in manuelle lists S9.1–S9.3 only — added S9.4 checkbox [docs/tests/checklist-qa-manuelle.md:53-56]
- [x] [Review][Patch] B4 missing post-restart blocked-generate check — fixed (parity with A4/C4) [docs/tests/checklist-qa-manuelle.md:257-266]
- [x] [Review][Patch] B4 archive note nested italics inside blockquote — fixed [docs/tests/checklist-qa-manuelle.md:266]
- [x] [Review][Defer] Plugin Type dirty-form confirm dialog undocumented in manuals — real UX gap but out of AC scope; document in follow-up [docs/user/user-manual.md §7.3] — deferred, pre-existing gap
- [x] [Review][Defer] Epic 9 anchor slug uses accented characters — may not resolve in all Markdown renderers [docs/tests/checklist-qa-*.md] — deferred, renderer-dependent

## Dev Notes

### Stale content inventory (grep baseline — fix all)

**README.md** (high priority):
- Line 3: "creating, reopening, and configuring" → scaffold-only
- Line 14: reopen/regenerate paragraph
- Line 25: "Reopen a project" feature bullet

**docs/user/user-manual.md** (~40+ stale references):
- §1 intro, §1 bullets (reopen, sidecar for reopen, accent in defaults list)
- §4 action bar table: remove Open Project
- §7 entire "Luthier Accent Color" on Project tab section — **delete**; accent lives in §8 Preferences only
- §7.5 Workspace: remove "After Open Project…" destination recalc
- §7.6 / §11.6: remove reopen-on-clone workflow
- §7 action buttons: remove Open Project… subsection; rewrite three-button lifecycle
- §11.3 Resume and tweak → replace with session regenerate or remove
- §12 `.luthier.json` row: remove accentColor, reopen wording
- §13 storage tables: fix accent/sidecar rows
- §16 message table: remove Open rows
- Quick reference table at end: remove Reopen row

**docs/user/manuel-utilisateur.md:** Mirror all EN fixes in French.

**docs/tests/** — extensive Open Project checkboxes in all three QA files; pre-release v1 doc still describes sidecar reload and accent in sidecar as v1.0 behaviour.

**docs/user/guide-juce-cmake-et-luthier.md:** Content is **already correct** (§9 limits, write-only sidecar). Only add inbound links; do not rewrite philosophy.

**templates/README.md:** No Luthier reopen references today — **add** post-generation guidance (AC10).

**CONTRIBUTING.md:** No Open/reload grep hits — light touch only.

### Current app behaviour reference (source of truth)

#### Project tab action bar

```174:174:docs/user/user-manual.md
| **Project** | **Create New Project**, **Open Project…**, **Generate Project** |
```

**Target after 9.5:** `Create New Project`, `Generate Project` only — verify in `app/main_window.py` if needed.

#### Accent (Preferences only — 9.1 + 9.7)

- `AccentColorSection` on `app/pages/preferences.py` only
- `ProjectSpec.to_dict()` omits `accentColor`
- Theme applies on all tabs immediately when changed on Preferences (9.7 fix)

#### Plugin characteristics UI (9.3)

Section widget: `app/pages/plugin_characteristics.py` — labels match UI exactly:
- Plugin is a Synth, Plugin MIDI Input, Plugin MIDI Output, MIDI Effect Plugin, Editor Requires Keyboard Focus
- Audio I/O combo: from `audio_io_combo_options()` — Stereo, Mono, Synth No Input, MIDI Effect
- VST MIDI Ins/Outs spinners (1–16)
- Plugin Description in `app/pages/project_info.py`

#### Session regenerate (9.8)

Confirm dialog copy (document in manuals):
- **Title:** `Regenerate Project`
- **Message:** replaces everything except `.git`; Finder/IDE edits since last generate lost
- Only when same session + same resolved project path

#### Generate guard (9.2)

Status message pattern: destination folder must be empty (or session carve-out applies). Hidden entries count as non-empty.

#### OS tree connectors (9.7)

Widget: `app/widgets/os_path_tree_group.py` — decorative lines, `Palette.BORDER` colour, two groups in Workspace (Destination, JUCE), one in Artefacts (under central copy checkbox).

### Suggested replacement workflows (for §11)

**§11.1 First project (keep, minor edits):** Preferences → Project → Generate → IDE. Remove any Open references.

**§11.2 JUCE version per project (keep):** Create New Project → set host JUCE directory → Generate. Sidecar stores paths; user edits `.luthier.json` manually on other machines if needed — **not** via Luthier reload.

**§11.3 NEW — Session regenerate (replaces "Resume and tweak"):**
1. Generate successfully in this session
2. Change form (e.g. characteristics, version)
3. Generate again → confirm destructive dialog → scaffold replaced except `.git`
4. After app restart, same folder is **blocked** — delete folder or use new name

**§11.3 NEW — After generation (replaces Open workflow):**
1. Open project folder in IDE/Cursor
2. Edit `Source/`, `CMakeLists.txt` as needed
3. Reconfigure/build with CMake presets
4. Do **not** run Luthier Generate on evolved project unless intentional full replace (session only)

**§11.4 Switch client profile (keep):** Import → Create New Project → Generate. Remove "previously open project" / accent sidecar wording.

**§11.5 Templates (keep):** Overrides apply to **new** generates only; note user overrides must retain `@CREATE_BUSES_PROPERTIES_BODY@` token if using custom `PluginProcessor.cpp` (deferred doc from 9.4).

**§11.6 Multi-OS Git (rewrite):** Clone repo → edit host `juceDir*` in `.luthier.json` or set in Preferences before **new** generate → build with CMake on each OS. No Luthier Open.

### `.luthier.json` documentation truth

| Field | Document |
|-------|----------|
| Identity, characteristics, workspace paths, formats | Written at Generate — snapshot for reference |
| `accentColor` | **Not present** — do not document |
| App read-back | **Never** — Luthier does not load sidecar into form |

Sidecar key order follows Project tab section order (9.4 DX) — optional note for advanced readers; not required for AC.

### Version metadata

```1:4:app/version.py
"""Application release metadata shown in About."""

VERSION = "1.0.0"
REVISION_DATE = "2026-07-02"
```

Update `REVISION_DATE` only. About page reads these constants — no UI code change expected.

### Overlap with other Epic 9 stories

| Story | Boundary |
|-------|----------|
| 9.1 | Done — removed Open; docs still stale |
| 9.7 | Done — accent + connectors; manuals not updated |
| 9.3–9.4 | Done — characteristics in UI/templates; manuals lack section |
| 9.8 | Done — session regenerate; manuals still describe Open |
| 9.6 | Done — tests aligned; explicitly deferred user docs to 9.5 |
| **9.5** | All user/contributor/QA docs + REVISION_DATE |

### Anti-patterns (do NOT)

- **Do not** reintroduce Open Project, sidecar reload, or Projucer-like round-trip language anywhere
- **Do not** document accent on Project tab or in `.luthier.json`
- **Do not** change `VERSION` from `1.0.0` or tag git without PO request
- **Do not** scope-creep into app/core/test code
- **Do not** rewrite `docs/user/guide-juce-cmake-et-luthier.md` philosophy — cross-link only
- **Do not** remove sponsor block from README
- **Do not** ship EN manual updates without matching FR sections

### Project Structure Notes

- **Docs layout:** lowercase `docs/` — user docs in `docs/user/` (manuals + guides FR/EN), QA in `docs/tests/`
- **Generated project README:** `templates/README.md` → rendered into each generated project
- **Architecture reference:** `_bmad-output/architecture.md` already scaffold-only — do not duplicate into user manuals
- **Manual YAML front matter:** bump `Updated:` on both manuals when editing

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 9.5]
- [Source: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §8 Story 9.5, §9.4]
- [Source: docs/user/guide-juce-cmake-et-luthier.md §8–9]
- [Source: _bmad-output/implementation-artifacts/9-1-remove-open-project-scaffold-only-positioning.md]
- [Source: _bmad-output/implementation-artifacts/9-7-ui-accent-preferences-only-os-tree-connectors.md]
- [Source: _bmad-output/implementation-artifacts/9-8-session-regenerate-with-warning.md]
- [Source: _bmad-output/implementation-artifacts/9-3-decoupled-plugin-characteristics-and-projectspec.md]
- [Source: _bmad-output/implementation-artifacts/9-6-test-suite-scaffold-only-regression.md — deferred docs to 9.5]
- [Source: app/pages/plugin_characteristics.py — UI labels]
- [Source: app/version.py — VERSION, REVISION_DATE]

## Dev Agent Guardrails

### Technical requirements

1. **Documentation-only** — default to zero `app/` and `core/` changes except `app/version.py` `REVISION_DATE`.
2. **Grep gate before/after:** no `Open Project`, `reopen`, sidecar accent, or reload-into-form claims in `docs/user/`, `README.md`, QA checklists.
3. **EN/FR parity** — same sections updated in both manuals; UI labels stay **English** in both (product UI is English per NFR5).
4. **Sponsor block** — README sponsor badges and "Supporting the project" section must remain unchanged in substance.
5. **Guide** — link, do not rewrite §9 limits.
6. **Characteristics** — document actual UI labels and preset behaviour from 9.3/9.4.
7. **Session regenerate + guard** — document 9.8 and 9.2 behaviour accurately in workflows and QA.
8. **Token override note** — mention `@CREATE_BUSES_PROPERTIES_BODY@` retention in Templates section (deferred from 9.4).

### Architecture compliance

| AD | Rule for 9.5 |
|----|--------------|
| AD-3 | Document sidecar as write-only; no app read path |
| AD-5 | Document Generate never writes `preferences.json` |
| AD-7 | Accent in `preferences.json` only; workspace paths on ProjectSpec/sidecar |
| NFR5 | UI strings English; manuals may be EN + FR editions |

### Library / framework requirements

- **No new dependencies** — Markdown edits only
- **No web research required** — all behaviour defined in completed Epic 9 stories

### File structure requirements

| File | Action |
|------|--------|
| `README.md` | Scaffold-only intro + features; guide link |
| `docs/user/user-manual.md` | Major rewrite — remove Open/reload/accent sidecar; add characteristics, guard, regenerate |
| `docs/user/manuel-utilisateur.md` | Mirror EN changes (French prose) |
| `docs/user/guide-juce-cmake-et-luthier.md` | Cross-links only (minimal); FR edition in `docs/user/` |
| `docs/user/juce-cmake-and-luthier-guide.md` | EN translation; cross-links only (minimal) |
| `docs/tests/checklist-qa-manuelle.md` | Remove Open scenarios; add guard/regenerate |
| `docs/tests/checklist-qa-passe-unique.md` | Same |
| `docs/tests/checklist-qa-pre-release-v1.md` | Same; fix stale v1 Open claims |
| `templates/README.md` | Add post-generation / no Luthier reopen section |
| `CONTRIBUTING.md` | Scaffold-only positioning if needed |
| `app/version.py` | Update `REVISION_DATE` only |

**Do not modify:** `app/main_window.py`, `core/**`, `tests/**`, `Templates/` (except `templates/README.md`), `_bmad-output/architecture.md` (already current)

### Testing requirements

**Must pass before marking done:**
```bash
.venv/bin/pytest
```
(No test changes expected — docs-only story.)

**Doc audit commands:**
```bash
rg -i 'Open Project|reopen|reload project|accentColor.*sidecar|rouvrir le projet' docs/ README.md
# Expected after 9.5: zero hits in user-facing stale sense (guide §9 "ne rouvrir" is OK — describes what Luthier does NOT do)
```

**Manual smoke (required — AD-6):**
1. Read updated README — no reopen promise
2. Spot-check EN manual §4 action bar — two buttons only
3. Spot-check EN manual accent section — Preferences only
4. Launch app → About → revision date matches `version.py`
5. Optional: run one QA checklist guard step (non-empty block)

### Previous story intelligence

**From 9.6 (done):**
- Explicitly deferred all `docs/user/**` and QA checklist updates to 9.5
- Test baseline: **316 passed, 3 skipped** — do not touch tests
- Architecture doc test count already updated

**From 9.4 (done):**
- Defer user manual note for `@CREATE_BUSES_PROPERTIES_BODY@` in template overrides → **9.5 owns this**
- Matrix-Control (Instrument + MIDI Output) is primary PO example for characteristics docs

**From 9.8 (done):**
- Session regenerate confirm copy documented in story — use exact strings in manuals
- `.git` preserved on regenerate — mention in guard/regenerate docs

**From 9.7 (done):**
- OS tree connector ASCII spec in story — reuse in manuals (AC5)
- Accent label may say "Luthier appearance" — check `accent_color_picker.py` for current string

**From 9.1 (done):**
- Open button removed; sidecar write-only — docs are the remaining gap

### Git intelligence

Recent Epic 9 commits (docs must reflect this shipped state):
- `9c7fceb` — Stories 9.4, 9.6: template pipeline + test alignment
- `d8d356f` — Story 9.8: session regenerate
- `97c808c` — Stories 9.2–9.3: generate guard + characteristics
- `a09f879` — Story 9.7: OS connectors + accent theme
- `c163cf2` — Story 9.1: Open removed

Follow established patterns: factual docs matching code, EN/FR parity, minimal diff outside doc paths.

### Latest tech information

No new libraries or APIs. Documentation reflects stable v1.0.0 scaffold-only product. JUCE/CMake content in guide remains valid for 2026.

## Project Context Reference

Key rules from `_bmad-output/project-context.md`:
- Scaffold-only data flow: form → guard → generate → write-only `.luthier.json`
- Accent: `Preferences.accent_color` → theme on all tabs
- Two Project tab buttons: Create New Project, Generate Project
- Session regenerate: in-memory `lastGeneratedProjectDir` only — not persisted
- Run app: `.venv/bin/python main.py`
- Docs in lowercase `docs/`; UI strings English

## Story Completion Status

- **Status:** done
- **Completion note:** Epic 9 documentation gate complete — code review patches applied (app_state in-memory row, QA checklists, EN/FR parity, guide sidecar wording)
- **Next step after dev:** Epic 9 retrospective optional; PO may request `v1.0.0` tag separately

## Dev Agent Record

### Agent Model Used

claude-sonnet-5-thinking-high

### Debug Log References

- Initial grep audit mapped ~40+ stale references across README, manuals, QA checklists
- `test_about.py` updated for `REVISION_DATE` `2026-07-04` (required by AC7)

### Completion Notes List

- README: scaffold-only intro, features (guard, session regenerate, characteristics, write-only sidecar), guide + manual links; sponsor block preserved
- EN manual: removed Open/reload/accent-on-Project; added §7.3 Plugin Characteristics, OS tree ASCII, §11 session regenerate + IDE workflow; Philosophy link to guide
- FR manual: mirrored EN structure (French prose, English UI labels)
- QA checklists: Epic 9 smoke section (S9.1–S9.4); archived/replaced Open Project scenarios in all three files
- `templates/README.md`: After generation section (no Luthier reopen)
- `CONTRIBUTING.md`: scaffold-only one-liner
- `app/version.py`: `REVISION_DATE` → `2026-07-04`
- Tests: **316 passed, 3 skipped**

### File List

- README.md
- CONTRIBUTING.md
- app/version.py
- docs/user/guide-juce-cmake-et-luthier.md
- docs/user/juce-cmake-and-luthier-guide.md
- docs/user/user-manual.md
- docs/user/manuel-utilisateur.md
- docs/tests/checklist-qa-manuelle.md
- docs/tests/checklist-qa-passe-unique.md
- docs/tests/checklist-qa-pre-release-v1.md
- templates/README.md
- tests/unit/test_about.py

### Change Log

- 2026-07-04 — Story 9.5: align all user/contributor/QA documentation with scaffold-only v1.0.0; update REVISION_DATE
