---
epic: 9
story: 4
story_key: 9-4-template-pipeline-audio-io-midi-description
depends_on: [9-3, 9-8]
blocks: [9-6]
implementation_order: 6
pivot_date: 2026-07-04
baseline_commit: d8d356f
---

# Story 9.4: Template Pipeline — Audio I/O, MIDI, Description

Status: done

<!-- Validation: optional — run validate-create-story before dev-story. -->

## Story

As a JUCE developer,
I want generated CMake and C++ sources to reflect my characteristic choices,
So that the scaffold compiles with the correct buses, MIDI counts, and metadata.

## Context

**Epic 9 pivot (2026-07-04):** Luthier is a **one-shot JUCE/CMake skeleton generator**. Stories **9.1–9.3** and **9.8** are **done** — scaffold-only positioning, decoupled plugin characteristics in form/sidecar, generate guard + session regenerate carve-out.

**Story 9.3 delivered UI + `ProjectSpec` fields but deliberately left the generation pipeline preset-driven.** Today `render_context.build_context()` still calls `plugin_settings.flags_for_type(d["pluginType"])`, ignoring user toggles (e.g. Instrument + MIDI Output / Matrix-Control). **Story 9.4 wires the template pipeline to `ProjectSpec` characteristic fields.**

**FR11 (generation half):** Generated `juce_add_plugin` and `PluginProcessor::createBusesProperties()` must reflect form choices — not preset defaults alone.

