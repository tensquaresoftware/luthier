---
epic: 9
story: 3
story_key: 9-3-decoupled-plugin-characteristics-and-projectspec
depends_on: [9-1, 9-7, 9-2]
blocks: [9-4, 9-6]
implementation_order: 4
pivot_date: 2026-07-04
baseline_commit: a09f879
note: Story 9.2 generate-guard may be uncommitted locally — ensure 9.2 is done before dev; full pytest green expected at start
---

# Story 9.3: Decoupled Plugin Characteristics and ProjectSpec

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a JUCE developer,
I want Projucer-like plugin characteristic toggles independent of the type preset,
So that I can configure cases like Instrument + MIDI Output (Matrix-Control) without being locked to fixed flags.

## Context

**Epic 9 pivot (2026-07-04):** Luthier is a **one-shot JUCE/CMake skeleton generator**. Stories **9.1**, **9.7**, and **9.2** precede this work — Open/reload removed, accent Preferences-only, OS tree connectors shipped, Generate hard-blocked on non-empty destination.

**FR11:** Plugin type uses **presets + independent characteristic toggles** (Synth, MIDI In/Out, MIDI Effect, keyboard focus), Audio I/O preset combo, MIDI channel counts, and Plugin Description — persisted in `.luthier.json` for reference only.

**Planning references:**
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md` — §5 F1 Plugin Characteristics
- `_bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md` — §5.2–5.5, §8 Story 9.3, §9.3 file inventory
- `_bmad-output/planning-artifacts/epics.md` — Epic 9, Story 9.3

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.4 → 9.6 → 9.5`

### What changes vs what stays

| Area | Change (9.3) | Defer to 9.4 |
|------|--------------|--------------|
| `ProjectSpec` | 9 new fields + `to_dict` / `from_dict` | — |
| Plugin Type UI | Preset radios **+** characteristic checkboxes, Audio I/O combo, MIDI count combos, description field | — |
| `plugin_settings.py` | `flags_for_type` → **preset defaults only**; add validation helpers | `render_context` still uses old path until 9.4 refactors it |
| `render_context.py` | **Do not change** in 9.3 | Map spec fields → CMake `TRUE`/`FALSE`, DESCRIPTION, VST counts |
| `Templates/` | **Do not change** in 9.3 | CMakeLists + PluginProcessor bus variants |
| Generate output | Sidecar gains new keys; **CMake flags unchanged** until 9.4 | Matrix-Control compiles after 9.4 |

### Critical distinction for dev agent

Today `plugin_type` alone drives generation via `render_context.build_context()` → `plugin_settings.flags_for_type(d["pluginType"])`. Story **9.3** decouples **form state** from that coupling — users can set Instrument + MIDI Output in the UI and sidecar, but **generated CMake still reflects preset-only flags** until Story **9.4** wires the template pipeline. Do **not** half-update `render_context` in 9.3 (scope creep + breaks 9.4 AC).

**Matrix-Control case (primary PO driver):** Instrument preset → Synth + MIDI Input on, MIDI Output off by default — user enables MIDI Output without changing preset.

## Acceptance Criteria

### AC1 — Plugin characteristics UI on Project tab

**Given** Project tab, Plugin Type section  
**Then** user sees **both**:
- Existing 3 preset radios (Instrument / Audio Effect / MIDI Effect)
- Independent checkboxes (Projucer-aligned labels):
  - Plugin is a Synth → `is_synth` / `IS_SYNTH`
  - Plugin MIDI Input → `needs_midi_input` / `NEEDS_MIDI_INPUT`
  - Plugin MIDI Output → `needs_midi_output` / `NEEDS_MIDI_OUTPUT`
  - MIDI Effect Plugin → `is_midi_effect` / `IS_MIDI_EFFECT`
  - Editor Requires Keyboard Focus → `editor_wants_keyboard_focus` / `EDITOR_WANTS_KEYBOARD_FOCUS`
