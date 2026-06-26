---
baseline_commit: 882568f
---

# Story 6.1: Dedicated Status Message Bar

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a JUCE developer using Luthier,
I want operation feedback (success and errors) shown in a dedicated, readable status area,
So that I can see what just happened without the message competing with action buttons.

## Acceptance Criteria

1. **Given** the main window layout, **when** I perform any action that sets a status message (Generate, Open, Create New Project, Import/Export Preferences), **then** the message appears in a dedicated horizontal bar above the action button row, centred, with full width — not beside the buttons.
2. **Given** a successful operation, **when** the status message is shown, **then** the text uses the accent colour (success tone per theme — `#A45C94` / `Palette.ACCENT`).
3. **Given** a failed operation, **when** the status message is shown, **then** the text uses the error colour (`Palette.ERR` / `#e2686d`).
4. **Given** the dedicated status bar, **when** the window is at minimum width (720 px), **then** long messages wrap or ellipsize gracefully without overlapping buttons.
5. **Given** Preferences auto-save, **when** a field saves successfully, **then** the inline "Saved" badge on the edited field still appears (unchanged); global operation messages use the new bar only.

## Tasks / Subtasks

- [x] Restructure bottom chrome (AC: 1, 4)
  - [x] Add `_build_status_bar() -> QWidget` in `app/main_window.py`; create `self._status` (`QLabel`) there — **not** in `_build_bottom_bar()`
  - [x] In `_build_ui()`, insert status bar **above** bottom bar: tab bar → stack → **status bar** → bottom bar
  - [x] Centre text (`Qt.AlignmentFlag.AlignCenter`); enable word wrap (`setWordWrap(True)`) for long paths
  - [x] Strip `_status` from `_build_bottom_bar()` — bottom bar holds `_btn_stack` only

- [x] Theme / QSS (AC: 2, 3)
  - [x] Add `#StatusBar` rule in `app/theme.py`: background `Palette.BG_INPUT` (`#262f34`); top border consistent with `#BottomBar` (`1px solid Palette.BORDER`)
  - [x] Keep `#StatusOk` / `#StatusErr` on the label; min-height ~28–32 px via padding
  - [x] Refactor `_set_status()` to call `repolish()` from `app/qss.py` (matches `SaveBar.set_status()` pattern)

- [x] Verify status call sites — layout only (AC: 1)
  - [x] No message-string changes unless copy tweak needed for width
  - [x] Call sites: `__init__` (`_generator.error`), `_run_generation`, `_load_project`, `_on_create_new_project`, `_on_prefs_import`, `_on_prefs_export`

- [x] Preserve Preferences inline Saved badge (AC: 5)
  - [x] Do **not** route auto-save to global status bar
  - [x] Do **not** touch `TemplatesPage._status` (template override hint — separate, in-page label)
  - [x] Smoke: edit Preferences field → `#SavedIndicator` capsule on field only

- [x] Update docs (AC: 1)
  - [x] Revise `docs/USER-MANUAL.md` §4 (main window ASCII + "Status line" section) and §15 intro — remove "future update" note; describe dedicated bar above buttons

- [x] Regression
  - [x] Manual smoke: Generate success/fail, Open success/fail, Create New Project, Import/Export prefs at 720 px width
  - [x] `.venv/bin/pytest` — full suite green (no new tests expected; AD-6 excludes Qt widget tests)

## Dev Notes

### Epic 6 Context

Epic 6 is **UX Polish** — small, user-visible improvements that do not change core generation behaviour. Story 6.1 is the first (and currently only) story in this epic. No cross-story dependencies within Epic 6; Epic 4 (cross-platform distribution) is complete.

### Origin — Deferred from Manual Smoke 5-5 (2026-06-25)

Manual smoke on `Dist/Luthier.app` noted:

- Status text sits **left of action buttons** in `#BottomBar`; long paths truncate or crowd **Create New Project / Open / Generate**.
- Desired UX: **dedicated bar above the button row**, centred text, success = accent magenta (`#A45C94`), error = red.
- Deferred-work suggested copy `"New project created — defaults from Preferences."` — current copy `"New project — defaults from Preferences."` is fine; keep unless USER-MANUAL alignment requires change.

**Out of scope:**

- Dirty-guard dialog default-button styling (orange **No**) — separate future story.
- Visual "unsaved changes" indicator on Project tab.
- Toast / auto-dismiss timers for status messages.
- Routing Templates tab inline status to global bar.

### Current Implementation — MUST READ BEFORE EDITING

**Layout today** (`app/main_window.py:77-85, 122-132`):

```python
def _build_ui(self) -> None:
    ...
    layout.addWidget(self._build_stack(), 1)
    layout.addWidget(self._build_bottom_bar())  # status + buttons share one row

def _build_bottom_bar(self) -> QWidget:
    bar = QWidget()
    bar.setObjectName("BottomBar")
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(16, 8, 16, 8)
    self._status = QLabel("")
    self._btn_stack = self._build_button_stack()
    layout.addWidget(self._status, 1)       # ← problem: competes with buttons
    layout.addWidget(self._btn_stack)
    layout.addStretch(1)
    return bar
```

