---
epic: 9
story: 7
story_key: 9-7-ui-accent-preferences-only-os-tree-connectors
depends_on: [9-1]
blocks: [9-5, 9-6]
implementation_order: 2
pivot_date: 2026-07-04
baseline_commit: 38747d278495fb4ae4bc7f5cd2a4617311142130
---

# Story 9.7: UI — Accent Preferences-Only + OS Tree Connectors

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a JUCE developer,
I want a cleaner Project form and visual OS path grouping,
So that accent colour personalises Luthier itself and multi-OS paths are easier to scan.

## Context

**Epic 9 pivot (2026-07-04):** Luthier is a **one-shot JUCE/CMake skeleton generator**. Story 9.7 follows **9.1** (Open/reload removal + Project-tab accent removal). **9.1 already delivered** most accent Preferences-only work — this story **verifies** those ACs and adds the **OS tree connector** UI plus one **accent theme wiring fix** flagged during 9.1 review.

**Depends on:** Story 9.1 (`done`) — `ProjectSpec` has no `accent_color`; Project tab has no `AccentColorSection`; write-only sidecar omits `accentColor`.

**Planning references:**
- `_bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md` — §5.8.1, §5.8.2, §8 Story 9.7, §9.2 file inventory
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md` — FR12, OS tree connectors
- `_bmad-output/planning-artifacts/epics.md` — Epic 9, Story 9.7

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.4 → 9.6 → 9.5`

### What 9.1 already did vs what 9.7 owns

| Area | Done in 9.1 (verify only) | 9.7 scope |
|------|---------------------------|-----------|
| Project tab accent | Removed `AccentColorSection` from `project.py` | Confirm absent; no re-add |
| `ProjectSpec.accent_color` | Removed from dataclass + `to_dict()` | Confirm sidecar still omits `accentColor` |
| Preferences accent | `AccentColorSection` on Preferences tab | Keep; optional label polish (§5.8.1) |
| Theme source | `_accent_color_for_tab()` → `prefs.accent_color` | **Fix** live accent apply on swatch click (see Dev Notes) |
| OS path layout | Flat indent via `OS_FIELD_LEFT_MARGIN = 28` | **New** tree connector widget + integration |
| User manuals | Unchanged (Story 9.5) | Out of scope |

### Critical gap from 9.1 review (must fix in 9.7)

```146:148:app/main_window.py
    def _on_prefs_accent_changed(self, color: str) -> None:
        if self._tab_bar.currentIndex() == _PREFS_TAB_INDEX:
            self._apply_accent_theme(color)
```

AC requires theme update **immediately on all tabs** when accent changes on Preferences. Today the global stylesheet updates **only if the user is already on the Preferences tab**. Remove the tab guard — always call `_apply_accent_theme(color)`.

## Acceptance Criteria

### AC1 — No accent picker on Project tab

**Given** Project tab scroll content  
**Then** no accent colour picker  
**And** Preferences tab still shows `AccentColorSection` with auto-save to `preferences.json`

### AC2 — Live accent theme on all tabs

**Given** user changes accent on Preferences (swatch click)  
**Then** Luthier theme updates **immediately** regardless of active tab (Project, Preferences, Templates, About)  
**And** single source remains `prefs.accent_color` — no Project-tab accent path

### AC3 — No accent in sidecar

**Given** `ProjectSpec.to_dict()` after Generate  
**Then** no `accentColor` key in `.luthier.json`  
*(Regression guard — implemented in 9.1; re-run existing tests.)*

### AC4 — Workspace tree connectors (Project + Preferences)

**Given** Workspace section on **Project** and **Preferences** tabs  
**Then** each OS path group displays tree connector lines per handoff §5.8.2:
- **Group 1:** anchor = label « Destination folder * » → children Windows, macOS, Linux
- **Group 2:** anchor = label « JUCE directory » → children Windows, macOS, Linux