- Audio I/O combo with values: `stereo` | `mono` | `synth-no-input` | `midi-effect` (default `stereo`; legacy underscore forms normalized on load)
- VST MIDI Inputs combo **1–16** (default **16**), visible/enabled when MIDI Input checked
- VST MIDI Outputs combo **1–16** (default **16**), visible/enabled when MIDI Output checked
- Plugin Description text field (optional, may be empty)

### AC2 — Preset default pre-check behaviour

**Given** Instrument preset selected (initial or after reset)  
**Then** Synth ✓, MIDI Input ✓, MIDI Output ✗, MIDI Effect ✗  
**And** user **may** enable MIDI Output (Matrix-Control)

**Given** Audio Effect preset  
**Then** Synth ✗, MIDI Input ✗, MIDI Output ✗, MIDI Effect ✗ (unless user toggles)

**Given** MIDI Effect preset  
**Then** MIDI Effect ✓, MIDI Input ✓, MIDI Output ✓, Synth ✗

### AC3 — Incompatible combination invalidates form

**Given** Synth **and** MIDI Effect both checked  
**Then** form is **invalid** (`ProjectPage.is_valid()` → False)  
**And** inline error visible near characteristics (same pattern as FormatsPage hint → `FieldError`)  
**And** Generate Project button disabled via existing `validityChanged` wiring

### AC4 — Preset change resets toggles (dirty guard)

**Given** user selects a **different** preset radio  
**Then** characteristic toggles reset to that preset's defaults (AC2 table)  
**And** Audio I/O combo resets to preset-appropriate default (`midi_effect` when MIDI Effect preset; else `stereo` unless preset logic dictates otherwise)  
**And** if `ProjectPage.is_dirty()` before the change, show confirmation via `confirm_discard_unsaved()` (reuse `app/confirm.py` pattern from Create New Project) — title e.g. `"Plugin Type"`, message explaining preset change will reset characteristics

### AC5 — MIDI Effect hides Audio I/O presets

**Given** `is_midi_effect` checked (by preset or manual toggle)  
**Then** Audio I/O combo is **disabled** (or hidden) and value forced to `midi_effect`  
**Given** `is_midi_effect` unchecked  
**Then** Audio I/O combo enabled with non-`midi_effect` options available

### AC6 — ProjectSpec serialization

**Given** `ProjectSpec.to_dict()` / `from_dict()`  
**Then** round-trip includes new fields with **camelCase JSON keys**:

| Python attribute | JSON key | Type | Default |
|------------------|----------|------|---------|
| `needs_midi_input` | `needsMidiInput` | `bool` | preset-derived |
| `needs_midi_output` | `needsMidiOutput` | `bool` | preset-derived |
| `is_synth` | `isSynth` | `bool` | preset-derived |
| `is_midi_effect` | `isMidiEffect` | `bool` | preset-derived |
| `editor_wants_keyboard_focus` | `editorWantsKeyboardFocus` | `bool` | `False` |
| `plugin_description` | `pluginDescription` | `str` | `""` |
| `audio_io_preset` | `audioIoPreset` | `str` | `"stereo"` or `"midi-effect"` when MIDI effect |
| `vst_num_midi_ins` | `vstNumMidiIns` | `int` | `16` |
| `vst_num_midi_outs` | `vstNumMidiOuts` | `int` | `16` |

**And** `from_dict` coerces bools via existing `_coerce_bool`  
**And** MIDI counts clamped or validated to **1–16** on load  
**And** successful Generate writes these keys into `.luthier.json` sidecar (automatic via `ProjectSpec.to_dict()` — no reader at runtime)

**And** `form_snapshots_equal()` in `core/project_form_state.py` includes new keys (uses `ProjectSpec().to_dict().keys()` — verify after adding fields)

### AC7 — plugin_settings refactor (preset defaults, not generate truth)

