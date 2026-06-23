---
baseline_commit: c3bb7bf
---

# Story 1.4: CMakeLists.txt Template Consolidation

Status: done

## Story

As a JUCE developer,
I want all project configuration in a single `CMakeLists.txt`,
so that I can read or edit my project's configuration from one file without understanding two separate CMake files.

## Acceptance Criteria

1. A generated project contains a single `CMakeLists.txt` with all named CMake variables at the top (copy settings, artefacts paths) — no `project-configuration.cmake` is generated.
2. When `preprocessorDefinitions` is empty on the `ProjectSpec`, no `target_compile_definitions` block (beyond the JUCE built-in one) appears in `CMakeLists.txt`.
3. When `headerSearchPaths` is empty on the `ProjectSpec`, no `target_include_directories` block appears in `CMakeLists.txt`.
4. `Templates/project-configuration.cmake` is deleted and never written to generated projects.

## Tasks / Subtasks

- [x] Update `Templates/CMakeLists.txt` — inline the copy configuration (AC: 1, 4)
  - [x] Remove lines 50–51: `# Plugin copy configuration (edit project-configuration.cmake to customize)` and `include(project-configuration.cmake)`
  - [x] Insert the copy-config block in place (see Dev Notes for exact content and position)
  - [x] Verify AC2: generate with empty `preprocessorDefinitions` → no second `target_compile_definitions` block in output
  - [x] Verify AC3: generate with empty `headerSearchPaths` → no `target_include_directories` block in output

- [x] Delete `Templates/project-configuration.cmake` (AC: 4)

- [x] Update `core/project_writer.py` — remove file from render list (AC: 4)
  - [x] Remove `"project-configuration.cmake"` from `_RENDERED` tuple

- [x] Update `core/project_reader.py` — read copy settings from consolidated file (system integrity)
  - [x] Change `_parse_build_settings()`: check `project-configuration.cmake` first (backward compat with legacy projects), fall back to `CMakeLists.txt` when absent
  - [x] See Dev Notes for exact implementation

## Dev Notes

### Scope — 4 files

| File | Change |
|------|--------|
| `Templates/CMakeLists.txt` | Replace `include(project-configuration.cmake)` with inlined content |
| `Templates/project-configuration.cmake` | **DELETE** |
| `core/project_writer.py` | Remove `"project-configuration.cmake"` from `_RENDERED` |
| `core/project_reader.py` | Update `_parse_build_settings()` to fall back to `CMakeLists.txt` |

**Do NOT touch in this story:**
- `core/render_context.py` — already provides `copyToSystemFolders`, `copyToArtefactsDir`, `artefactsDirWindows/Macos/Linux` keys; no changes needed
- `core/project_spec.py`, `core/project_generator.py`, `core/preferences.py` — out of scope
- Any `app/` file — out of scope

### Current State of Files Being Modified

**`Templates/CMakeLists.txt`** — 302 lines. Lines 50–51 do:
```cmake
# Plugin copy configuration (edit project-configuration.cmake to customize)
include(project-configuration.cmake)
```
This pulls in `project-configuration.cmake` which defines `COPY_TO_SYSTEM_FOLDERS`, `COPY_TO_ARTEFACTS_DIR`, and the three `ARTEFACTS_DIR_*` variables. The rest of `CMakeLists.txt` references these CMake variables (e.g. `${{COPY_TO_SYSTEM_FOLDERS}}` at line 117, `${{COPY_TO_ARTEFACTS_DIR}}` at lines 174 and 213). After story 1.4, those definitions move inline.

**`Templates/project-configuration.cmake`** — 38 lines. Contains:
- Header comment block describing the two options (lines 1–24)
- `set(USER_COPY_TO_SYSTEM_FOLDERS {copyToSystemFolders})` — str.format placeholder
- `set(USER_COPY_TO_ARTEFACTS_DIR {copyToArtefactsDir})` — str.format placeholder
- `set(COPY_TO_SYSTEM_FOLDERS ...)` CACHE BOOL
- `set(COPY_TO_ARTEFACTS_DIR ...)` CACHE BOOL
- `set(ARTEFACTS_DIR_WINDOWS "{artefactsDirWindows}")` — str.format placeholder
- `set(ARTEFACTS_DIR_MACOS   "{artefactsDirMacos}")` — str.format placeholder
- `set(ARTEFACTS_DIR_LINUX   "{artefactsDirLinux}")` — str.format placeholder

**`core/project_writer.py`** — `_RENDERED` tuple at lines 11–18 includes `"project-configuration.cmake"`. Remove that entry. The tuple will still contain `CMakeLists.txt` and the four `.vscode/*.json` / `README.md` files.

**`core/project_reader.py`** — `_parse_build_settings(project_dir)` at lines 109–120 reads exclusively from `project-configuration.cmake`. After story 1.4, newly generated projects won't have that file; the function must fall back to `CMakeLists.txt`. `_parse_set_vars()` is reusable as-is — it extracts all `set(KEY VALUE)` calls from any CMake text. The keys `USER_COPY_TO_SYSTEM_FOLDERS`, `USER_COPY_TO_ARTEFACTS_DIR`, `ARTEFACTS_DIR_WINDOWS/MACOS/LINUX` are unique in `CMakeLists.txt`, so there is no collision risk.