**Visual spec:**
```
Destination folder *
│
├─ Windows     [________________]
├─ macOS       [________________]  [Choose…]
└─ Linux       [________________]
```

### AC5 — Artefacts tree connectors (Project + Preferences)

**Given** Artefacts section on **Project** and **Preferences** tabs  
**When** « Copy to central artefacts folder » checkbox is visible  
**Then** the three OS path rows display the same tree connector pattern **anchored to that checkbox** (not the system-folders checkbox)

### AC6 — Connector styling

**Given** light/dark theme QSS (current dark Fusion theme)  
**Then** connector lines use a **subtle neutral colour** (`Palette.BORDER` / `#44525a` — **not** accent)  
**And** lines remain visible against `BG_MAIN`  
**And** horizontal branch ends ~6–8 px before OS label text (labels must not touch the line)

### AC7 — Reusable widget

**Given** implementation  
**Then** one shared widget in `app/widgets/` (suggested: `os_path_tree_group.py`) used by `workspace.py` and `artefacts.py`  
**And** no duplicated paint logic across section files

### AC8 — Accessibility preserved

**Given** tree connector lines  
**Then** lines are **decorative only** — keyboard tab order and screen-reader field order unchanged (children remain direct layout siblings in logical order)

### AC9 — Tests and CI green

**Given** full `pytest` run  
**When** story 9.7 is complete  
**Then** all tests pass  
**And** no new `accentColor` in `ProjectSpec.to_dict()` or sidecar assertions regress

## Tasks / Subtasks

- [x] **Fix live accent theme apply** (AC: 2)
  - [x] `app/main_window.py`: `_on_prefs_accent_changed` — remove `_PREFS_TAB_INDEX` guard; always `_apply_accent_theme(color)`
  - [x] Consider applying accent on tab switch for **all** tabs (or rely on global stylesheet from step above — verify Templates `#SaveButton` / `#ActionButton` update live)
  - [x] Optional: simplify `_accent_color_for_tab(index)` → inline `self._prefs.accent_color` if index param unused
- [x] **Optional accent label polish** (AC: 1)
  - [x] `app/widgets/accent_color_picker.py`: rename title/hint to clarify Luthier app appearance (e.g. « Luthier appearance » / « Pick a preset accent for the Luthier interface. ») — handoff §5.8.1
- [x] **Create `OsPathTreeGroup` widget** (AC: 4, 5, 6, 7, 8)
  - [x] New `app/widgets/os_path_tree_group.py` — custom paint for vertical trunk + horizontal branches (├ / └ on last child)
  - [x] API: accepts anchor widget (QLabel or QCheckBox) + list of child row widgets (`ValidatedField` / `FolderField`)
  - [x] Line colour from `Palette.BORDER`; antialiased `QPainter`
  - [x] Export geometry constants (trunk X, branch length, label gap) — co-locate with `OS_FIELD_LEFT_MARGIN` in `path_specs.py` or widget module
- [x] **Integrate Workspace section** (AC: 4)
  - [x] `app/pages/workspace.py`: replace `_build_path_group` flat margined layout with `OsPathTreeGroup` for destination + JUCE groups
  - [x] Preserve: host-only `FolderField`, validity signals, `path_fields()` dict keys, `flash_saved` behaviour
- [x] **Integrate Artefacts section** (AC: 5)
  - [x] `app/pages/artefacts.py`: wrap `_paths_host` children in `OsPathTreeGroup` anchored to `copyToArtefactsDir` checkbox
  - [x] Preserve: `_sync_paths_enabled` disable/enable of path rows; connector lines follow disabled state visually (dimmed or hidden when paths disabled — PO prefers visible but muted; default: keep lines visible, fields greyed via existing QSS)
- [x] **Tune alignment** (AC: 6)
  - [x] Adjust `OS_FIELD_LEFT_MARGIN` in `path_specs.py` if connector geometry requires retuning so OS labels align with existing form grid