**Planning references:**
- `_bmad-output/planning-artifacts/epics.md` — Epic 9, Story 9.4
- `_bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md` — §5.3 (Audio I/O presets), §5.4 (MIDI counts), §5.5 (Description), §9.4 file inventory
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md` — §5 F1 generation half

**Recommended Epic 9 order:** `9.1 → 9.7 → 9.2 → 9.3 → 9.8 → 9.4 → 9.6 → 9.5`

### What changes vs what stays

| Area | Change (9.4) | Keep unchanged |
|------|--------------|----------------|
| `render_context.py` | Read **spec** characteristic fields → CMake context + categories | str.format / token pass mechanics |
| `plugin_settings.py` | Add spec→CMake + buses C++ helpers; `flags_for_type` = preset defaults **only** | Preset UI helpers (`preset_characteristics`, etc.) |
| `Templates/CMakeLists.txt` | `DESCRIPTION`, `EDITOR_WANTS_KEYBOARD_FOCUS`, `VST_NUM_MIDI_*` placeholders | Existing company/format blocks |
| `Templates/Source/PluginProcessor.cpp` | `createBusesProperties()` driven by `audioIoPreset` + `isSynth` | Rest of processor/editor templates |
| `build_tokens()` | New `@CREATE_BUSES_PROPERTIES_BODY@` token | `@PROJECT_NAME@`, `@PROJECT_DISPLAY_NAME@` |
| App UI / `ProjectSpec` | — | Already done in 9.3 |
| Generate guard / session regenerate | — | 9.2 + 9.8 |
| User manuals | — | Story 9.5 |

### Critical distinction for dev agent

**9.3 explicitly deferred render_context and Templates changes.** Do not re-touch characteristics UI unless a wiring bug blocks generation tests.

**Primary PO smoke case (Matrix-Control):** Instrument preset + user enables **MIDI Output** → generated `CMakeLists.txt` has `NEEDS_MIDI_OUTPUT TRUE` and sidecar already has `needsMidiOutput: true` — after 9.4 they must **match**.

**Audio I/O preset identifiers:** UI/spec use **kebab-case** (`synth-no-input`, `midi-effect`). Internal helpers must accept normalized values from `normalize_audio_io_preset()`.

## Acceptance Criteria

### AC1 — CMake reflects all characteristic flags from spec

**Given** `ProjectSpec` with characteristic toggles that **differ** from the type preset defaults (e.g. Instrument + `needs_midi_output=True`)  
**When** project is generated  
**Then** rendered `CMakeLists.txt` `juce_add_plugin(...)` contains:

| Placeholder | Source |
|-------------|--------|
| `IS_SYNTH {isSynth}` | `spec.is_synth` → `TRUE`/`FALSE` |
| `NEEDS_MIDI_INPUT {needsMidiInput}` | `spec.needs_midi_input` |
| `NEEDS_MIDI_OUTPUT {needsMidiOutput}` | `spec.needs_midi_output` |
| `IS_MIDI_EFFECT {isMidiEffect}` | `spec.is_midi_effect` |
| `EDITOR_WANTS_KEYBOARD_FOCUS {editorWantsKeyboardFocus}` | `spec.editor_wants_keyboard_focus` |
| `DESCRIPTION {pluginDescription}` | `spec.plugin_description` (CMake-quoted; empty → `""`) |
| `VST_NUM_MIDI_INS {vstNumMidiIns}` | `spec.vst_num_midi_ins` (integer 1–16) |
| `VST_NUM_MIDI_OUTS {vstNumMidiOuts}` | `spec.vst_num_midi_outs` (integer 1–16) |

**And** values come from **`ProjectSpec` fields**, not `flags_for_type(pluginType)`.

### AC2 — AU/VST3 categories derived from spec flags

**Given** generated context  
**Then** `auMainType` and `vst3Categories` use `au_and_vst3_categories(isSynth, isMidiEffect)` with **spec-derived** CMake strings (same as AC1 flags)  
**And** Instrument + MIDI Output (Matrix-Control) still yields Instrument/Synth categories when `is_synth=True`, `is_midi_effect=False`

### AC3 — `createBusesProperties()` matches audio I/O preset (handoff §5.3)

**Given** `audioIoPreset` on spec (normalized kebab-case)  
**Then** generated `Source/PluginProcessor.cpp` `createBusesProperties()` body matches:

| Preset | `createBusesProperties()` behaviour |
|--------|-------------------------------------|
| `midi-effect` | `return {};` (no audio buses) |
| `stereo` + effect (`is_synth=False`, not midi effect) | input stereo + output stereo |
| `stereo` + synth (`is_synth=True`) | output stereo only (no input bus) |
| `mono` + effect | input mono + output mono |
| `mono` + synth | output mono only |
| `synth-no-input` | output stereo only (no input bus) |

**And** when `is_midi_effect=True`, preset is forced to `midi-effect` (9.3 UI rule) — buses `{}` regardless of other toggles.

**And** unrendered bundled template remains **valid C++** (default stub body under `@CREATE_BUSES_PROPERTIES_BODY@`).

### AC4 — `flags_for_type` no longer sole generate truth

**Given** `plugin_settings.flags_for_type(type_key)`  
**Then** still returns preset-default CMake strings (for tests / legacy callers)  
**And** `render_context.build_context()` **does not** use it as the source of generated flags — uses spec fields via new helper (e.g. `characteristics_cmake_context(spec)`)

### AC5 — Session regenerate emits updated characteristics

**Given** user generated once, changed characteristics (e.g. enabled MIDI Output), confirmed session regenerate (9.8)  
**When** regenerate succeeds  
**Then** new `CMakeLists.txt` and `PluginProcessor.cpp` reflect **current** form spec (not first-generation preset-only output)

### AC6 — Tests

**Given** unit + integration tests  
**Then** cover at minimum:
- Spec override vs preset: Instrument + `needs_midi_output=True` → `needsMidiOutput TRUE` in context
- All four `audioIoPreset` bus bodies (pure function tests)
- `pluginDescription` with quotes/special chars → safe CMake quoting
- `editorWantsKeyboardFocus`, MIDI counts in context
- Integration spot-check: `generate_project()` → parse `CMakeLists.txt` for Matrix-Control flags
- Existing `test_render_context.py` preset-only parametrized tests **updated** to assert spec-driven behaviour (or split preset-default vs override cases)

**And** full `.venv/bin/pytest` green

### AC7 — Out of scope (explicit)

**Not in 9.4:** UI changes, `ProjectSpec` schema changes, user manual updates (9.5), broad test-suite cleanup (9.6), VST3 category manual picker, free-text channel configs, `type_for_flags` removal unless dead after refactor

## Tasks / Subtasks

- [x] **Spec → CMake context** (AC: 1, 2, 4)
  - [x] Add `characteristics_cmake_context(spec: ProjectSpec) -> dict` in `core/plugin_settings.py` or `core/render_context.py`
  - [x] Refactor `build_context()` to use spec fields; update `_categories()` call site
  - [x] Add `_cmake_description(value: str) -> str` (reuse `_cmake_quoted` pattern)
- [x] **Audio bus C++ generator** (AC: 3)
  - [x] Add pure `buses_properties_body(is_synth, is_midi_effect, audio_io_preset) -> str`
  - [x] Extend `build_tokens()` with `CREATE_BUSES_PROPERTIES_BODY`
  - [x] Update `Templates/Source/PluginProcessor.cpp` to use `@CREATE_BUSES_PROPERTIES_BODY@`
- [x] **CMake template** (AC: 1)
  - [x] Replace hardcoded `EDITOR_WANTS_KEYBOARD_FOCUS FALSE`
  - [x] Add `DESCRIPTION`, `VST_NUM_MIDI_INS`, `VST_NUM_MIDI_OUTS` lines to `juce_add_plugin`
- [x] **Tests** (AC: 6)
  - [x] Extend `tests/unit/test_render_context.py` (override matrix + new keys)
  - [x] Add `tests/unit/test_buses_properties.py` or section in `test_plugin_settings.py`
  - [x] Add integration CMake spot-check in `tests/integration/test_round_trip.py` or dedicated module
  - [x] Run `.venv/bin/pytest` — full suite green
- [x] **Docs touch (optional)** 
  - [x] Update `_bmad-output/project-context.md` token list if third token added

### Review Findings

- [x] [Review][Decision] Unrendered template valid C++ (AC3) — **Resolved: 1B** — bare `@CREATE_BUSES_PROPERTIES_BODY@` token accepted; valid C++ after generation, consistent with `@KEY@` pipeline (not at repo checkout).

- [x] [Review][Decision] `_SIDECAR_KEY_ORDER` scope (AC7) — **Resolved: 2A** — keep sidecar key ordering (UI section order); DX improvement only, no schema change; documented in file list below.

- [x] [Review][Patch] Duplicate `_bool_to_cmake` [`core/render_context.py:35`] — fixed: reuse `plugin_settings._bool_to_cmake`.

- [x] [Review][Patch] AC5 regenerate test gap [`tests/integration/test_round_trip.py`] — fixed: assert `PluginProcessor.cpp` bus layout updates on regenerate (`stereo` → `mono`).

- [x] [Review][Defer] `_cmake_quoted` newline/tab not escaped [`core/render_context.py:20`] — deferred, pre-existing acceptance in `deferred-work.md` for description fields; same trade-off applies to new `pluginDescription` path.

- [x] [Review][Defer] Unknown `audio_io_preset` silent fallback [`core/plugin_settings.py:157`] — deferred, `normalize_audio_io_preset()` returns `"stereo"` by design; UI constrains choices.

- [x] [Review][Defer] User template override may retain unreplaced `@CREATE_BUSES_PROPERTIES_BODY@` — deferred, pre-existing token-override pattern; documentation belongs in Story 9.5.

## Dev Notes

### Current state — the gap 9.4 closes

#### `core/render_context.py` — still preset-driven

```20:31:core/render_context.py
def build_context(spec: ProjectSpec) -> dict:
    d = spec.to_dict()
    flags = plugin_settings.flags_for_type(d["pluginType"])
    context = {key: d[key] for key in _VALUE_KEYS}
    context.update(flags)
    context.update(_categories(flags))
    ...