### `Templates/CMakeLists.txt` — Exact Edit

Replace lines 50–51:
```cmake
# Plugin copy configuration (edit project-configuration.cmake to customize)
include(project-configuration.cmake)
```

With:
```cmake
# =============================================================================
# PLUGIN COPY CONFIGURATION
# COPY_TO_SYSTEM_FOLDERS: ON/OFF — copies plugins to standard DAW scan locations
#   Windows: VST3 → C:\Program Files\Common Files\VST3\ (UAC prompt)
#   macOS: AU → ~/Library/Audio/Plug-Ins/Components/, VST3 → ~/Library/Audio/Plug-Ins/VST3/
#   Linux: VST3 → ~/.vst3/
# COPY_TO_ARTEFACTS_DIR: ON/OFF — copies build outputs to a central custom folder
#   (ARTEFACTS_DIR_WINDOWS/MACOS/LINUX, organized by platform and architecture)
# Override at configure time: cmake .. -DUSER_COPY_TO_ARTEFACTS_DIR=ON
# =============================================================================

set(USER_COPY_TO_SYSTEM_FOLDERS {copyToSystemFolders})
set(USER_COPY_TO_ARTEFACTS_DIR {copyToArtefactsDir})

set(COPY_TO_SYSTEM_FOLDERS ${{USER_COPY_TO_SYSTEM_FOLDERS}} CACHE BOOL "Copy plugins to system folders after build (all OS)")
set(COPY_TO_ARTEFACTS_DIR ${{USER_COPY_TO_ARTEFACTS_DIR}} CACHE BOOL "Copy build outputs to central artefacts folder (organized by platform/architecture)")

set(ARTEFACTS_DIR_WINDOWS "{artefactsDirWindows}")
set(ARTEFACTS_DIR_MACOS   "{artefactsDirMacos}")
set(ARTEFACTS_DIR_LINUX   "{artefactsDirLinux}")
```

Template authoring rules apply: CMake variable references use `${{VAR}}` (double braces survive `str.format`); project values use single braces `{key}`.

### `core/project_writer.py` — Exact Edit

```python
_RENDERED = (
    "CMakeLists.txt",
    # "project-configuration.cmake",  ← REMOVE THIS LINE
    ".vscode/settings.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    "README.md",
)
```

Result:
```python
_RENDERED = (
    "CMakeLists.txt",
    ".vscode/settings.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    "README.md",
)
```

### `core/project_reader.py` — Exact Implementation

Replace `_parse_build_settings()` at lines 109–120:

```python
def _parse_build_settings(project_dir: Path) -> dict:
    config = project_dir / "project-configuration.cmake"
    source = config if config.exists() else project_dir / "CMakeLists.txt"
    if not source.exists():
        return {}
    cfg = _parse_set_vars(source.read_text(encoding="utf-8"))
    return {
        "copyToSystemFolders": _bool(cfg, "USER_COPY_TO_SYSTEM_FOLDERS", "COPY_TO_SYSTEM_FOLDERS"),
        "copyToArtefactsDir": _bool(cfg, "USER_COPY_TO_ARTEFACTS_DIR", "COPY_TO_ARTEFACTS_DIR"),
        "artefactsDirWindows": cfg.get("ARTEFACTS_DIR_WINDOWS", ""),
        "artefactsDirMacos": cfg.get("ARTEFACTS_DIR_MACOS", ""),
        "artefactsDirLinux": cfg.get("ARTEFACTS_DIR_LINUX", ""),
    }
```

Clean code: 10 lines, complexity 2. Backward-compatible: legacy projects with `project-configuration.cmake` still parse correctly. The `_parse_set_vars` regex matches `set(KEY VALUE)` across any CMake text; the five target keys are unique in `CMakeLists.txt`.

### ACs 2 & 3 — Already Implemented, Verification Only

`render_context._definitions_block()` returns `""` when `preprocessorDefinitions` is empty.
`render_context._include_block()` returns `""` when `headerSearchPaths` is empty.

Both return values are injected via `{extraDefinitionsBlock}` and `{headerSearchPathsBlock}` at line 160 of `CMakeLists.txt`. The template produces no block when the value is `""`. These ACs require no code change — only manual verification during testing.

### Testing

No automated test infrastructure exists yet (Epic 3). Manual verification:

1. Run the app: `.venv/bin/python main.py`
2. Fill a project with `copyToSystemFolders=ON`, `copyToArtefactsDir=OFF`, empty `headerSearchPaths`, empty `preprocessorDefinitions`
3. Generate → inspect output directory:
   - `CMakeLists.txt` exists; `project-configuration.cmake` does NOT exist (AC1, AC4)
   - `CMakeLists.txt` contains `set(USER_COPY_TO_SYSTEM_FOLDERS ON)` (AC1)
   - No second `target_compile_definitions` block (AC2)
   - No `target_include_directories` block (AC3)