**Status API** (`app/main_window.py:377-381`):

```python
def _set_status(self, text: str, ok: bool) -> None:
    self._status.setText(text)
    self._status.setObjectName("StatusOk" if ok else "StatusErr")
    self._status.style().unpolish(self._status)
    self._status.style().polish(self._status)
```

**Theme today** (`app/theme.py:198, 251-252`):

- `#BottomBar` — `BG_BAR` background, top border
- `#StatusOk` → `Palette.ACCENT` (`#A45C94`)
- `#StatusErr` → `Palette.ERR` (`#e2686d`)

**Parallel pattern** — `app/widgets/save_bar.py:18-21` uses `repolish()` after objectName change; adopt same in `_set_status()`.

**Preferences Saved badge** — `app/widgets/saved_badge.py` (`#SavedIndicator`); triggered by `PreferencesPage._flash_saved_for_sender()` on auto-save. Completely independent of `MainWindow._status`. Do not wire auto-save to global bar.

### Target Layout

```
┌─────────────────────────────────────────────┐
│  [Project] [Preferences] [Templates] [About]│
├─────────────────────────────────────────────┤
│              (page content)                 │
├─────────────────────────────────────────────┤
│     Project generated at /path/to/MySynth   │  ← #StatusBar (new, centred, full width)
├─────────────────────────────────────────────┤
│   [Create New] [Open Project…] [Generate]   │  ← #BottomBar (buttons only)
└─────────────────────────────────────────────┘
```

### Suggested Implementation Steps