```

**Target:** `flags = plugin_settings.characteristics_cmake_context(spec)` (or inline from spec bools). `_categories()` receives spec-derived `isSynth`/`isMidiEffect` strings.

#### `Templates/CMakeLists.txt` — missing new placeholders

```159:163:Templates/CMakeLists.txt
    IS_SYNTH {isSynth}
    NEEDS_MIDI_INPUT {needsMidiInput}
    NEEDS_MIDI_OUTPUT {needsMidiOutput}
    IS_MIDI_EFFECT {isMidiEffect}
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
```

**Target:** dynamic `EDITOR_WANTS_KEYBOARD_FOCUS`, plus `DESCRIPTION`, `VST_NUM_MIDI_INS`, `VST_NUM_MIDI_OUTS`.

#### `Templates/Source/PluginProcessor.cpp` — fixed stereo + JUCE macros

Current logic uses `#if JucePlugin_IsMidiEffect` / `#if !JucePlugin_IsSynth` — works for preset defaults only. **Replace inner body** with generated C++ from `audioIoPreset` + `is_synth` (see AC3 table). JUCE compile-time macros still reflect CMake flags; bus layout must match **explicit preset** (e.g. `mono` synth must use mono output, not stereo).

Suggested template shape (valid C++ when unrendered):

```cpp
juce::AudioProcessor::BusesProperties PluginProcessor::createBusesProperties()
{
@CREATE_BUSES_PROPERTIES_BODY@
}
```

