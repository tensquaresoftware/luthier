# Luthier — rc4 smoke test (Windows only)

**Tag tested:** `1.0.0-rc4`  
**Date:** 10/07/2026  
**Tester:** Guillaume DUPONT  
**Audience:** supplement to the [full smoke test](./smoke-test-v1-trois-os.md) — completes **Phase B** (build/regen) and **Phase D2** not validated under rc2  
**Actual duration:** ~30 min  
**Result:** ✅ **success** (RC4-G1 through RC4-G3)

This guide covered the blocking issues under rc2/rc3 on Windows:

- **Visual Studio 2026** CMake presets (default)
- **In-session regeneration** with a `.git/` folder (`WinError 32` — fixed in rc4)
- Cursor build + plugins + **D2** (Git clone)

**History:** rc3 already fixed VS 2026 presets but WinError 32 persisted; rc4 introduces the **`Project` → `Project.old`** swap in `core/project_writer.py`.

---

## Prerequisites

| Item | Expected |
| --- | --- |
| **OS** | Windows 10+ |
| **Visual Studio** | **2026** — *Desktop development with C++* workload |
| **CMake** | **4.2+** (`cmake --version`) — required for the `windows-debug` preset |
| **Cursor / VS Code** | **CMake Tools** + **C/C++** extensions |
| **JUCE** | Full checkout (e.g. `C:/Users/Guillaume/Dev/SDKs/JUCE`) |
| **Luthier rc4** | Zip `Luthier-1.0.0-rc4-windows.zip` from [GitHub Releases](https://github.com/tensquaresoftware/luthier/releases) |
| **Master prefs** | `luthier-smoke-prefs.json` (Phase P of the full smoke test) |
| **DAW or AudioPluginHost** | To load the VST3 |

**Project path:** ASCII only (e.g. `C:/Users/Guillaume/Desktop/SmokeTest`) — no accents (MSVC limitation).

**Legacy VS 2022:** if you do **not** have VS 2026, generate the project with Luthier rc4 then select the **`windows-debug-vs2022`** preset (CMake 3.22+ is enough).

---

## R0 — Obtain rc4

| ID | Action | ✅ OK | ❌ KO | Notes |
| --- | --- | :---: | :---: | --- |
| R0-01 | Download `Luthier-1.0.0-rc4-windows.zip` | ✅ | ☐ | |
| R0-02 | Extract → launch `Luthier.exe` or `--check` | ✅ | ☐ | |
| R0-03 | **About** → version `1.0.0-rc4` | ✅ | ☐ | |

---

## W1 — Generation (quick recap)

| ID | Action | ✅ OK | ❌ KO | Notes |
| --- | --- | :---: | :---: | --- |
| W1-01 | **Import Preferences…** (Phase P master file) | ✅ | ☐ | |
| W1-02 | **Create New Project** → `SmokeTest` → **Generate Project** | ✅ | ☐ | ASCII destination — Desktop |
| W1-03 | Verify `CMakeUserPresets.json`: preset `windows-debug` = **Visual Studio 18 2026** | ✅ | ☐ | Verified with Notepad++ |

> A **new** project generated with rc4 is required — a `SmokeTest` created under rc2/rc3 keeps the old VS 2022 presets.

---

## W2 — Regeneration with `.git/` (WinError fix)

**Context:** rc2 and rc3 failed with `WinError 32` after `git init` + in-session regen. **rc4** replaces the tree with a **rename aside** (`SmokeRegen.old`) instead of deleting `.git` in place.

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| W2-01 | **Create New Project** → `SmokeRegen` → **Generate Project** | Success | ✅ | ☐ | Same Luthier session |
| W2-02 | In `SmokeRegen`: `git init`, `git add .`, `git commit -m "init"` | `.git/` created | ✅ | ☐ | |
| W2-03 | Luthier: **Version** → `2.0.0` → **Generate Project** | **Regenerate Project** modal; default **No** | ✅ | ☐ | |
| W2-04 | Choose **Yes** | Success — **no** `WinError 32` | ✅ | ☐ | |
| W2-05 | On disk: version `2.0.0` in sources; `.git/` folder **still present** | As expected | ✅ | ☐ | `git log`: init commit preserved |

> **Tip:** close Cursor/File Explorer on the folder before W2-04 to reduce Windows file locks.

**Full smoke test equivalent:** B-405, B-406.

---

## W3 — Cursor build (VS 2026)

Target project: **`SmokeTest`** (W1-02).

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| W3-01 | Cursor → **Open Folder** → `SmokeTest` | No error | ✅ | ☐ | |
| W3-02 | **CMake: Select Configure Preset** → **`windows-debug`** | Configure OK | ✅ | ☐ | |
| W3-03 | **CMake: Build** / `Ctrl+Shift+B` | Build without error | ✅ | ☐ | |
| W3-04 | **Problems** | No project errors | ✅ | ☐ | |
| W3-05 | **UAC** prompt for system VST3 copy → **Yes** | Copy logs visible | ✅ | ☐ | |
| W3-06 | **F5** Standalone | No crash | ✅ | ☐ | |
| W3-07 | VST3 in `C:/Program Files/Common Files/VST3/` + **artefacts** folder | Present; DAW load OK | ✅ | ☐ | |

**Full smoke test equivalent:** B-701 through B-706, B-801 through B-805.

---

## W4 — Phase D2 (Git clone, without Luthier)

**Prerequisites:** `VoyageLuthier` repo pushed from macOS (full smoke test D1).

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| W4-01 | `git clone` of the repo | Local copy OK | ✅ | ☐ | |
| W4-02 | Edit `.luthier.json`: **`juceDirWindows`** → local JUCE path | Saved | ✅ | ☐ | Do not reopen in Luthier |
| W4-03 | Cursor → preset **`windows-debug`** → build | No error | ✅ | ☐ | |
| W4-04 | Standalone **F5** + system VST3 + artefacts | No crash | ✅ | ☐ | |

**Full smoke test equivalent:** D-201 through D-204.

---

## rc4 success criteria (Windows)

| ID | Criterion | ✅ OK | ❌ KO |
| --- | --- | :---: | :---: |
| RC4-G1 | W2 — regen with `.git/` without WinError | ✅ | ☐ |
| RC4-G2 | W3 — build + Standalone + VST3 | ✅ | ☐ |
| RC4-G3 | W4 — Git clone + Windows build | ✅ | ☐ |

**Verdict:** all three criteria are ✅ — the full smoke test can mark **G-02**, **G-04**, and **G-05** as ✅ (see [full smoke test](./smoke-test-v1-trois-os.md)).

---

## References

- [Full 3-OS smoke test](./smoke-test-v1-trois-os.md)
- Generated project README (`SmokeTest/README.md`) — Windows VS 2026 prerequisites
