---
epic: 9
story: 1
story_key: 9-1-remove-open-project-scaffold-only-positioning
depends_on: []
blocks: [9-7, 9-6, 9-5]
implementation_order: 1
pivot_date: 2026-07-04
baseline_commit: 38747d278495fb4ae4bc7f5cd2a4617311142130
---

# Story 9.1: Remove Open Project (Scaffold-Only Positioning)

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a JUCE developer,
I want Luthier to focus solely on creating new project skeletons,
So that I am not misled into destructive regeneration over an existing CMake project.

## Context

**Epic 9 pivot (2026-07-04):** Luthier becomes a **one-shot JUCE/CMake skeleton generator**. Story 9.1 is the foundation — remove all reload/reopen paths and reposition the product. **No backward compatibility** (PO §2.3): delete legacy code; do not shim old `.luthier.json` sidecars.

**Supersedes:** Epic 2 (Reliable Project Reload), Story 8.2 sidecar-required-on-Open behaviour.

**Planning references:**
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md`
- `_bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md` (§8 Story 9.1, §9.1 file inventory)
- `_bmad-output/planning-artifacts/epics.md` — Epic 9 section

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.4 → 9.6 → 9.5`

### What changes vs what stays

| Area | Remove (9.1) | Keep |
|------|--------------|------|
| Open Project UI + handlers | `_open_btn`, `_on_open`, `_load_project`, `read_project_result` import | Create New Project, Generate Project buttons |
| Reload module | `core/project_reader.py` entirely | — |
| Sidecar | Any **read** of `.luthier.json` | `ProjectWriter._write_sidecar()` on Generate (write-only metadata for humans/AI) |
| Project-tab accent | `AccentColorSection` on Project tab, `ProjectSpec.accent_color`, `accentColor` in sidecar | `AccentColorSection` on **Preferences** tab; `prefs.accent_color` drives Luthier theme |
| Post-generate form sync | — | `MainWindow._run_generation()` → `ProjectPage.load(spec)` (baseline reset, **not** Open) |
| Overwrite confirm | — | `_confirm_overwrite()` stays until Story 9.2 (non-empty guard) |
| AD-5 prefs isolation | — | Open/Generate never call `prefs.save()` (Open path removed entirely) |

### Critical distinction for dev agent

`ProjectPage.load(spec)` is used in three places today:
1. **`_load_project`** — **DELETE** (Open Project reload)
2. **`_run_generation`** — **KEEP** (sync dirty baseline after successful Generate)
3. **`reset` / `_seed_new_project`** — **KEEP** (Create New Project)

Do **not** remove `ProjectPage.load()` — only remove the Open entry point.

## Acceptance Criteria

### AC1 — Project tab action bar

**Given** Luthier running  
**When** the user views the Project tab action bar  
**Then** buttons are **Create New Project** and **Generate Project** only — no **Open Project…**

### AC2 — Reload code path removed

**Given** the codebase  
**Then** `core/project_reader.py` is **deleted**  
**And** no app-layer import of `read_project_result` or `project_reader`  
**And** no `_on_open`, `_load_project`, open dialog constant, or Open status messages in `app/`  
**And** no menu item or keyboard shortcut for Open (today: button only — verify no new shortcuts added)  
**And** no backward-compatibility shim for older `.luthier.json` sidecars (PO §2.3)

### AC3 — Sidecar still written (write-only)

**Given** successful Generate  
**Then** `.luthier.json` is still written alongside CMake/sources  
**And** no module in `app/` or `core/` reads `.luthier.json` at runtime

### AC4 — Architecture docs superseded

**Given** Epic 2 / reload documentation in `_bmad-output/architecture.md`, `_bmad-output/project-context.md`, and `architecture-spine.md`  
**Then** reload/round-trip narrative is replaced with write-only AD-3  
**And** Epic 2 is marked **superseded by Epic 9** with a brief note (epics.md may already contain this — verify consistency)

### AC5 — Project-tab accent removed

**Given** the Project tab scroll content  
**Then** no **Luthier Accent Color** / `AccentColorSection`  
**And** the colour picker exists **only** on the Preferences tab (handoff §5.8.1)

### AC6 — No accent in sidecar

**Given** successful Generate  
**Then** `.luthier.json` does **not** contain `accentColor`  
**And** `ProjectSpec.to_dict()` omits `accentColor`

### AC7 — Theme from Preferences only