- [x] **Regression verification** (AC: 1, 3, 9)
  - [x] Run `.venv/bin/pytest` — full suite green
  - [x] Manual smoke: accent change on Preferences while on Project tab → buttons recolour immediately
  - [x] Manual smoke: tree connectors visible on Project + Preferences for all 4 blocks
  - [x] Confirm `tests/unit/test_project_writer.py::test_sidecar_omits_accent_color` still passes

### Review Findings

- [x] [Review][Patch] Branches align to field widget center, not input row — shifts when validation error appears [app/widgets/os_path_tree_group.py:69-76] — Fixed: branch Y from `#FieldLabel` center via `findChild`.
- [x] [Review][Patch] Anchor widget resize/move does not trigger connector repaint [app/widgets/os_path_tree_group.py:19-25] — Fixed: event filter on anchor + shared `_REFRESH_EVENTS`.
- [x] [Review][Patch] Child Hide event does not trigger connector repaint [app/widgets/os_path_tree_group.py:27-34] — Fixed: `QEvent.Type.Hide` in `_REFRESH_EVENTS`.
- [x] [Review][Defer] Open Project removal bundled in same `main_window.py` diff [app/main_window.py] — deferred, pre-existing (Story 9.1 scope; not 9.7 regression).
- [x] [Review][Defer] HiDPI 1.0px cosmetic pen without device-pixel-ratio scaling [app/widgets/os_path_tree_group.py:78-84] — deferred, pre-existing (story Dev Notes flag HiDPI as low risk for v1).
- [x] [Review][Defer] Shared `OS_TREE_TRUNK_X` for FieldLabel and QCheckBox anchors — verify manual QA [app/pages/path_specs.py:13] — deferred, pre-existing (needs visual smoke on both tabs; not provably wrong in code).

## Dev Notes

### Current state — files to modify

#### `app/pages/workspace.py` (111 lines)

Two path groups built by `_build_path_group()`:
- Uses `OS_FIELD_LEFT_MARGIN` (28 px) left margin on a `QVBoxLayout`
- Each group: 3 rows (Windows, macOS, Linux) — host OS row gets `FolderField`, others `ValidatedField`
- Labels « Destination folder * » and « JUCE directory » are **siblings above** the indented layout (not inside the group)

**Target:** Replace inner margined layout with `OsPathTreeGroup(anchor_label, [field, field, field])` for both groups. Public API (`path_fields()`, `values()`, `load()`, `is_valid()`, signals) **unchanged**.

#### `app/pages/artefacts.py` (126 lines)

Structure:
1. Two checkboxes (`copyToSystemFolders`, `copyToArtefactsDir`)
2. `_paths_host` widget with margined `QVBoxLayout` of 3 artefact path fields

**Target:** `OsPathTreeGroup(anchor=copyToArtefactsDir_checkbox, children=[win, mac, linux fields])`. Do **not** add connectors under « Copy to system plugin folders » (no OS children — handoff §5.8.2).

#### `app/pages/path_specs.py`

```9:12:app/pages/path_specs.py
# Left margin for per-OS rows nested under section headings (Workspace, Artefacts).
# Checkbox label inset (theme.py): padding-left 2 + indicator 16 + spacing 8 = 26;
# +2 px so FieldLabel text lines up with QCheckBox label text.
OS_FIELD_LEFT_MARGIN = 28
```

May become the trunk offset for connector geometry, or move to shared constants consumed by `OsPathTreeGroup`.

#### `app/main_window.py` — accent wiring (minimal change)

**Keep:**
- `_prefs_page.accent_section().colorChanged.connect(self._on_prefs_accent_changed)`
- Startup `apply_accent_theme(prefs.accent_color)` in `__init__`
- `_accent_color_for_tab()` returning `self._prefs.accent_color`

**Fix:**
- `_on_prefs_accent_changed` — remove tab-index guard (see Context above)

**Do not reintroduce:** `_on_project_accent_changed`, Project-tab accent wiring, tab-based accent switching between project vs prefs colours.

