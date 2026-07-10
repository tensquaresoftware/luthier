# Luthier — Single QA pass (v1.0.0 — Workspace)

**Target version:** 1.0.0 (pre-publication release build)  
**Audience:** tester without technical background  
**App language:** English (labels quoted as shown on screen)  
**Estimated duration:** 3 to 5 h across three OS (or 1 to 2 h if you only rerun regressions + end of Git workflow)

> **Goal:** one read, one pass. Check `- [ ]` → `- [x]` as you go.  
> Previous detailed checklist: [checklist-qa-manual.md](checklist-qa-manual.md) (detailed archive pre-Workspace).

---

## Epic 9 — Scaffold-only smoke (v1.0.0 — 2026-07-04)

> **Product change:** no more **Open Project…** button. Luthier generates the starter project once; `.luthier.json` is **write-only** (never read back into the form).

### S9.1 — Non-empty folder guard (fresh session)

- [ ] Close and relaunch Luthier (or use a path never generated before).
- [ ] **Create New Project** → `TestLuthier` → **Generate Project** once → success.
- [ ] Close and relaunch Luthier → same destination / name → **Generate Project** → **blocked**: modal + bar *This folder already exists and is not empty…*

### S9.2 — Session regenerate (same session)

- [ ] **Create New Project** → `TestRegen` → **Generate Project** → success.
- [ ] Change **Version** (e.g. `2.0.0`) **without** closing Luthier.
- [ ] **Generate Project** → **Regenerate Project** modal (default **No**) → **Yes** → success; `.git/` preserved if present.
- [ ] Verify `CMakeLists.txt` / sources reflect the new version.

### S9.3 — Accent color (Preferences only)

- [ ] **Project** tab: **no** accent color picker.
- [ ] **Preferences** → **Luthier appearance** → another preset → theme updated on all tabs.
- [ ] **Generate Project** → open `.luthier.json`: **no** `accentColor` key.

### S9.4 — Plugin Characteristics (optional)

- [ ] **Plugin Type** **Instrument** → check **Plugin MIDI Output** → **Generate Project** → `CMakeLists.txt` reflects MIDI out (e.g. Matrix-Control).

---

## Before you begin

### On each machine

- [x] **1.0.0** build installed (same type on all three OS if possible: standalone app **or** from sources).
- [x] **JUCE** installed locally; note the path.

- macOS: /Volumes/Guillaume/Dev/SDKs/JUCE
- Windows: C:/Users/Guillaume/Dev/SDKs/JUCE
- Linux: /home/guillaume/Dev/SDKs/JUCE

- [x] Working folder for test projects (e.g. Desktop, `Téléchargements`, or `été 2026` folder — to validate accents).
- [x] **Git** available for the cross-platform section.
- [x] **About** tab: version **1.0.0**, revision date **2026-07-01**.

### Suggested test files