**Given** the user changes accent on Preferences  
**Then** Luthier theme updates immediately  
**And** tab switching no longer reads accent from Project tab (single source: `prefs.accent_color`)

### AC8 — Tests and CI green

**Given** full `pytest` run  
**When** story 9.1 is complete  
**Then** all tests pass  
**And** `grep -r "project_reader\|read_project_result" app/ core/` returns no matches (except deleted file gone)

## Tasks / Subtasks

- [x] **Remove Open Project UI and wiring** (AC: 1, 2)
  - [x] `app/main_window.py`: remove `_OPEN_PROJECT_DIALOG_TITLE`, `_open_btn`, `_on_open`, `_load_project`, `read_project_result` import
  - [x] `_project_buttons()`: return `[Create New, Generate]` only via `_make_button_bar`
  - [x] Remove `#OpenButton` QSS block from `app/theme.py` (dead style cleanup)
- [x] **Delete reload module** (AC: 2, 3)
  - [x] Delete `core/project_reader.py`
  - [x] Grep entire repo; fix any remaining imports
- [x] **Remove Project-tab accent** (AC: 5, 6, 7)
  - [x] `app/pages/project.py`: remove `AccentColorSection` import, `_accent` field, `accent_section()`, layout widget, `accentColor` in `spec()`, `set_color` in `load()`
  - [x] `core/project_spec.py`: remove `accent_color` field; drop `accentColor` from `to_dict()` / `from_dict()`; remove `normalize_accent_color` import if unused
  - [x] `app/main_window.py`: remove `_on_project_accent_changed`, simplify `_accent_color_for_tab()` to always return `self._prefs.accent_color`; disconnect project accent signal; remove `accent_section()` calls in `_on_create_new_project` and `_run_generation`; keep `_on_prefs_accent_changed` + startup `apply_accent_theme(prefs.accent_color)`
- [x] **Verify sidecar write** (AC: 3, 6)
  - [x] Confirm `core/project_writer.py` `_write_sidecar()` still calls `spec.to_dict()` — accent key gone after `ProjectSpec` change
  - [x] Add/update assertion in `tests/unit/test_project_writer.py`: sidecar JSON has no `accentColor` key
- [x] **Update agent/contributor docs** (AC: 4)
  - [x] `_bmad-output/project-context.md`: remove `_on_open` data-flow branch; revise AD-3 to write-only sidecar; remove `project_reader.py` from layout; drop round-trip reload bullets
  - [x] `_bmad-output/architecture.md`: remove/replace "Round-trip reload (AD-3)" section; remove Open Project references; document write-only sidecar
  - [x] `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md`: revise AD-1/AD-3; remove `project_reader` from structural seed and contract table
- [x] **Fix tests** (AC: 8)
  - [x] Delete `tests/unit/test_project_reader.py`
  - [x] `tests/unit/test_core_imports.py`: remove `"core.project_reader"` from parametrize
  - [x] `tests/unit/test_project_spec.py`: remove `accent_color` round-trip tests; update `to_dict` assertions
  - [x] `tests/unit/test_project_dirty_guard.py`: replace accent dirty test with a non-accent field change
  - [x] `tests/integration/test_round_trip.py`: rewrite to generation-only (write files, assert `.luthier.json` exists, assert no `accentColor`; **no** `read_project_result`)
  - [x] `tests/integration/test_cmake_cross_platform.py`: remove sidecar reload assertions via reader
  - [x] `tests/integration/test_frozen_bundle.py`: remove reload-after-generate assertion
  - [x] `tests/unit/test_workspace_migration.py`: remove `test_open_project_updates_host_destination_only` (reader-dependent)
  - [x] Run `.venv/bin/pytest` — full suite green
- [x] **Preserve behaviours** (regression guard)
  - [x] Create New Project + dirty guard still works
  - [x] Generate → status OK → `AppState.remember_parent()` still runs
  - [x] Preferences accent + import/export unchanged

### Review Findings

- [x] [Review][Decision] `epics.md` hors périmètre file list — Conservé : contenu Epic 9 aligné sprint change proposal ; ajouté au Dev Agent Record.

- [x] [Review][Patch] `_accent_color_for_tab` lit le widget Prefs au lieu de `prefs.accent_color` — Corrigé : retourne toujours `self._prefs.accent_color`. [app/main_window.py:157-158]