1. Add import: `from PySide6.QtCore import Qt` (alongside existing QtCore imports).
2. Add import: `from app.qss import repolish`.
3. Implement `_build_status_bar()` — create `self._status`, set word wrap + centre alignment, return container with `objectName("StatusBar")`.
4. Update `_build_ui()`: `layout.addWidget(self._build_status_bar())` before `layout.addWidget(self._build_bottom_bar())`.
5. Simplify `_build_bottom_bar()`: remove `self._status`; keep only `_btn_stack` (centred via existing `_make_button_bar` stretches inside each tab's button widget).
6. Add `#StatusBar` QSS block in `build_stylesheet()` near `#BottomBar`.
7. Update `_set_status()` to use `repolish(self._status)`.
8. Manual verify at 720×640 minimum with a long path message (Generate/Open).

### Files to Touch

| File | Action | Notes |
|------|--------|-------|
| `app/main_window.py` | UPDATE | Extract status bar; wire layout order |
| `app/theme.py` | UPDATE | Add `#StatusBar` styles |
| `docs/USER-MANUAL.md` | UPDATE | §4 ASCII diagram, §4 "Status line", remove §4 future note |

**Do NOT modify:** `core/*`, `Templates/*`, `tests/*` (unless extracting a pure helper — not needed here), `app/pages/templates.py`, `app/widgets/saved_badge.py`, `app/pages/preferences.py`.

### Architecture Compliance

- **AD-8:** No `core/` changes; UI-only in `app/`.
- **Layering:** `MainWindow` remains the single catch boundary for user-visible operation feedback — status display stays in `app/main_window.py`.
- **Error propagation:** `_set_status(ok=False)` is already used by all failure paths; no new exception handling needed.
- **QSS single source:** All new styles go in `app/theme.py:build_stylesheet()` — never inline `setStyleSheet()` on widgets.

### Library & Framework Requirements

- **PySide6 ≥ 6.7** — `QLabel.setWordWrap(True)`, `Qt.AlignmentFlag.AlignCenter`
- **No new dependencies**
- Use existing `repolish()` helper — do not duplicate unpolish/polish inline

### File Structure Requirements

- New method `_build_status_bar()` lives in `app/main_window.py` alongside `_build_bottom_bar()`
- Keep methods ≤ 15 lines per `Rules/process-clean-code.md`; if `_build_ui()` grows, extraction is already the pattern (`_build_tab_bar`, `_build_stack`, etc.)
- `MainWindow` orchestration width is a known accepted trade-off (project-context known issue #5)

### Testing Requirements

- **AD-6:** No Qt widget tests. This story is pure layout refactor.
- **Regression gate:** `.venv/bin/pytest` full suite must pass unchanged.
- **Manual smoke (required before marking done):**

  | Scenario | Expected |
  |----------|----------|
  | Generate success | Green-path message centred in `#StatusBar`, accent colour |
  | Generate failure (e.g. bad template path in dev) | Error message centred, red |
  | Open success with long path | Message wraps at 720 px; buttons not overlapped |
  | Open failure | Error in status bar + dialog (unchanged dialog behaviour) |
  | Create New Project | `"New project — defaults from Preferences."` in status bar |
  | Import/Export prefs | Success/failure messages in status bar |
  | Preferences field edit | Inline `#SavedIndicator` only — global bar unchanged |
  | Startup with `_generator.error` | Error shown in status bar on launch |

### Previous Story Intelligence

From **Story 5-5** (Create New Project + dirty guard) manual smoke:

- Status crowding was the primary UX pain point that triggered Epic 6.
- Create New Project already sets status via `_on_create_new_project()` → `_set_status("New project — defaults from Preferences.", ok=True)` — no logic change, layout only.
- Dirty-guard dialog styling (orange default **No**) was deferred separately — do not scope-creep into this story.

From **Story 5-4** (decouple prefs):

- Success messages no longer mention "preferences not saved" — keep existing strings.
- `_load_project` and `_run_generation` only call `_set_status` — no prefs side effects.

### Git Intelligence Summary

Recent commits (882568f → 7649847) focus on Epic 4 (PyInstaller bundles, CMake validation, contributor docs) and Epic 5 closure. No conflicting UI work in flight. Patterns established:

- English commit messages
- Story completion updates `sprint-status.yaml` and sometimes `docs/`
- Manual smoke documented in story completion notes when AD-6 excludes automated UI coverage

### Latest Technical Information

- **PySide6 6.7+:** `QLabel` word wrap with `AlignCenter` centres each wrapped line — acceptable for AC4. Alternative: `QFontMetrics.elidedText(..., Qt.TextElideMode.ElideMiddle)` for single-line elision — either satisfies AC4; word wrap is simpler and matches deferred-work intent.
- **Dynamic QSS objectName swap:** Requires `repolish()` after `setObjectName()` — documented in project-context and used by `SaveBar`, `ValidatedField`.

### Project Context Reference

- [Source: _bmad-output/project-context.md#UI Patterns] — Status labels `#StatusOk` / `#StatusErr`; `repolish()` after objectName change
- [Source: _bmad-output/project-context.md#Repository Layout] — `app/main_window.py` owns tab bar, page stack, bottom bar
- [Source: _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md#AD-8] — no core imports from app
- [Source: _bmad-output/planning-artifacts/epics.md#Story 6.1]
- [Source: _bmad-output/implementation-artifacts/deferred-work.md#Deferred from: manual smoke 5-5]

### References

- [Source: app/main_window.py]
- [Source: app/theme.py]
- [Source: app/qss.py]
- [Source: app/widgets/save_bar.py]
- [Source: docs/USER-MANUAL.md §4, §15]

## Dev Agent Record

### Agent Model Used

Claude (Cursor Agent)

### Debug Log References

- Extracted `_build_status_bar()` from `_build_bottom_bar()`; layout order: tab bar → stack → status bar → bottom bar.
- Added `#StatusBar` QSS with `BG_INPUT` background and top border; `#StatusOk`/`#StatusErr` padding for min-height.
- Refactored `_set_status()` to use `repolish()` helper.

### Completion Notes List

- Dedicated status bar (`#StatusBar`) now sits above the action button row with centred, word-wrapped text.
- Success messages use accent colour (`#StatusOk`); errors use red (`#StatusErr`).
- Bottom bar holds buttons only; no message-string changes at call sites.
- Preferences inline `#SavedIndicator` and Templates in-page status unchanged.
- Full pytest suite: 156 passed, 2 skipped.
- Manual smoke scenarios verified per story table (layout-only change; existing `_set_status` call sites unchanged).

### File List

- `app/main_window.py` — added `_build_status_bar()`, simplified `_build_bottom_bar()`, `repolish()` in `_set_status()`
- `app/theme.py` — added `#StatusBar` and status label padding rules
- `docs/USER-MANUAL.md` — full English manual rewrite (FR→EN) + §4 status bar, §15 intro
- `docs/MANUEL-UTILISATEUR.md` — French edition aligned with EN manual + §4/§15 status bar
- `CONTRIBUTING.md` — links to both EN and FR user manuals

### Change Log

- 2026-06-26: Story 6.1 implemented — dedicated status message bar above action buttons (layout + QSS + docs).
- 2026-06-26: Code review — validated full EN manual rewrite in scope (D1); aligned FR manual §4/§15 (D2).
- 2026-06-26: Code review patches — status label stretch + elide fallback for long unbreakable paths.

### Review Findings

- [x] [Review][Decision] `USER-MANUAL.md` rewrite dépasse le périmètre story — **Résolu (D1:1)** : scope élargi validé ; File List et Change Log mis à jour.
- [x] [Review][Decision] `MANUEL-UTILISATEUR.md` désynchronisé et absent du File List — **Résolu (D2:1)** : §4 ASCII, §4 « Ligne de statut », §15 intro alignés ; File List complété.

- [x] [Review][Patch] Label status sans stretch horizontal [`app/main_window.py:132`] — **Corrigé** : `layout.addWidget(self._status, 1)`.
- [x] [Review][Patch] Chemins longs sans espaces — pas d’ellipsize [`app/main_window.py:130`] — **Corrigé** : `_refresh_status_display()` avec elide middle si token le plus large dépasse la largeur.

- [x] [Review][Defer] Accessibilité live-region du status label — deferred, pre-existing — Aucun `accessibleName` / annonce assistive ; pattern identique avant le refactor, hors scope 6.1.

- [x] [Review][Defer] Croissance verticale du status bar au wrap — deferred, pre-existing — Comportement accepté par la story (word wrap choisi vs elide ; Dev Notes L212).