**Given** `core/plugin_settings.py`  
**Then** `flags_for_type(type_key)` is **replaced or renamed** to return **preset default booleans** (e.g. `preset_characteristics(type_key) -> dict[str, bool]`) — not CMake `"TRUE"`/`"FALSE"` strings  
**And** add pure helper e.g. `characteristics_conflict(is_synth, is_midi_effect) -> tuple[bool, str]` for UI + tests  
**And** keep `bundle_id()`, `au_and_vst3_categories()` unchanged (still take bool/str flags — 9.4 will pass spec-derived values)  
**And** `type_for_flags()` updated or deprecated if no longer needed after decoupling

### AC8 — Tests cover model + validation (not templates)

**Given** unit tests  
**Then** cover at minimum:
- `ProjectSpec` round-trip for all new fields + defaults on missing keys
- Preset default maps for all 3 presets (Instrument Matrix-Control defaults)
- `characteristics_conflict` — synth+midi effect invalid
- `form_snapshots_equal` detects characteristic toggle change
- Optional: pure preset-reset helper if extracted from UI

**And** existing `test_plugin_settings.py` / `test_render_context.py` updated for renamed APIs — **render_context behaviour unchanged** (still preset-driven flags until 9.4)

**And** full `.venv/bin/pytest` green

### AC9 — Out of scope (explicit)

**Not in 9.3:** `render_context.py` mapping, `Templates/CMakeLists.txt` placeholders, `PluginProcessor.cpp` bus variants, user manual updates, VST3 category picker (nice-to-have per handoff §5.6 — keep deriving categories from flags in 9.4)

## Tasks / Subtasks

- [x] **Extend `ProjectSpec`** (AC: 6)
  - [x] Add 9 fields with defaults aligned to Instrument preset
  - [x] Update `to_dict` / `from_dict` with camelCase keys + int coercion for MIDI counts
  - [x] Extend `tests/unit/test_project_spec.py` round-trip + missing-key defaults
- [x] **Refactor `plugin_settings.py`** (AC: 2, 7)
  - [x] Replace `flags_for_type` CMake-string dict with bool preset defaults function
  - [x] Add `characteristics_conflict()` validation helper
  - [x] Update `tests/unit/test_plugin_settings.py`
- [x] **Build characteristics UI** (AC: 1, 2, 3, 4, 5)
  - [x] Extend `app/pages/plugin_type.py` or split into `plugin_characteristics.py` (keep class ≤200 lines / methods ≤15)
  - [x] Wire checkboxes, `ComboField` for Audio I/O and MIDI counts, description field
  - [x] Emit `validityChanged` on conflict; connect in `ProjectPage._connect_signals`
  - [x] Preset change: apply defaults + dirty confirm via callback from `ProjectPage`
  - [x] MIDI Effect ↔ Audio I/O enable/disable logic
- [x] **Integrate `ProjectPage`** (AC: 3, 6)
  - [x] `spec()` / `load()` / `is_valid()` include characteristics widget
  - [x] Section title may become `"Plugin Type & Characteristics"` (optional)
- [x] **Tests** (AC: 8)
  - [x] Add `tests/unit/test_plugin_characteristics.py` (or extend existing) for pure logic
  - [x] Update `test_project_dirty_guard.py` if needed for new snapshot keys
  - [x] Run `.venv/bin/pytest` — full suite green
- [x] **Do NOT touch** (AC: 9)
  - [x] `core/render_context.py`, `Templates/*`, user docs — Story 9.4 / 9.5

## Dev Notes

### Current state — coupling to replace

#### `core/plugin_settings.py` — fixed flags per preset

```18:38:core/plugin_settings.py
# type_key -> (isSynth, isMidiEffect, needsMidiInput, needsMidiOutput)
_FLAGS = {
    TYPE_INSTRUMENT: ("TRUE", "FALSE", "TRUE", "FALSE"),
    TYPE_AUDIO_EFFECT: ("FALSE", "FALSE", "FALSE", "FALSE"),
    TYPE_MIDI_EFFECT: ("FALSE", "TRUE", "TRUE", "TRUE"),
}


def flags_for_type(type_key: str) -> dict:
    ...
    return {
        "isSynth": is_synth,
        "isMidiEffect": is_midi,
        "needsMidiInput": midi_in,
        "needsMidiOutput": midi_out,
    }
```