- [x] [Review][Patch] Numérotation « Known Technical Debt » saute l’item 6 — Renuméroté 6–9. [_bmad-output/project-context.md:266-269]

- [x] [Review][Defer] `_confirm_overwrite` autorise encore la régénération destructive — Hors scope 9.1 (Story 9.2). Comportement documenté dans la story Out of scope.

- [x] [Review][Defer] `test_regenerate_*` ne rechargent plus le sidecar — Réécriture volontaire (AC8 / tasks) : plus de `read_project_result` ; couverture round-trip sidecar→regenerate reportée à Epic 9.6 si besoin.

- [x] [Review][Defer] Validation `pluginType` supprimée avec `project_reader` — `ProjectSpec.from_dict` accepte toute chaîne ; acceptable tant qu’aucun module ne lit `.luthier.json` à l’exécution (AC3).

- [x] [Review][Defer] Import Preferences n’applique le thème que sur l’onglet Prefs — Pré-existant ; non introduit par ce diff ; QA manuelle AD-6.

## Dev Notes

### Current state — files to modify

#### `app/main_window.py` (576 lines — orchestration hub)

**Open path (DELETE):**
```python
# L43: from core.project_reader import read_project_result
# L48: _OPEN_PROJECT_DIALOG_TITLE
# L250: self._open_btn = _make_btn("Open Project…", "OpenButton", self._on_open)
# L252: _make_button_bar([self._new_btn, self._open_btn, self._generate_btn])
# L498-524: _on_open(), _load_project()
```

**Accent path (SIMPLIFY to prefs-only):**
```python
# L148-150: _on_project_accent_changed — DELETE
# L163-168: _accent_color_for_tab — return self._prefs.accent_color always (or inline at call sites)
# L174-175: tab change accent — use prefs.accent_color
# L190: disconnect project accent colorChanged signal
# L493-495, L519-520, L543-544: remove accent_section() calls; use self._prefs.accent_color for theme
```

**Preserve:** `_run_generation()` lines 536-554 — keep `ProjectPage.load(spec)` after generate; keep `AppState.remember_parent()`.

#### `app/pages/project.py`

- `AccentColorSection` at top of scroll (L44, L114) — remove widget and import
- `spec()` L74: `d["accentColor"] = ...` — remove
- `load()` L99: `self._accent.set_color(...)` — remove
- `accent_section()` public API — remove (grep callers in `main_window.py` only)

#### `core/project_spec.py`

- Field `accent_color: str = DEFAULT_ACCENT_COLOR` (L52) — remove
- `to_dict()` key `"accentColor"` (L100) — remove
- `from_dict()` `accent_color=normalize_accent_color(...)` (L132) — remove
- Remove unused imports from `core.accent_colors` if no longer referenced

#### `core/project_writer.py` — **UPDATE nothing** (sidecar write stays)

```104:108:core/project_writer.py
    def _write_sidecar(self, dest: Path, spec: ProjectSpec) -> None:
        (dest / ".luthier.json").write_text(
            json.dumps(spec.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
```

Sidecar content follows `ProjectSpec.to_dict()` — removing `accentColor` from the dataclass is sufficient.

#### `core/project_reader.py` — **DELETE entire file** (105 lines)

Sole app consumer: `main_window.py`. Test files import directly — see test section.

### Target data flow (post-9.1)

```
User fills form (ProjectPage)
  → ProjectPage.spec() → ProjectSpec
  → MainWindow._on_generate()
      → ProjectGenerator.generate(spec)
          → ProjectWriter.write() → CMake + sources + .luthier.json (write-only)
      → ProjectPage.load(spec)   ← baseline sync only
      → AppState.remember_parent() + save()
Preferences.accent_color → apply_accent_theme() on all tabs
```

### Overlap with Story 9.7

Story 9.7 adds OS tree connector widgets (`app/widgets/os_path_tree_group.py`) in Workspace/Artefacts and may further polish Preferences accent labelling. **9.1 owns:** Open removal, `project_reader` deletion, Project-tab accent removal, `ProjectSpec.accent_color` removal, prefs-only theme wiring, architecture doc updates. **Do not** implement tree connectors in 9.1.

### Out of scope (later stories)

| Story | Scope deferred |
|-------|----------------|
| 9.2 | Non-empty destination guard; remove `_confirm_overwrite` |
| 9.5 | User manuals (`docs/user/`), README Open sections, QA checklists |
| 9.6 | Broader test hardening, guard/characteristics tests (9.1 must still leave CI green) |
| 9.3–9.4 | Plugin characteristics, template pipeline |