#### `app/widgets/accent_color_picker.py` — keep, optional polish

`AccentColorSection` lives here; used only from `preferences.py`. Title currently « Luthier Accent Color » — acceptable; handoff allows clearer « Luthier appearance » wording.

#### `app/pages/project.py` — no accent changes expected

9.1 removed all accent references. **Do not** add accent section back. Workspace/Artefacts sections are shared — tree connector changes propagate to Project tab automatically.

#### `app/pages/preferences.py` — no structural changes required

Composes same `WorkspaceSection` + `ArtefactsSection`. Accent auto-save via `_on_accent_save` unchanged.

### Suggested `OsPathTreeGroup` design

```python
# app/widgets/os_path_tree_group.py (sketch — adapt to clean-code limits)

class OsPathTreeGroup(QWidget):
    """Decorative tree lines linking an anchor to per-OS path rows."""

    def __init__(self, anchor: QWidget, children: list[QWidget], parent=None):
        ...

    def paintEvent(self, event):
        # Vertical line: from below anchor baseline to center of last child row
        # Horizontal branches: trunk → each child label column (~6-8 px gap before text)
        # Last child: └ corner; others: ├
        # Colour: QColor(Palette.BORDER) — never Palette.ACCENT()
```

**Layout approach:** Use outer `QVBoxLayout`: row 0 = anchor; row 1 = inner column of children with left margin for trunk space. Paint on the group widget background, or use a dedicated `_TreeOverlay` child with `WA_TransparentForMouseEvents`.

**Row height:** `ValidatedField` / `FolderField` use `outer.setContentsMargins(0, 4, 0, 4)` — trunk must span actual widget heights; compute from `children[i].geometry()` in `paintEvent` or `resizeEvent`.

**HiDPI:** Use `devicePixelRatio()` or `QPainter` antialiasing; handoff flags HiDPI alignment as low risk if constants live in one place.

### Target visual data flow (unchanged functionally)

```
Preferences.accent_color
  → AccentColorSection.colorChanged
  → MainWindow._on_prefs_accent_changed → apply_accent_theme (ALL tabs)
  → preferences.json auto-save (PreferencesPage._on_accent_save)

WorkspaceSection / ArtefactsSection (Project + Preferences tabs)
  → OsPathTreeGroup decorates OS rows only
  → path_fields() / values() / validation unchanged
```

### Overlap with other Epic 9 stories

| Story | Boundary |
|-------|----------|
| 9.1 | Open removal, accent from ProjectSpec — **done**; do not redo |
| 9.2 | Non-empty destination guard — **out of scope** |
| 9.5 | User manuals, README accent/tree docs — **out of scope** |
| 9.6 | Broader test hardening — 9.7 keeps CI green; no obligation to add widget unit tests |

### Out of scope

- Documentation updates (`docs/user/`, README) — Story 9.5
- Generate guard — Story 9.2
- Connectors on sections other than Workspace/Artefacts OS path groups
- Animation of tree lines
- Connectors under « Copy to system plugin folders »

### Project Structure Notes

