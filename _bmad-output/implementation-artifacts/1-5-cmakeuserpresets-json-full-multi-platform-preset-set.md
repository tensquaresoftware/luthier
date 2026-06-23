---
baseline_commit: c58a341d93061e7d29dfc966c38baf1840411528
---

# Story 1.5: CMakeUserPresets.json — Full Multi-Platform Preset Set

Status: done

## Story

As a JUCE developer working across macOS, Windows, and Linux,
I want a `CMakeUserPresets.json` with all platform presets pre-configured,
so that I can switch between platforms and architectures without manually editing the file.

## Acceptance Criteria

1. A generated project's `CMakeUserPresets.json` contains exactly 10 presets: `macos-debug-arm64`, `macos-release-arm64`, `macos-debug-x86_64`, `macos-release-x86_64`, `macos-debug-universal`, `macos-release-universal`, `windows-debug`, `windows-release`, `linux-debug`, `linux-release`.
2. When central artefacts mode is enabled (`copy_to_artefacts_dir=True`) with a non-empty per-OS path, each platform preset includes the corresponding artefact cache variable (`ARTEFACTS_DIR_MACOS`, `ARTEFACTS_DIR_WINDOWS`, `ARTEFACTS_DIR_LINUX`).
3. When central artefacts mode is disabled (`copy_to_artefacts_dir=False`) or the path is empty, no `ARTEFACTS_DIR_*` key appears in any preset.
4. When the "Copy to central artefacts folder" checkbox is unchecked, the three per-OS path fields are visually disabled (grayed out). *(Already implemented — verify only.)*

## Tasks / Subtasks

- [x] Replace `Templates/CMakeUserPresets.json` with the new 10-preset str.format template (AC: 1, 2, 3)
  - [x] Escape all CMake/env variable refs: `${sourceDir}` → `${{sourceDir}}`, `$env{JUCE_DIR}` → `$env{{JUCE_DIR}}`, `${hostSystemName}` → `${{hostSystemName}}`
  - [x] Add `{macosArtefactEntry}` placeholder in each macOS preset's `cacheVariables` (after `JUCE_DIR` entry)
  - [x] Add `{windowsArtefactEntry}` placeholder in each Windows preset's `cacheVariables`
  - [x] Add `{linuxArtefactEntry}` placeholder in each Linux preset's `cacheVariables`
  - [x] Include 10 matching `buildPresets` referencing their configurePreset

- [x] Move `CMakeUserPresets.json` from `_VERBATIM` to `_RENDERED` in `core/project_writer.py` (AC: 1, 2, 3)

- [x] Add artefact entry helpers to `core/render_context.py` (AC: 2, 3)
  - [x] Add `_artefact_entries(d: dict) -> dict` — returns the three `*ArtefactEntry` context keys
  - [x] Add `_artefact_entry(enabled: bool, key: str, path: str) -> str` — returns `,\n        "KEY": "path"` or `""`
  - [x] Call `context.update(_artefact_entries(d))` in `build_context()` after `_copy_config(d)`

- [x] Verify AC4: `app/pages/artefacts.py` already implements `_sync_paths_enabled()` — no code change needed, confirm it still works

## Dev Notes

### Scope — 3 files

| File | Change |
|------|--------|
| `Templates/CMakeUserPresets.json` | **REPLACE** — new 10-preset str.format template |
| `core/project_writer.py` | Move `"CMakeUserPresets.json"` from `_VERBATIM` to `_RENDERED` |
| `core/render_context.py` | Add `_artefact_entries()` + `_artefact_entry()`, call in `build_context()` |

**Do NOT touch:**
- `app/pages/artefacts.py` — AC4 already done (`_sync_paths_enabled()` disables the form on line 77)
- `core/project_spec.py` — all required fields already exist (`copy_to_artefacts_dir`, `artefacts_dir_*`)
- Any other file

### Current State of Files Being Modified

**`Templates/CMakeUserPresets.json`** — 135 lines. Currently in `_VERBATIM` (copied verbatim). Has 6 presets named `default-macos-arm64`, `default-macos-x86_64`, `default-macos-x86_64-rosetta`, `default-macos-universal`, `default-windows`, `default-linux`. No artefact path injection. No debug/release split.