Default token value in repo template file (before substitution): stereo-out-only stub matching current synth default.

### Suggested pure helpers

```python
def characteristics_cmake_context(spec: ProjectSpec) -> dict:
    return {
        "isSynth": _bool_to_cmake(spec.is_synth),
        "isMidiEffect": _bool_to_cmake(spec.is_midi_effect),
        "needsMidiInput": _bool_to_cmake(spec.needs_midi_input),
        "needsMidiOutput": _bool_to_cmake(spec.needs_midi_output),
        "editorWantsKeyboardFocus": _bool_to_cmake(spec.editor_wants_keyboard_focus),
        "pluginDescription": _cmake_quoted(spec.plugin_description or ""),
        "vstNumMidiIns": str(spec.vst_num_midi_ins),
        "vstNumMidiOuts": str(spec.vst_num_midi_outs),
    }

def buses_properties_body(is_synth: bool, is_midi_effect: bool, audio_io_preset: str) -> str:
    preset = normalize_audio_io_preset(audio_io_preset)
    if is_midi_effect or preset == "midi-effect":
        return "    return {};"
    if preset == "synth-no-input":
        return _OUT_STEREO_ONLY_BODY
    if preset == "mono":
        return _MONO_EFFECT_BODY if not is_synth else _MONO_OUT_ONLY_BODY
    # stereo (default)
    return _STEREO_EFFECT_BODY if not is_synth else _OUT_STEREO_ONLY_BODY
```

Keep each `_*_BODY` as a multiline string constant (4–6 lines) to stay under clean-code limits; orchestrator delegates.

### `build_tokens()` extension

```python
def build_tokens(spec: ProjectSpec) -> dict:
    return {
        "PROJECT_NAME": spec.project_name,
        "PROJECT_DISPLAY_NAME": spec.project_display_name,
        "CREATE_BUSES_PROPERTIES_BODY": plugin_settings.buses_properties_body(
            spec.is_synth, spec.is_midi_effect, spec.audio_io_preset
        ),
    }
```

**User template overrides:** `ProjectWriter` still applies overrides for `PluginProcessor.cpp`; token replacement runs on override content too — overrides must retain `@CREATE_BUSES_PROPERTIES_BODY@` unless user intentionally removes it (document in 9.5, not 9.4).

### Matrix-Control integration test sketch

```python
def test_matrix_control_midi_output_in_cmake(tmp_path):
    spec = make_spec(
        tmp_path,
        plugin_type=TYPE_INSTRUMENT,
        needs_midi_output=True,
        is_synth=True,
        needs_midi_input=True,
    )
    project_dir, _ = generate_project(tmp_path, spec=spec)
    cmake = (project_dir / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "NEEDS_MIDI_OUTPUT TRUE" in cmake
    assert "NEEDS_MIDI_INPUT TRUE" in cmake
    assert "IS_SYNTH TRUE" in cmake
```

Use `make_spec` / `ProjectSpec.from_dict` — verify `tests/conftest.py` `make_spec` accepts new kwargs (extend if needed).

### Overlap with other Epic 9 stories

| Story | Boundary |
|-------|----------|
| 9.3 | Done — spec + UI; do not rework unless blocking bug |
| 9.8 | Done — session regenerate must pick up new CMake after 9.4 |
| **9.4** | render_context + Templates + focused tests |
| 9.6 | Broader regression matrix, reader removal, doc test cleanup |
| 9.5 | Manuals — out of scope |

### Anti-patterns (do NOT)

- **Do not** read characteristics from `pluginType` preset at generate time
- **Do not** move `PluginProcessor.cpp` to str.format `{` placeholders (breaks valid-C++-when-unrendered rule for user overrides)
- **Do not** reintroduce Open/reload or read `.luthier.json` into form
- **Do not** weaken 9.2/9.8 generate guard
- **Do not** add free-text bus configuration (handoff §5.7)

### Project Structure Notes