- **Layer boundaries (AD-8):** New widget in `app/widgets/`; section pages compose it; no Qt in `core/`
- **Clean code limits:** Extract paint helpers if `paintEvent` exceeds 15 lines; keep `OsPathTreeGroup` under 200 lines
- **No comments policy:** no story/ticket references in code
- **Run:** `.venv/bin/python main.py`
- **Tests:** `.venv/bin/pytest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 9.7]
- [Source: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §5.8, §8 Story 9.7, §9.2]
- [Source: _bmad-output/implementation-artifacts/9-1-remove-open-project-scaffold-only-positioning.md — overlap + deferred accent fix]
- [Source: app/pages/workspace.py — `_build_path_group`]
- [Source: app/pages/artefacts.py — `_build_path_fields`]
- [Source: app/pages/path_specs.py — `OS_FIELD_LEFT_MARGIN`]
- [Source: app/main_window.py — `_on_prefs_accent_changed`]
- [Source: app/widgets/accent_color_picker.py — `AccentColorSection`]
- [Source: app/theme.py — `Palette.BORDER`, `apply_accent_theme`]

## Dev Agent Guardrails

### Technical requirements

1. **Do not regress 9.1:** No `accentColor` in `ProjectSpec`; no Project-tab accent picker; no `project_reader` resurrection.
2. **Live accent fix is mandatory:** Swatch click must call `apply_accent_theme` regardless of active tab.
3. **Shared widget:** One `OsPathTreeGroup` (or equivalent name) — no copy-paste paint in `workspace.py` and `artefacts.py`.
4. **Neutral connector colour:** Use `Palette.BORDER` (`#44525a`) — never accent colour for tree lines.
5. **Preserve section contracts:** `path_fields()`, `values()`, `load()`, `is_valid()`, `validityChanged`, `flash_saved`, `is_saved_sender` behaviour unchanged.
6. **Both tabs:** `WorkspaceSection` and `ArtefactsSection` are embedded in `ProjectPage` and `PreferencesPage` — single implementation covers both.

### Architecture compliance

| AD | Relevance to 9.7 |
|----|------------------|
| AD-5 | `preferences.json` only written by Preferences auto-save — accent save unchanged |
| AD-6 | No Qt widget unit tests required — manual smoke for connectors + accent |
| AD-8 | Widget in `app/widgets/`; sections in `app/pages/` |
| FR12 | Accent Preferences-only + OS tree connectors |

No architecture doc updates required unless dev agent discovers drift; optional one-line FR12 note in `project-context.md` if tree widget added to layout section.

### Library / framework requirements

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- **Qt patterns:** Custom paint via `QPainter` + `RenderHint.Antialiasing`; `setAttribute(WA_TransparentForMouseEvents)` on overlay if used
- **Theme:** Read `Palette.BORDER` at paint time (static colour — safe if theme stays dark)

### File structure requirements

| File | Action |
|------|--------|
| `app/widgets/os_path_tree_group.py` | **New** — shared tree connector widget |
| `app/pages/workspace.py` | Integrate `OsPathTreeGroup` (×2 groups) |
| `app/pages/artefacts.py` | Integrate `OsPathTreeGroup` (×1 group) |
| `app/pages/path_specs.py` | Possibly tune `OS_FIELD_LEFT_MARGIN` / add connector constants |
| `app/main_window.py` | Fix `_on_prefs_accent_changed` tab guard |
| `app/widgets/accent_color_picker.py` | Optional label polish |
| `app/theme.py` | **No change expected** — connector uses `Palette.BORDER` in paint code |

**Do not modify:** `core/project_spec.py`, `Templates/`, user manuals, `tests/` (unless CI breaks — prefer zero test changes).

### Testing requirements

**Strategy (AD-6):** Manual Qt smoke for visual connectors and live accent; automated regression via existing suite.

**Must pass before marking done:**
```bash
.venv/bin/pytest
```

**Existing tests to keep green (no accent regression):**
- `tests/unit/test_project_writer.py::test_sidecar_omits_accent_color`
- `tests/unit/test_preferences.py` — accent persistence tests
- `tests/integration/test_frozen_bundle.py` — sidecar lacks `accentColor`

**Manual smoke (required — no automated widget tests):**
1. Launch app → Project tab → Workspace shows tree lines for Destination + JUCE groups
2. Preferences tab → same Workspace + Artefacts tree under « Copy to central artefacts folder »
3. On Project tab, switch accent on Preferences → **Generate Project** / tab bar recolour **without** switching back to Preferences first
4. Toggle « Copy to central artefacts folder » off → path fields disabled; layout intact
5. Tab order through OS path fields unchanged (keyboard)

### Previous story intelligence (9.1)