**Target:** preset function returns **bools**; CMake string conversion deferred to 9.4.

#### `core/render_context.py` — still reads preset only (unchanged in 9.3)

```20:24:core/render_context.py
def build_context(spec: ProjectSpec) -> dict:
    d = spec.to_dict()
    flags = plugin_settings.flags_for_type(d["pluginType"])
    context = {key: d[key] for key in _VALUE_KEYS}
    context.update(flags)
```

After 9.3 refactor, `flags_for_type` may become `preset_characteristics` returning bools — **temporarily** keep a thin adapter or leave `render_context` calling a compatibility shim that reads **preset defaults only** (not spec toggles) until 9.4. Simplest: rename internally but add `flags_for_type_from_preset(type_key)` that still returns `"TRUE"`/`"FALSE"` for render_context, marked for 9.4 removal.

#### `app/pages/plugin_type.py` — radios only today

```28:47:app/pages/plugin_type.py
class PluginTypePage(QWidget):
    ...
    def selected_type(self) -> str:
        checked = self._group.checkedButton()
        return checked.property("typeKey") if checked else _DEFAULT_TYPE

    def set_type(self, type_key: str) -> None:
        for button in self._group.buttons():
            if button.property("typeKey") == type_key:
                button.setChecked(True)
                return
```

**Target:** add `values() -> dict`, `load(d: dict)`, `is_valid() -> bool`, `apply_preset(type_key)`, `validityChanged` signal — mirror `FormatsPage` patterns.

#### `app/pages/project.py` — wire new widget API

```62:77:app/pages/project.py
    def spec(self) -> ProjectSpec:
        d = dict(self._info.values())
        d["pluginType"] = self._type.selected_type()
        ...
        return ProjectSpec.from_dict(d)

    def is_valid(self) -> bool:
        return (
            self._info.is_valid()
            and self._formats.is_valid()
            ...
        )
```

Add `d.update(self._type.characteristics_values())` (or merge into spec builder) and `and self._type.is_valid()`.

### Suggested preset defaults (source of truth)

| Preset key | `is_synth` | `needs_midi_input` | `needs_midi_output` | `is_midi_effect` | `audio_io_preset` |
|------------|------------|--------------------|--------------------|------------------|---------------------|
| `instrument` | True | True | False | False | `stereo` |
| `audio-effect` | False | False | False | False | `stereo` |
| `midi-effect` | False | True | True | True | `midi_effect` |

All presets: `editor_wants_keyboard_focus=False`, `plugin_description=""`, MIDI counts 16 when respective MIDI toggle on.

### Suggested pure helpers (`core/plugin_settings.py`)

```python
AUDIO_IO_PRESETS = ("stereo", "mono", "synth_no_input", "midi_effect")

def preset_characteristics(type_key: str) -> dict[str, bool]:
    ...

def characteristics_conflict(is_synth: bool, is_midi_effect: bool) -> tuple[bool, str]:
    if is_synth and is_midi_effect:
        return False, "Synth and MIDI Effect cannot both be enabled."
    return True, ""

def clamp_midi_count(value, default: int = 16) -> int:
    ...
```

### UI patterns to reuse

| Pattern | Reference |
|---------|-----------|
| Checkboxes + validity hint | `app/pages/formats.py` — `FieldHint` / `FieldError` + `repolish()` |
| Label + combo row | `app/widgets/combo_field.py` — `ComboField(label, choices, default)` |
| Optional text | `ValidatedField` (single line) or small `QLineEdit` row with `make_field_label` |
| Dirty confirm on destructive reset | `app/main_window.py` `_on_create_new_project` → `confirm_discard_unsaved` |
| Aggregate validity | `ProjectPage.validityChanged` → Generate button |

### Preset change + dirty guard flow