- **Layer boundaries (AD-8):** bus + CMake mapping in `core/`; templates in `Templates/`
- **Clean code limits:** extract body string constants; keep orchestrators ≤15 lines
- **Run:** `.venv/bin/python main.py`
- **Tests:** `.venv/bin/pytest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 9.4]
- [Source: _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §5.3–5.5, §9.4]
- [Source: core/render_context.py — build_context, build_tokens]
- [Source: core/plugin_settings.py — flags_for_type shim, normalize_audio_io_preset]
- [Source: core/project_spec.py — characteristic fields]
- [Source: Templates/CMakeLists.txt — juce_add_plugin block]
- [Source: Templates/Source/PluginProcessor.cpp — createBusesProperties]
- [Source: _bmad-output/implementation-artifacts/9-3-decoupled-plugin-characteristics-and-projectspec.md]
- [Source: _bmad-output/implementation-artifacts/9-8-session-regenerate-with-warning.md]

## Dev Agent Guardrails

### Technical requirements

1. **Generation truth = `ProjectSpec` characteristic fields**, not `pluginType` preset.
2. **Matrix-Control must compile:** Instrument + MIDI Output → CMake MIDI output TRUE + sensible stereo buses.
3. **Four audio I/O presets only** — map kebab-case spec values; no underscore forms in generated code.
4. **MIDI effect → empty buses** — `{}` regardless of other preset selection.
5. **CMake quoting** for `DESCRIPTION` — escape `"`, `\`, `$` like existing path quoting.
6. **Third token allowed** — `@CREATE_BUSES_PROPERTIES_BODY@`; update project-context token note if touched.
7. **Do not regress 9.1–9.3, 9.7, 9.8** — guard, session regenerate, sidecar write-only, accent Preferences-only.

### Architecture compliance

| AD | Rule for 9.4 |
|----|--------------|
| AD-1 | `ProjectSpec` remains cross-layer contract; render_context reads spec |
| AD-3 | Sidecar unchanged — already has characteristic keys from 9.3 |
| AD-4 | Writer replace semantics unchanged; 9.8 carve-out still works |
| AD-6 | Unit tests for new pure helpers + render_context; integration spot-check |
| AD-8 | Pure bus/CMake logic in `core/`; no Qt imports in render path |

### Library / framework requirements

- **Python 3.14**, **PySide6 ≥ 6.7** — no new dependencies
- **JUCE `juce_add_plugin`** — `DESCRIPTION`, `VST_NUM_MIDI_INS`, `VST_NUM_MIDI_OUTS`, `EDITOR_WANTS_KEYBOARD_FOCUS` are standard JUCE CMake args (same as Projucer)
- No web research required — JUCE API stable for these fields

### File structure requirements

| File | Action |
|------|--------|
| `core/render_context.py` | Spec-driven characteristics + extend `build_tokens` |
| `core/plugin_settings.py` | Add `characteristics_cmake_context`, `buses_properties_body` |
| `Templates/CMakeLists.txt` | New juce_add_plugin placeholders |
| `Templates/Source/PluginProcessor.cpp` | Token-based bus body |
| `tests/unit/test_render_context.py` | Update + add override cases |
| `tests/unit/test_plugin_settings.py` | Bus body tests (or new file) |
| `tests/integration/test_round_trip.py` | CMake characteristic spot-check |
| `tests/conftest.py` | Extend `make_spec` if missing characteristic kwargs |

**Do not modify in 9.4:** `app/pages/*` (unless `make_spec`-only), `docs/user/**`, `app/main_window.py` generate flow, `core/project_writer.py` (unless token list comment)

### Testing requirements

**Must pass before marking done:**
```bash
.venv/bin/pytest
```

**Manual smoke (required — AD-6):**
1. Instrument preset → enable MIDI Output → Generate → CMake has `NEEDS_MIDI_OUTPUT TRUE`
2. MIDI Effect preset → Generate → `createBusesProperties()` returns `{}`; CMake `IS_MIDI_EFFECT TRUE`
3. Audio Effect → Audio I/O **Mono** → mono in+out buses in generated cpp
4. Instrument → Audio I/O **Synth No Input** → stereo out only
5. Fill Plugin Description → appears quoted in CMake `DESCRIPTION`
6. Session regenerate after toggling keyboard focus → CMake updates on confirm

### Previous story intelligence

**From 9.3 (done):**
- Nine characteristic fields on `ProjectSpec` with camelCase sidecar keys
- `flags_for_type()` intentionally preset-only shim — **9.4 replaces its use in render_context**
- `normalize_audio_io_preset()` handles legacy underscore forms on load
- Audio I/O UI uses kebab-case: `synth-no-input`, `midi-effect`
- Full pytest baseline: **282 passed, 3 skipped**