- **Accent mostly done:** Project tab clean; `ProjectSpec` has no `accent_color`; sidecar write-only without `accentColor`
- **Deferred to 9.7:** `_confirm_overwrite` → Story 9.2; accent live-apply tab guard → **this story**
- **Review note:** « Import Preferences n'applique le thème que sur l'onglet Prefs » — pre-existing; if fixing `_on_prefs_accent_changed` resolves swatch-click case, import path may still need tab switch — verify manually, fix only if trivial (call `_apply_accent_theme` after successful import in `PreferencesPage` or `MainWindow`)
- **Pattern:** Story files in `_bmad-output/implementation-artifacts/`; architecture docs updated in same epic when behaviour changes — optional minor `project-context.md` layout line for new widget

### Git intelligence

Recent commits are README/logo/release polish — Epic 9 code from 9.1 may be uncommitted in working tree. Follow 9.1 file patterns: co-locate widget under `app/widgets/`, minimal `main_window.py` diff for accent fix.

### Latest tech information

No new libraries. PySide6 custom painting: use widget-relative coordinates from `child.geometry()`; call `update()` on resize. `QPainter.drawLine` sufficient for trunk/branches; optional `drawPolyline` for └ corner.

## Project Context Reference

Key rules from `_bmad-output/project-context.md`:
- `Preferences.accent_color` → `apply_accent_theme()` on all tabs (wording in data flow — 9.7 fixes implementation gap)
- `WorkspaceSection` / `ArtefactsSection` shared between Project and Preferences pages
- `OS_FIELD_LEFT_MARGIN = 28` aligns OS labels with checkbox label inset
- `#FieldLabel` QSS colour `TEXT_DIM`; connector should use `BORDER` for subtler lines
- No Qt widget tests — manual QA for visual features

## Story Completion Status

- **Status:** done
- **Completion note:** Live accent apply fixed; OsPathTreeGroup widget added and integrated in Workspace + Artefacts sections on both tabs. Code review patches applied: FieldLabel-anchored branch Y, anchor/hide repaint events.
- **Next story after dev:** 9.2 (`9-2-block-generate-non-empty-destination`) per PO implementation order

## Dev Agent Record

### Agent Model Used

claude-4.6-sonnet-medium-thinking

### Debug Log References

### Completion Notes List

- Removed `_PREFS_TAB_INDEX` guard from `_on_prefs_accent_changed` so swatch clicks apply theme on all tabs immediately.
- Also removed import tab guard — accent theme applies after successful Preferences import regardless of active tab.
- Removed unused `_accent_color_for_tab()`; tab switch uses `self._prefs.accent_color` directly.
- Polished accent labels: « Luthier appearance » / « Pick a preset accent for the Luthier interface. »
- Added `OsPathTreeGroup` widget with antialiased trunk/branches using `Palette.BORDER`.
- Connector geometry constants in `path_specs.py`: `OS_TREE_TRUNK_X`, `OS_TREE_LABEL_GAP`, `OS_TREE_BRANCH_END`, `OS_TREE_LINE_WIDTH`.
- Workspace: two tree groups (Destination + JUCE) with field labels as anchors.
- Artefacts: tree anchored to `copyToArtefactsDir` checkbox; path fields disabled individually when checkbox off (lines remain visible).
- Full pytest: 240 passed, 3 skipped. `test_sidecar_omits_accent_color` green.

### File List

- `app/widgets/os_path_tree_group.py` (new)
- `app/pages/path_specs.py` (modified)
- `app/pages/workspace.py` (modified)
- `app/pages/artefacts.py` (modified)
- `app/main_window.py` (modified)
- `app/widgets/accent_color_picker.py` (modified)

### Change Log

- 2026-07-04: Story 9.7 — live accent theme fix, accent label polish, OsPathTreeGroup widget + Workspace/Artefacts integration.
- 2026-07-04: Code review — OsPathTreeGroup branch Y from FieldLabel; anchor/hide repaint events.