```
User clicks different preset radio
  → if dirty_callback() and not confirm_discard_unsaved(...): revert radio selection
  → apply_preset_defaults(new_type_key)
  → emit changed + validityChanged
```

Implement `dirty_callback` as lambda from `ProjectPage`: `lambda: self.is_dirty()`. Block signal when `load(spec)` programmatically sets preset.

### Audio I/O + MIDI Effect interaction

```
is_midi_effect toggled ON  → set audio_io_preset = "midi_effect"; disable combo
is_midi_effect toggled OFF → enable combo; if value was midi_effect, set "stereo"
needs_midi_input OFF       → disable vst_num_midi_ins combo (value may remain stored)
needs_midi_output OFF      → disable vst_num_midi_outs combo
```

### CMake template context (reference for 9.4 — do not implement in 9.3)

Current `Templates/CMakeLists.txt` uses `{isSynth}`, `{needsMidiInput}`, `{needsMidiOutput}`, `{isMidiEffect}`, hardcoded `EDITOR_WANTS_KEYBOARD_FOCUS FALSE`. Story 9.4 will add `{editorWantsKeyboardFocus}`, `{pluginDescription}`, `{vstNumMidiIns}`, `{vstNumMidiOuts}` and bus variants in `PluginProcessor.cpp` per handoff §5.3.

### Overlap with other Epic 9 stories

| Story | Boundary |
|-------|----------|
| 9.1 / 9.7 | Done — no accent/Open/tree regressions |
| 9.2 | Done (or local) — do not touch generate guard |
| **9.3** | Spec + UI + plugin_settings preset/validation |
| 9.4 | render_context + Templates — **blocked on 9.3** |
| 9.6 | Broader test alignment — 9.3 adds focused unit tests only |
| 9.5 | Manuals — out of scope |

### Out of scope

- CMake / C++ template changes
- `render_context.build_context()` reading spec characteristics
- VST3 category manual picker (auto-derive in 9.4)
- Preferences tab changes
- Qt widget automated tests (AD-6 — manual smoke)

### Project Structure Notes