### Project Structure Notes

- **Layer boundaries (AD-8):** UI changes in `app/`; delete reader from `core/`; no new Qt in `core/`
- **Button bar pattern:** `_make_btn(label, objectName, slot)` + `_make_button_bar([...])` in `main_window.py`
- **Clean code limits:** 15-line functions, 200-line classes — extract if `_on_open` removal leaves dead code paths; do not expand `MainWindow` with new responsibilities
- **No comments policy:** no story/ticket references in code comments
- **Run:** `.venv/bin/python main.py` — never bare `python`
- **Tests:** `.venv/bin/pytest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 9]
- [Source: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §8 Story 9.1, §9.1]
- [Source: _bmad-output/project-context.md — Data Flow, AD-3, AD-5]
- [Source: _bmad-output/architecture.md — Round-trip reload section (to revise)]
- [Source: app/main_window.py — Open + accent wiring]
- [Source: app/pages/project.py — AccentColorSection]
- [Source: core/project_spec.py — accent_color field]
- [Source: core/project_writer.py — _write_sidecar]

## Dev Agent Guardrails

### Technical requirements

1. **Zero reload surface:** After this story, no code path reads `.luthier.json`. Grep gate: `project_reader`, `read_project_result`, `_load_project`, `_on_open`, `Open Project` in `app/` and `core/`.
2. **Write-only sidecar:** Generate must still emit `.luthier.json` with full project metadata **except** `accentColor`.
3. **No migration shims:** Do not add fallback readers for sidecars missing new fields or containing legacy `accentColor` — PO §2.3.
4. **Preferences accent untouched:** `core/preferences.py`, `app/pages/preferences.py`, `core/accent_colors.py` stay as-is (accent lives in profile only).
5. **`ProjectPage.load()` preserved** for Create New + post-generate baseline — do not conflate with Open removal.

### Architecture compliance

| AD | Before (8.2) | After (9.1) |
|----|--------------|-------------|
| AD-1 | `project_reader.read_project()` in contract | Contract: `ProjectPage.spec()` → `ProjectGenerator.generate()` only |
| AD-3 | Sidecar for round-trip; reader sole deserialiser | Sidecar **write-only**; `ProjectWriter` writes; no reader |
| AD-5 | Open/Generate don't write prefs | Unchanged; Open removed |
| AD-8 | Layer boundaries | Unchanged |

Update spine + architecture.md + project-context.md to match.

### Library / framework requirements

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- **Qt patterns:** `repolish()` after QSS objectName changes; `QFileDialog` still used for Choose… dialogs (not Open)
- Remove dead `#OpenButton` QSS — optional but recommended cleanup in `app/theme.py`

### File structure requirements

| File | Action |
|------|--------|
| `app/main_window.py` | Remove Open; simplify accent to prefs-only |
| `app/pages/project.py` | Remove AccentColorSection + accent in spec/load |
| `core/project_spec.py` | Remove `accent_color` |
| `core/project_reader.py` | **Delete** |
| `app/theme.py` | Remove `#OpenButton` styles |
| `_bmad-output/project-context.md` | Update data flow + AD-3 |
| `_bmad-output/architecture.md` | Replace reload section |
| `architecture-spine.md` | Revise AD-1, AD-3, structural seed |
| `tests/unit/test_project_reader.py` | **Delete** |
| `tests/unit/test_core_imports.py` | Remove reader import test |
| `tests/integration/test_round_trip.py` | Rewrite generation-only |
| Other test files | Remove reader/accent-on-spec references (see AC8) |

**Do not modify:** `Templates/`, user manuals (`docs/user/`), README — Story 9.5.

### Testing requirements

**Strategy (AD-6):** unit tests for pure `core/`; integration tests with `tmp_path`; no Qt widget tests.

**Must pass before marking done:**
```bash
.venv/bin/pytest
grep -r "project_reader\|read_project_result" app/ core/ tests/  # only hits in tests being rewritten/deleted
```

**Test changes (minimum):**