4. Click "Open Project…" on the generated directory → all fields reload including copy settings (reader integration)
5. Headless check: `.venv/bin/python main.py --check` exits 0

### What Must Be Preserved

- All `${{VAR}}` CMake variable references in `CMakeLists.txt` remain unchanged — the double-brace escaping is load-bearing for `str.format`
- The `{copyToSystemFolders}` etc. str.format placeholders must appear in the NEW inline block exactly as they appear in `project-configuration.cmake` today — `render_context._copy_config()` already provides these keys
- `CMakeLists.txt` must remain a complete, valid CMake file that configures the JUCE plugin without `project-configuration.cmake`

### Previous Story Intelligence

From story 1-3 (done):
- Prefs save/update: `MainWindow` is the only caller of `prefs.update(spec)` + `prefs.save()` — no impact on this story
- `ProjectPage.spec()` assembles `copyToSystemFolders`, `copyToArtefactsDir`, artefacts dirs from `_artefacts.values()` → these flow through to `render_context.build_context(spec)` → `_copy_config()` → template placeholders. Chain unchanged.

From story 1-2 (done):
- `ProjectWriter._write_all()` iterates `_RENDERED`; removing one entry from the tuple is sufficient to stop writing the file
- `_write_sidecar()` writes `.luthier.json` — unaffected

From story 1-1 (done):
- `ProjectSpec` fields `copy_to_system_folders`, `copy_to_artefacts_dir`, `artefacts_dir_windows/macos/linux` exist and are serialized by `to_dict()` with camelCase keys — no changes needed

### Architecture Rules

| Rule | How enforced here |
|------|-----------------|
| FR2: Single `CMakeLists.txt` | `project-configuration.cmake` removed from `_RENDERED` and `Templates/` |
| AD-8: `core/` never imports `app/` | Not affected; all changes in `core/` and `Templates/` |
| Template authoring: `${{VAR}}` | Inlined content uses double braces for CMake vars |
| Clean Code: function ≤ 15 lines | `_parse_build_settings()`: 10 lines ✓ |

### References

- Story 1.4 ACs: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md) §Story 1.4
- Template authoring rules: [_bmad-output/project-context.md](_bmad-output/project-context.md) §Template Authoring
- Current template files: [Templates/CMakeLists.txt](Templates/CMakeLists.txt), [Templates/project-configuration.cmake](Templates/project-configuration.cmake)
- Current writer: [core/project_writer.py](core/project_writer.py)
- Current reader: [core/project_reader.py](core/project_reader.py)
- Render context (no changes): [core/render_context.py](core/render_context.py)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — all 4 tasks applied cleanly on first pass.

### Completion Notes List

- Replaced `include(project-configuration.cmake)` (lines 50–51) with the full inline copy-config block in `Templates/CMakeLists.txt`. Double-brace escaping (`${{VAR}}`) preserved for `str.format` compatibility.
- Deleted `Templates/project-configuration.cmake`.
- Removed `"project-configuration.cmake"` from `_RENDERED` tuple in `core/project_writer.py`.
- Updated `_parse_build_settings()` in `core/project_reader.py`: prefers `project-configuration.cmake` when it exists (backward compat), falls back to `CMakeLists.txt` otherwise.
- All 4 ACs verified programmatically: AC1 (inline vars present), AC2 (no extra `target_compile_definitions`), AC3 (no `target_include_directories`), AC4 (`project-configuration.cmake` absent from output). Reader round-trip confirmed (`copyToSystemFolders`, `copyToArtefactsDir`, all three `artefactsDir*` fields correct).
- Headless check passes: `main.py --check` exits cleanly.

### File List

- `Templates/CMakeLists.txt` — modified (inline copy-config block replaces `include(...)`)
- `Templates/project-configuration.cmake` — deleted
- `core/project_writer.py` — modified (`_RENDERED` tuple)
- `core/project_reader.py` — modified (`_parse_build_settings` fallback logic)

### Review Findings

- [x] [Review][Patch] Docstring obsolète dans `project_reader.py` [core/project_reader.py:1-7]
- [x] [Review][Defer] `CACHE BOOL` sans `FORCE` — valeurs de copy-settings non mises à jour si re-génération [Templates/CMakeLists.txt] — deferred, pre-existing
- [x] [Review][Defer] Chemins Windows avec backslashes non échappés dans les placeholders artefact dir [Templates/CMakeLists.txt:65-67] — deferred, pre-existing
- [x] [Review][Defer] `OSError` non capturé sur `source.read_text()` [core/project_reader.py:114] — deferred, pre-existing
- [x] [Review][Defer] Aucun test couvrant le fallback du reader — deferred, Epic 3 planifié

## Change Log

- 2026-06-23: Story created — CMakeLists.txt template consolidation, eliminating project-configuration.cmake
- 2026-06-23: Story implemented — inlined copy config into CMakeLists.txt, deleted project-configuration.cmake, updated writer and reader