- **Layer boundaries (AD-8):** validation helpers in `core/plugin_settings.py`; Qt in `app/pages/`
- **Clean code limits:** extract sub-widgets if `PluginTypePage` exceeds 200 lines
- **No comments policy:** no story/ticket references in code
- **Run:** `.venv/bin/python main.py`
- **Tests:** `.venv/bin/pytest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 9.3]
- [Source: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §5.2–5.5, §9.3]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md §5 F1]
- [Source: core/plugin_settings.py — `_FLAGS`, `flags_for_type`]
- [Source: core/project_spec.py — field inventory pattern]
- [Source: app/pages/plugin_type.py — current radios-only UI]
- [Source: app/pages/formats.py — checkbox validity pattern]
- [Source: app/pages/project.py — spec()/is_valid()/load()]
- [Source: core/project_form_state.py — dirty snapshot keys]
- [Source: _bmad-output/implementation-artifacts/9-2-block-generate-non-empty-destination.md — prior story patterns]

## Dev Agent Guardrails

### Technical requirements

1. **Decouple UI state from generate pipeline in 9.3:** Sidecar + form reflect toggles; CMake generation unchanged until 9.4.
2. **Preset defaults are starting points, not locks:** Instrument + MIDI Output enabled manually must be valid and serializable.
3. **Synth + MIDI Effect = hard invalid:** Block Generate via `is_valid()` — no silent coercion.
4. **Preset change resets characteristics:** With dirty confirmation when `ProjectPage.is_dirty()`.
5. **MIDI Effect forces `midi_effect` audio preset:** Disable other I/O options while active.
6. **camelCase JSON keys:** Match existing `ProjectSpec` convention (`needsMidiInput`, not `needs_midi_input` in JSON).
7. **Do not regress 9.1/9.7/9.2:** No Open, no accent in sidecar, generate guard intact.

### Architecture compliance

| AD | Rule for 9.3 |
|----|--------------|
| AD-3 | Sidecar write-only — new fields appear in `.luthier.json` on Generate |
| AD-5 | Generate never writes `preferences.json` |
| AD-6 | Unit tests for core validation + ProjectSpec; manual UI smoke for characteristics |
| AD-8 | Pure logic in `core/`; widgets in `app/pages/` |

No `architecture-spine.md` update required unless dev agent adds a one-line FR11 note — optional, not blocking.

### Library / framework requirements

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- Reuse `ComboField`, `confirm_discard_unsaved`, `repolish`, `make_field_label`
- `QButtonGroup.blockSignals(True)` when loading spec to avoid spurious preset-reset dialogs

### File structure requirements

| File | Action |
|------|--------|
| `core/project_spec.py` | Add 9 fields + serialization |
| `core/plugin_settings.py` | Preset defaults + conflict validation |
| `app/pages/plugin_type.py` | Extend UI (or split helper module) |
| `app/pages/project.py` | Wire values/load/validity/dirty callback |
| `tests/unit/test_project_spec.py` | New field round-trips |
| `tests/unit/test_plugin_settings.py` | Update for API rename |
| `tests/unit/test_plugin_characteristics.py` | **New** — validation + preset defaults |
| `tests/unit/test_project_dirty_guard.py` | Update if snapshot coverage needed |

**Do not modify in 9.3:** `core/render_context.py`, `Templates/**`, `docs/user/**`, `app/main_window.py` (unless preset confirm needs no main_window changes — keep confirm in page via imported helper)

### Testing requirements

**Must pass before marking done:**
```bash
.venv/bin/pytest
```

**Manual smoke (required — AD-6):**
1. New project → Instrument preset → Synth+MIDI In on, MIDI Out off
2. Enable MIDI Output → form valid, Generate enabled
3. Enable Synth + MIDI Effect together → inline error, Generate disabled
4. Select MIDI Effect preset → Audio I/O locked to midi_effect
5. Customize toggles, change preset → dirty confirm appears; confirm resets toggles
6. Generate → inspect `.luthier.json` contains new camelCase keys with expected values

### Previous story intelligence

**From 9.2 (done / local):**
- Generate guard in `core/project_generator.py` — do not conflict with form validity (both can block Generate independently)
- `ProjectPage.load(spec)` after Generate syncs baseline — new fields must participate in `load()` / `_capture_baseline()`
- Full suite baseline after 9.2: **245 passed, 3 skipped** (per 9.2 story file)

**From 9.7 (done):**
- `ComboField` + tree connectors patterns established — reuse combo widget for Audio I/O and MIDI counts
- Touch `project.py` only for characteristics wiring — do not revert accent/tree work

**From 9.1 (done):**
- Sidecar is write-only metadata — new fields are for humans/AI reference, not app reload

### Git intelligence

Recent Epic 9 commits:
- `a09f879` — Story 9.7: OS tree connectors + live accent theme
- `c163cf2` — Story 9.1: Remove Open Project, delete `project_reader`

Story 9.2 changes may exist **uncommitted** (generate guard in `project_generator.py`, `main_window.py`). Verify guard tests pass before starting 9.3.

Follow established patterns: pure helpers in `core/`, minimal Qt wiring, pytest green, no template edits in this story.

### Latest tech information

No new libraries. PySide6 checkbox/combo patterns unchanged in 6.7+. Projucer characteristic names mapped 1:1 to JUCE `juce_add_plugin` flags (verified against handoff §5.2) — CMake wiring is 9.4.

## Project Context Reference

Key rules from `_bmad-output/project-context.md`:
- `ProjectPage.spec()` → `ProjectSpec` → Generate pipeline — extend spec, not render path in 9.3
- Form keys: **camelCase** in dicts (`pluginType`, `needsMidiInput`, …)
- `form_snapshots_equal` compares all `ProjectSpec.to_dict()` keys — new fields auto-included once dataclass updated
- Plugin type page today: `app/pages/plugin_type.py` listed under Project sections
- Run via `.venv/bin/python main.py`

## Story Completion Status

- **Status:** done
- **Completion note:** Decoupled plugin characteristics in ProjectSpec + UI; render_context unchanged (preset-driven until 9.4). Code review patches applied (AC3 validity, FieldError, guards). Full pytest: 282 passed, 3 skipped.
- **Next story after dev:** 9.4 (`9-4-template-pipeline-audio-io-midi-description`) wires render_context + Templates to spec fields

## Dev Agent Record

### Agent Model Used

claude-4.6-sonnet-medium-thinking

### Debug Log References

### Completion Notes List

- Added 9 `ProjectSpec` fields with camelCase serialization and MIDI count validation via `clamp_midi_count`.
- Refactored `plugin_settings`: `preset_characteristics`, `preset_audio_io`, `characteristics_conflict`, `clamp_midi_count`; kept `flags_for_type` as preset-only CMake shim for `render_context`.
- Split UI into `PluginCharacteristicsWidget` + extended `PluginTypePage` with preset dirty-guard, conflict validation, and MIDI Effect / Audio I/O interaction.
- Wired `ProjectPage.spec()` / `load()` / `is_valid()` and renamed section to "Plugin Type & Characteristics".
- Tests: `test_plugin_characteristics.py` (new), updates to `test_project_spec`, `test_plugin_settings`, `test_project_dirty_guard`.

### File List

- core/project_spec.py
- core/plugin_settings.py
- app/pages/plugin_characteristics.py (new)
- app/pages/plugin_type.py
- app/pages/project.py
- app/widgets/combo_field.py
- tests/unit/test_plugin_characteristics.py (new)
- tests/unit/test_project_spec.py
- tests/unit/test_plugin_settings.py
- tests/unit/test_project_dirty_guard.py

### Change Log

- 2026-07-04: Story 9.3 — decoupled plugin characteristics in form/sidecar; generation pipeline still preset-driven until 9.4.

### Review Findings

- [x] [Review][Decision] Audio I/O preset identifier format — **Resolved:** keep kebab-case (`synth-no-input`, `midi-effect`); spec AC1/AC6 updated; legacy underscore normalized on load.

- [x] [Review][Patch] AC3 — `is_valid()` always returns True; `characteristics_conflict()` never called [app/pages/plugin_characteristics.py:126-127]
- [x] [Review][Patch] AC3 — No inline `FieldError` on Synth+MIDI Effect conflict (FormatsPage pattern missing) [app/pages/plugin_characteristics.py]
- [x] [Review][Patch] AC5 — Manual `is_midi_effect` toggle does not lock Audio I/O combo [app/pages/plugin_characteristics.py:189-193]
- [x] [Review][Patch] `apply_preset()` emits spurious `changed`/`validityChanged` without `_loading` guard [app/pages/plugin_characteristics.py:129-142]
- [x] [Review][Patch] `load()` paths lack try/finally for `_loading` flag [app/pages/plugin_type.py:64-72, app/pages/plugin_characteristics.py:109-124]
- [x] [Review][Patch] `set_type()` silently no-ops on unknown `type_key` [app/pages/plugin_type.py:74-78]
- [x] [Review][Patch] `ComboField` empty choices can yield `int('')` in `values()` [app/widgets/combo_field.py:42-52]
- [x] [Review][Patch] `load()` checkbox fallback uses stale `isChecked()` instead of preset default [app/pages/plugin_characteristics.py:114]
- [x] [Review][Patch] `ComboField._combo` private attribute accessed for signals [app/pages/plugin_characteristics.py:185-187]

- [x] [Review][Defer] `type_for_flags()` not deprecated — still used by `render_context` path and round-trip tests until Story 9.4 [core/plugin_settings.py:145-150] — deferred, intentional shim
- [x] [Review][Defer] Preset confirm dialog omits description/MIDI count reset from message [app/pages/plugin_type.py:27-30] — deferred, UX polish