| Name | Usage |
| --- | --- |
| `TestLuthier` | Quick local project per OS |
| `VoyageLuthier` | Shared Git project (repo: https://github.com/tensquaresoftware/voyage-luthier or equivalent) |
| `profil-qa.json` | Export Preferences for import test |

### Luthier config locations

| OS | Folder |
| --- | --- |
| macOS | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\` |
| Linux | `~/.config/Luthier/` |

---

## Part 1 — Regression fixes (on **each** OS)

> Short block (~15 min/OS). If a point fails, note it in the [grid](#tracking-grid) before continuing.

### R1 — Paths with accents and special characters

- [x] **Preferences** → **Workspace** → **Destination folder** (host OS row) → **Choose…** → folder whose name contains **accents** (e.g. `Téléchargements`, `été 2026`).
- [x] **No** red error under the field; **Saved** badge possible.
- [x] **Create New Project** → `TestLuthier` → **Generate Project**: success without unexpected folder dialog (destination already valid).

### R2 — Messages and displayed paths

- [x] **Generate Project** → message bar: path with **`/`** (no `\` on Windows).
- [x] ~~**Open Project…**~~ *(removed v1.0.0 scaffold-only)* — see [S9.1–S9.2](#epic-9--scaffold-only-smoke-v100--2026-07-04).
- [x] **Export Preferences…** → message with **full path** of exported file.

### R3 — Confirmation modals

- [x] **Create New Project** after edit without generate → modal: **No** on the left, **Yes** on the right; **No** is the default button (accent highlight).

❌ GD: on Windows, the No button is still on the right and Yes to its left (inverted vs macOS and Linux)

- [x] **Generate Project** on a **non-empty** folder (fresh session or after app restart) → **blocked**: modal + bar *This folder already exists and is not empty…*
- [x] **Generate Project** on the **same path** after a successful Generate **in this session** → **Regenerate Project** modal: **No** / **Yes**, default **No**.

❌ GD: on Windows, the No button is still on the right and Yes to its left (inverted vs macOS and Linux)

### R4 — Generate then Create New Project

- [x] Create a valid project → **Generate Project** (success).
- [x] **Create New Project** immediately after → **no** « unsaved changes » modal.

### R5 — Error color

- [x] Trigger an error (invalid field or invalid JSON import) → red text **clearly visible** (no longer pastel).

### R6 — Corrupt preferences file (one machine is enough, preferably macOS)

- [x] Quit Luthier.
- [x] Back up `preferences.json`, replace its content with `{`.
- [x] Relaunch Luthier → **no crash**; warning in message bar; usable default values.
- [x] Restore your `preferences.json` backup.

### R7 — Linux only: icon and window

*(Skip on macOS / Windows.)*

- [ ] ❌ Launcher / taskbar: **Luthier** icon (not generic Qt icon). GD: still not working > icon still generic (broken square with white gear). Also, I don't know how to fix the app icon in the taskbar — it doesn't appear here after launch (I'm not very familiar with Linux). For info, icons of apps bundled with JUCE (e.g. Projucer, AudioPluginHost, etc.) are generic too.
- [ ] ❌ Resize and move the window → close → reopen: position and size **roughly** restored (slight WM drift acceptable). GD: size preserved but position reset near (0;0). However, AudioPluginHost size and position are well preserved between launches.

**Optional Linux — desktop shortcut:** in `dist/Luthier/`, copy `luthier.desktop` to `~/.local/share/applications/`, edit `Exec=` (absolute path to `Luthier` executable) and `Icon=` (path to `resources/icons/luthier.png` in the bundle).

✅ It works! A bit tedious to set up but I now have the app icon in the taskbar with the Luthier icon. 👍

---

## Part 2 — Functional smoke (per OS)

> Condensed workflow. Repeat steps **A** (macOS), **B** (Windows), **C** (Linux).

**Date / build:** _______________

### 2A — macOS

- [ ] Launch without crash; tabs **Project**, **Preferences**, **Templates**, **About**.
- [ ] **Preferences**: manufacturer, **Generate** codes, **Workspace** section (destination + JUCE for all three OS), accent color, export/import `profil-qa-macos.json`.
- [ ] **Create New Project** → `TestLuthier` → **VST3** + **AU** formats → **Generate Project** → folder with `CMakeLists.txt`, `.luthier.json`, `Source/`.
- [ ] **Session regenerate** (same session): change **Version** → **Generate Project** → confirm **Regenerate Project** → changes visible on disk.
- [ ] *(After app restart)* **Generate Project** on the same folder → **blocked** (non-empty folder).
- [ ] **Templates**: override `PluginProcessor.cpp` → new project → override visible → **Reset to default** → gone on new projects.
- [ ] *(Optional)* CMake build of generated project: OK.

### 2B — Windows

- [ ] Same workflow as 2A (**VST3** formats; **AU** checked must not block).
- [ ] Paths displayed with **`/`** in UI and messages.
- [ ] **Generate Project** on `TestLuthier` in a cloned Git repo: **no** WinError / access denied on `.git`.
- [ ] *(Optional)* CMake build: OK.

### 2C — Linux

- [ ] Same workflow as 2A (**VST3** formats).
- [ ] **Generate Project** with destination `~/Desktop` (or equivalent): **no** folder picker if the folder exists.
- [ ] *(Optional)* CMake build: OK.

---

## Part 3 — Cross-platform `VoyageLuthier` workflow

> If you already completed steps 2.2–2.4 of the old checklist, go directly to **3.4**. Otherwise, follow the full thread.

### 3.1 — Preparation

- [ ] Empty Git repo or `voyage-luthier` ready.
- [ ] JUCE installed on **each** machine (different local paths).

### 3.2 — Machine 1 (e.g. macOS) — Creation

- [ ] **Create New Project** → `VoyageLuthier`, version `1.0.0`, **VST3** + **Standalone** (+ **AU** if Mac).
- [ ] **Artefacts** paths filled for all three OS.
- [ ] **Generate Project**; `.luthier.json` present.
- [ ] `git init` / commit / push.

### 3.3 — Machine 2 (e.g. Windows)

- [ ] `git clone` → edit Windows **JUCE directory** in `.luthier.json` → **CMake build** (no Luthier Open).
- [ ] Verify metadata in `.luthier.json` (version `1.1.0`, **Display name** `Voyage Cross QA Windows` if committed on machine 1); build + VST3 load from system and artefacts folders.
- [ ] *(Optional — new Luthier generation)* **Empty** folder + **Create New Project** → regenerate project if you need to change metadata via Luthier; otherwise edit `.luthier.json` / `CMakeLists.txt` manually.

### 3.4 — Machine 3 (e.g. Linux)

- [ ] `git pull` → edit Linux **JUCE directory** in `.luthier.json` → **CMake build**.
- [ ] Local **Templates** override (`// Linux QA` in `PluginProcessor.h`) → **Save override** (applies to **new** Luthier generations only).
- [ ] Verify committed metadata (version `1.2.0`, **Preprocessor defs** `LINUX_QA=1` if present in repo); build + VST3 load.
- [ ] Commit project (not local templates) + push if you modified files.

### 3.5 — Return to machine 1 (e.g. macOS) — Finalization

- [ ] `git pull`.
- [ ] Verify `.luthier.json` in cloned `VoyageLuthier` (metadata); **CMake build** on Mac (host **Workspace** paths adjusted in `.luthier.json` if needed).
- [ ] **Version**: `1.2.0`; **Preprocessor defs**: `LINUX_QA=1`; **Display name**: `Voyage Cross QA Final` — reflected in repo or edited manually.
- [ ] *(No **Generate Project** on cloned folder after Luthier restart — non-empty folder; CMake build or intentional session regenerate only.)*

### 3.6 — Final cross-platform checks

- [ ] On **all three** OS: clone Git latest revision → consistent CMake build (host **Workspace** paths adjusted manually if needed).
- [ ] **Import Preferences…** from JSON exported on another machine: **Preferences** updated; **Project** form unchanged until **Create New Project**.
- [ ] Simulated Git conflict (different versions without pull): merge → `.luthier.json` reflects repo.
- [ ] **No Luthier crash** during all of Part 3.

### VoyageLuthier summary

| Step | Machine | Version | Display name |
| --- | --- | --- | --- |
| Creation | | 1.0.0 | Voyage Cross QA macOS |
| Windows | | 1.1.0 | … Windows |
| Linux | | 1.2.0 | (unchanged or …) |
| Final Mac | | 1.2.0 | … Final |

---

## Success criteria

The QA pass is **successful** if:

- [ ] Part 1 (regressions): **all** R1–R6 points OK on each relevant OS; R7 OK on Linux.
- [ ] Part 2: smoke OK on macOS, Windows, and Linux.
- [ ] Part 3: complete Git workflow (at minimum 3.5 if the rest was already done).
- [ ] No **blocking** issues open in the grid below.

---

## Tracking grid

| # | OS | Section | What were you doing? | Expected | Actual | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | blocking / annoying / minor |
| 2 | | | | | | |
| 3 | | | | | | |

**Severity:** **blocking** = cannot continue; **annoying** = painful workaround; **minor** = cosmetic.

---

## References

- [Detailed QA checklist (archive)](checklist-qa-manual.md)
- [User manual (EN)](../../../user/user-manual.md)