**`core/project_writer.py`** — `_VERBATIM` tuple (lines 26–32) includes `"CMakeUserPresets.json"`. `_RENDERED` tuple (lines 11–17) does not. Moving the entry is the only change.

**`core/render_context.py`** — `build_context()` at line 17 already calls `_copy_config(d)` which returns `copyToArtefactsDir` as "ON"/"OFF" string. The raw bool `d["copyToArtefactsDir"]` is still intact in `d` when `_artefact_entries(d)` is called (context updates don't mutate `d`).

### Template Authoring Rules (Critical)

All CMake/environment variable references in a `_RENDERED` template must use doubled braces to survive `str.format`:
- `${sourceDir}` → `${{sourceDir}}`
- `$env{JUCE_DIR}` → `$env{{JUCE_DIR}}`
- `${hostSystemName}` → `${{hostSystemName}}`

Project value placeholders use single braces: `{macosArtefactEntry}`, etc.

### New `Templates/CMakeUserPresets.json` — Exact Content

```json
{
  "version": 4,
  "configurePresets": [
    {
      "name": "macos-debug-arm64",
      "displayName": "macOS Apple Silicon — Debug",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/macOS/ARM/Debug",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Darwin"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_OSX_ARCHITECTURES": "arm64",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{macosArtefactEntry}
      }
    },
    {
      "name": "macos-release-arm64",
      "displayName": "macOS Apple Silicon — Release",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/macOS/ARM/Release",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Darwin"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release",
        "CMAKE_OSX_ARCHITECTURES": "arm64",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{macosArtefactEntry}
      }
    },
    {
      "name": "macos-debug-x86_64",
      "displayName": "macOS Intel — Debug",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/macOS/Intel/Debug",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Darwin"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_OSX_ARCHITECTURES": "x86_64",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{macosArtefactEntry}
      }
    },
    {
      "name": "macos-release-x86_64",
      "displayName": "macOS Intel — Release",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/macOS/Intel/Release",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Darwin"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release",
        "CMAKE_OSX_ARCHITECTURES": "x86_64",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{macosArtefactEntry}
      }
    },
    {
      "name": "macos-debug-universal",
      "displayName": "macOS Universal (arm64 + x86_64) — Debug",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/macOS/Universal/Debug",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Darwin"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_OSX_ARCHITECTURES": "arm64;x86_64",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{macosArtefactEntry}
      }
    },
    {
      "name": "macos-release-universal",
      "displayName": "macOS Universal (arm64 + x86_64) — Release",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/macOS/Universal/Release",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Darwin"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release",
        "CMAKE_OSX_ARCHITECTURES": "arm64;x86_64",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{macosArtefactEntry}
      }
    },
    {
      "name": "windows-debug",
      "displayName": "Windows x64 — Debug",
      "generator": "Visual Studio 17 2022",
      "binaryDir": "${{sourceDir}}/Builds/Windows",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Windows"},
      "architecture": {"value": "x64", "strategy": "external"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{windowsArtefactEntry}
      }
    },
    {
      "name": "windows-release",
      "displayName": "Windows x64 — Release",
      "generator": "Visual Studio 17 2022",
      "binaryDir": "${{sourceDir}}/Builds/Windows",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Windows"},
      "architecture": {"value": "x64", "strategy": "external"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{windowsArtefactEntry}
      }
    },
    {
      "name": "linux-debug",
      "displayName": "Linux x86_64 — Debug",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/Linux/Debug",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Linux"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{linuxArtefactEntry}
      }
    },
    {
      "name": "linux-release",
      "displayName": "Linux x86_64 — Release",
      "generator": "Ninja",
      "binaryDir": "${{sourceDir}}/Builds/Linux/Release",
      "condition": {"type": "equals", "lhs": "${{hostSystemName}}", "rhs": "Linux"},
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release",
        "JUCE_DIR": "$env{{JUCE_DIR}}"{linuxArtefactEntry}
      }
    }
  ],
  "buildPresets": [
    {"name": "macos-debug-arm64",      "configurePreset": "macos-debug-arm64",      "configuration": "Debug"},
    {"name": "macos-release-arm64",    "configurePreset": "macos-release-arm64",    "configuration": "Release"},
    {"name": "macos-debug-x86_64",     "configurePreset": "macos-debug-x86_64",     "configuration": "Debug"},
    {"name": "macos-release-x86_64",   "configurePreset": "macos-release-x86_64",   "configuration": "Release"},
    {"name": "macos-debug-universal",  "configurePreset": "macos-debug-universal",  "configuration": "Debug"},
    {"name": "macos-release-universal","configurePreset": "macos-release-universal","configuration": "Release"},
    {"name": "windows-debug",          "configurePreset": "windows-debug",          "configuration": "Debug"},
    {"name": "windows-release",        "configurePreset": "windows-release",        "configuration": "Release"},
    {"name": "linux-debug",            "configurePreset": "linux-debug",            "configuration": "Debug"},
    {"name": "linux-release",          "configurePreset": "linux-release",          "configuration": "Release"}
  ]
}
```

**Why `{macosArtefactEntry}` goes after `JUCE_DIR` with no comma in the template:**
- When entry is empty: renders to `"JUCE_DIR": "$env{JUCE_DIR}"` — valid JSON
- When entry is non-empty (`,\n        "ARTEFACTS_DIR_MACOS": "/path"`): renders to `"JUCE_DIR": "$env{JUCE_DIR}",\n        "ARTEFACTS_DIR_MACOS": "/path"` — valid JSON

### `core/project_writer.py` — Exact Edit

Move `"CMakeUserPresets.json"` from `_VERBATIM` to `_RENDERED`:

```python
_RENDERED = (
    "CMakeLists.txt",
    "CMakeUserPresets.json",
    ".vscode/settings.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    "README.md",
)

_VERBATIM = (
    ".vscode/extensions.json",
    ".cursorrules",
    ".gitignore",
    "CMake/CopyVst3Elevated.ps1",
)
```

### `core/render_context.py` — Exact Implementation

Add after `_on_off()`:
```python
def _artefact_entries(d: dict) -> dict:
    enabled = d["copyToArtefactsDir"]
    return {
        "macosArtefactEntry": _artefact_entry(enabled, "ARTEFACTS_DIR_MACOS", d.get("artefactsDirMacos", "")),
        "windowsArtefactEntry": _artefact_entry(enabled, "ARTEFACTS_DIR_WINDOWS", d.get("artefactsDirWindows", "")),
        "linuxArtefactEntry": _artefact_entry(enabled, "ARTEFACTS_DIR_LINUX", d.get("artefactsDirLinux", "")),
    }


def _artefact_entry(enabled: bool, key: str, path: str) -> str:
    if not enabled or not path:
        return ""
    return f',\n        "{key}": "{path}"'
```

Update `build_context()` — add one line after `_copy_config(d)`:
```python
def build_context(spec: ProjectSpec) -> dict:
    d = spec.to_dict()
    flags = plugin_settings.flags_for_type(d["pluginType"])
    context = {key: d[key] for key in _VALUE_KEYS}
    context.update(flags)
    context.update(_categories(flags))
    context.update(_copy_config(d))
    context.update(_artefact_entries(d))   # ← NEW
    context["bundleId"] = plugin_settings.bundle_id(d["manufacturerName"], d["projectName"])
    context.update(_extra_fields(d))
    return context
```

**Why call after `_copy_config(d)` instead of before**: `_copy_config(d)` mutates `context` but never `d`. `d["copyToArtefactsDir"]` remains a bool throughout — safe to consume in `_artefact_entries(d)` at any point.

### Clean Code Metrics Verification

| Function | Lines | Params | Complexity |
|----------|-------|--------|------------|
| `build_context()` (updated) | 10 | 1 | 1 |
| `_artefact_entries()` | 5 | 1 | 1 |
| `_artefact_entry()` | 4 | 3 | 2 |

All within limits. ✓

### AC4 — Already Implemented (Verify Only)

`app/pages/artefacts.py:76-77` — `_sync_paths_enabled()` calls `self._form.setEnabled(self._checks["copyToArtefactsDir"].isChecked())`. This disables the entire `ValidatedForm` (all 3 path fields) when the checkbox is unchecked. Connected at line 73. **No code change needed.**

### Windows binaryDir — Intentional Duplicate

`windows-debug` and `windows-release` share the same `binaryDir` (`${{sourceDir}}/Builds/Windows`). This is correct: Visual Studio 17 2022 is a **multi-config generator** — it manages Debug/Release inside one build tree. Ninja (macOS/Linux) is single-config, hence separate dirs.

### Known Deferred Issues (Do Not Fix Here)

- Windows artefact paths with backslashes (`\`) may contain escape sequences in JSON context — pre-existing (same issue as in CMakeLists.txt). Do not add escaping logic; it would require escaping in `_artefact_entry` but this issue predates the story. Leave for Epic 3/4.

### Testing

No automated tests yet (Epic 3). Manual verification:

1. Run `.venv/bin/python main.py`
2. Set artefacts paths in Preferences: `artefactsDirMacos=/Users/me/Plugins`, `artefactsDirWindows=C:\Plugins`, `artefactsDirLinux=/home/me/plugins`; enable "Copy to central artefacts folder"
3. Generate a project → open `CMakeUserPresets.json`:
   - Exactly 10 `configurePresets` with correct names (AC1) ✓
   - Each macOS preset has `"ARTEFACTS_DIR_MACOS": "/Users/me/Plugins"` (AC2) ✓
   - Each Windows preset has `"ARTEFACTS_DIR_WINDOWS": "C:\\Plugins"` (AC2) ✓
   - Each Linux preset has `"ARTEFACTS_DIR_LINUX": "/home/me/plugins"` (AC2) ✓
4. Uncheck "Copy to central artefacts folder" → regenerate → no `ARTEFACTS_DIR_*` in any preset (AC3) ✓
5. Verify UI: path fields are grayed out when checkbox is off (AC4) ✓
6. `.venv/bin/python main.py --check` exits 0

### References

- Story 1.5 ACs: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md) §Story 1.5
- Template authoring rules: [_bmad-output/project-context.md](_bmad-output/project-context.md) §Template Authoring
- Current template: [Templates/CMakeUserPresets.json](Templates/CMakeUserPresets.json)
- Writer (VERBATIM/RENDERED tuples): [core/project_writer.py](core/project_writer.py)
- Render context (build_context): [core/render_context.py](core/render_context.py)
- AC4 already done: [app/pages/artefacts.py:72-77](app/pages/artefacts.py)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Story spec showed JSON template with single structural braces, but `str.format` requires all literal `{`/`}` to be doubled. Fixed by doubling every structural JSON brace in the template (consistent with `.vscode/*.json` templates already in the project).

### Completion Notes List

- `Templates/CMakeUserPresets.json` replaced: 6 verbatim presets → 10 `str.format` presets (6 macOS + 2 Windows + 2 Linux). All CMake variable refs doubled. Three `{*ArtefactEntry}` placeholders injected after each `JUCE_DIR` entry.
- `core/project_writer.py`: `CMakeUserPresets.json` moved from `_VERBATIM` to `_RENDERED`.
- `core/render_context.py`: `_artefact_entries()` + `_artefact_entry()` added; `build_context()` updated with one `context.update(_artefact_entries(d))` call.
- AC4 verified: `app/pages/artefacts.py:76-77` — `_sync_paths_enabled()` already wired up, no change needed.
- All ACs validated via Python assertions and `--check` exit 0.

### File List

- `Templates/CMakeUserPresets.json`
- `core/project_writer.py`
- `core/render_context.py`

### Review Findings

- [x] [Review][Defer] Windows path backslashes break rendered JSON [`core/render_context.py:63`] — deferred, pre-existing (story spec §Known Deferred; same issue as CMakeLists.txt Epic 3/4)
- [x] [Review][Defer] `from_dict` bool coercion — string `"false"` is truthy in `_artefact_entries` [`core/project_spec.py:70`, `core/render_context.py:52`] — deferred, pre-existing (already tracked in deferred-work from stories 1-1/1-2; amplified by new artefact entry path)
- [x] [Review][Defer] `copyToArtefactsDir` ON with all empty paths — presets omit cache vars but CMakeLists still emits ON [`core/render_context.py:51-57`] — deferred, pre-existing cross-file inconsistency; AC3-compliant for presets
- [x] [Review][Defer] No post-render JSON validation of CMakeUserPresets output [`core/rendering.py`] — deferred, pre-existing; Epic 3 test infrastructure