| File | Action |
|------|--------|
| `tests/unit/test_project_reader.py` | Delete |
| `tests/unit/test_core_imports.py` | Remove `"core.project_reader"` |
| `tests/unit/test_project_spec.py` | Remove accent round-trip tests |
| `tests/unit/test_project_dirty_guard.py` | Replace accent dirty test |
| `tests/unit/test_project_writer.py` | Assert sidecar lacks `accentColor` |
| `tests/integration/test_round_trip.py` | Generation-only assertions |
| `tests/integration/test_cmake_cross_platform.py` | Drop reader reload checks |
| `tests/integration/test_frozen_bundle.py` | Drop reload check |
| `tests/unit/test_workspace_migration.py` | Remove open-project test |

**Keep unchanged:** `tests/unit/test_preferences.py`, `tests/unit/test_accent_colors.py` (Preferences accent).

**Manual smoke (no automated Qt tests):**
1. Launch app — Project tab shows 2 buttons only
2. Generate project — `.luthier.json` on disk, no `accentColor` key
3. Change accent on Preferences — theme updates on Project tab
4. Create New Project — dirty guard still prompts when form edited

### Git intelligence

Recent commits are README/logo/release-guide polish — no Epic 9 code yet. Patterns from Epic 8 stories (8.1 workspace, 8.2 sidecar-only reader):
- Story files live in `_bmad-output/implementation-artifacts/`
- Tests co-located under `tests/unit/` and `tests/integration/`
- Architecture docs updated in same story as code (8.2 precedent)

### Latest tech information

No new libraries. PySide6 `QFileDialog.getExistingDirectory` remains for **Choose…** folder picks in Workspace/Artefacts — only the Open Project dialog path is removed.

**PyInstaller frozen bundle:** `test_frozen_bundle.py` must not import deleted `project_reader` — update to generation-only assertion.

## Project Context Reference

Key rules from `_bmad-output/project-context.md`:
- Run via `.venv/bin/python main.py`
- AD-5: `preferences.json` written only by Preferences auto-save / Import — never Generate/Open
- Sidecar currently described as read via `project_reader` — **must update** to write-only in this story
- `#OpenButton` orange action button — remove with Open button
- `AccentColorSection` on Preferences stays; Project tab section removed

## Story Completion Status

- **Status:** done
- **Completion note:** Scaffold-only pivot implemented — Open Project removed, `project_reader` deleted, Project-tab accent removed, prefs-only theme, write-only sidecar AD-3 documented, 240 tests pass
- **Next story after dev:** 9.7 (`9-7-ui-accent-preferences-only-os-tree-connectors`) — OS tree connectors + accent polish

## Dev Agent Record

### Agent Model Used

claude-4.6-sonnet-medium-thinking

### Debug Log References

### Completion Notes List

- Removed Open Project UI (`_open_btn`, `_on_open`, `_load_project`) and deleted `core/project_reader.py`
- Removed Project-tab `AccentColorSection`; theme now driven by `prefs.accent_color` (live picker on Preferences tab)
- Removed `accent_color` from `ProjectSpec`; sidecar write-only via existing `ProjectWriter._write_sidecar()`
- Updated architecture docs (project-context, architecture.md, architecture-spine) for write-only AD-3
- Rewrote integration tests to generation-only assertions; deleted `test_project_reader.py`
- Full suite: 240 passed, 3 skipped

### File List

- `app/main_window.py` (modified)
- `app/pages/project.py` (modified)
- `app/theme.py` (modified)
- `core/project_spec.py` (modified)
- `core/project_reader.py` (deleted)
- `tests/unit/test_project_reader.py` (deleted)
- `tests/unit/test_core_imports.py` (modified)
- `tests/unit/test_project_spec.py` (modified)
- `tests/unit/test_project_dirty_guard.py` (modified)
- `tests/unit/test_project_writer.py` (modified)
- `tests/unit/test_workspace_migration.py` (modified)
- `tests/integration/test_round_trip.py` (modified)
- `tests/integration/test_cmake_cross_platform.py` (modified)
- `tests/integration/test_frozen_bundle.py` (modified)
- `_bmad-output/project-context.md` (modified)
- `_bmad-output/architecture.md` (modified)
- `_bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/architecture-spine.md` (modified)
- `_bmad-output/planning-artifacts/epics.md` (modified — Epic 9 planning, review accepted)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)
- `_bmad-output/implementation-artifacts/9-1-remove-open-project-scaffold-only-positioning.md` (modified)

### Change Log

- 2026-07-04: Story 9.1 — scaffold-only pivot: remove Open/reload path, delete project_reader, prefs-only accent, write-only sidecar AD-3