**From 9.8 (done):**
- Session regenerate re-runs full generate with current spec — 9.4 changes automatically flow through
- Use `generate_project()` / `allow_overwrite=True` patterns in tests for regenerate scenarios
- Full pytest baseline: **291 passed, 3 skipped**

**From 9.2 (done):**
- Do not conflate generate guard with template work

### Git intelligence

Recent Epic 9 commits:
- `d8d356f` — Story 9.8: session regenerate + `allow_overwrite`
- `97c808c` — Stories 9.2–9.3: generate guard + decoupled characteristics UI/spec
- `a09f879` — Story 9.7: OS tree connectors + accent theme

Follow established patterns: pure helpers in `core/`, minimal template diffs, pytest green, no UI scope creep.

### Latest tech information

No new libraries. JUCE `juce_add_plugin` CMake arguments match Projucer exports. Bus layout uses `juce::AudioProcessor::BusesProperties::withInput` / `withOutput` with `juce::AudioChannelSet::stereo()` or `::mono()` — same API as current template.

## Project Context Reference

Key rules from `_bmad-output/project-context.md`:
- Two-pass rendering: CMake via `str.format` (`rendering.render`), Source via `@KEY@` tokens (`rendering.render_tokens`)
- Previously documented tokens: `@PROJECT_NAME@`, `@PROJECT_DISPLAY_NAME@` — **9.4 adds `@CREATE_BUSES_PROPERTIES_BODY@`**
- `ProjectPage.spec()` → `ProjectSpec` → `build_context` / `build_tokens` → `ProjectWriter`
- Form/sidecar keys: camelCase; Python attrs: snake_case
- Run via `.venv/bin/python main.py`

## Story Completion Status

- **Status:** done
- **Completion note:** Template pipeline reads ProjectSpec characteristic fields; Matrix-Control and all four audio I/O presets covered by tests
- **Next story after dev:** 9.6 (`9-6-test-suite-scaffold-only-regression`) — broader test alignment; 9.4 adds focused pipeline tests only

## Dev Agent Record

### Agent Model Used

Claude (Cursor Agent)

### Debug Log References

- `build_context()` now calls `characteristics_cmake_context(spec)` instead of `flags_for_type(pluginType)` — categories derived from spec flags
- `buses_properties_body()` in `plugin_settings.py` with four preset branches + MIDI effect empty buses
- Third token `@CREATE_BUSES_PROPERTIES_BODY@` in `templates/Source/PluginProcessor.cpp`

### Completion Notes List

- Wired template pipeline to `ProjectSpec` characteristic fields (AC1–AC5): CMake flags, categories, description quoting, VST MIDI counts, keyboard focus
- Added `buses_properties_body()` pure helper and `@CREATE_BUSES_PROPERTIES_BODY@` token for `createBusesProperties()` (AC3)
- `flags_for_type()` unchanged for preset-default callers; no longer used by `build_context()` (AC4)
- `_SIDECAR_KEY_ORDER` in `to_dict()` — sidecar keys emitted in Project tab section order (DX; no schema change)
- 18 new tests; full suite **309 passed, 3 skipped**

### File List

- `core/render_context.py` — `characteristics_cmake_context()`, spec-driven `build_context()`, extended `build_tokens()`
- `core/plugin_settings.py` — `buses_properties_body()` with body string constants
- `core/project_spec.py` — `_SIDECAR_KEY_ORDER`; `to_dict()` emits keys in UI section order
- `templates/CMakeLists.txt` — dynamic `EDITOR_WANTS_KEYBOARD_FOCUS`, `DESCRIPTION`, `VST_NUM_MIDI_*`
- `templates/Source/PluginProcessor.cpp` — token-based `createBusesProperties()` body
- `tests/unit/test_render_context.py` — spec override, quoting, token tests
- `tests/unit/test_buses_properties.py` — new bus body preset tests
- `tests/unit/test_project_spec.py` — sidecar key order test
- `tests/integration/test_round_trip.py` — Matrix-Control CMake, buses, regenerate integration
- `tests/conftest.py` — `generate_project(allow_overwrite=...)`
- `_bmad-output/project-context.md` — third token documented

## Change Log

- 2026-07-04: Story 9.4 — spec-driven CMake characteristics, audio I/O bus generation, integration tests (309 passed)
