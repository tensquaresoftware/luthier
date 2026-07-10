# Luthier — Manual QA checklist

**Target product version:** 1.0.0  
**Audience:** testers without particular technical background  
**App language:** the Luthier interface is in **English**; button labels below use the exact on-screen text.

---

## How to use this document

1. **Read first** the [Before you begin](#before-you-begin) section.
2. **Part 1** — check boxes in **each** block: [A — macOS](#a--macos), [B — Windows](#b--windows), [C — Linux](#c--linux).
3. **Part 2** — once, with **all three machines** (or two machines + a VM), follow the « travelling project » workflow (Git, cross-platform CMake builds — **without** reopening in Luthier since v1.0.0 scaffold-only).
4. Check each box: `- [ ]` → `- [x]` when OK.
5. Note problems in the [Issue tracking grid](#issue-tracking-grid) at the bottom.

**What you are testing:** Luthier **generates** **JUCE starter projects** (VST/AU plugins and Standalone audio/MIDI apps). Luthier does **not** compile the plugin for you — you mainly verify the Luthier app itself. If you want to go further, a quick CMake build on each OS is a plus (optional step at the end of each block).

---

## Before you begin

### On each machine (macOS, Windows, Linux)

- [x] Luthier is installed (standalone app **or** version launched from sources — keep the **same method** on all three OS if possible).
- [x] You have a copy of **JUCE** somewhere on disk (downloaded or cloned folder).
- [x] You know where you put your projects (Desktop, Documents, etc.).
- [x] For **Part 2**: **Git** is installed and you have an empty repo (GitHub, GitLab, USB key with repo, etc.) to sync the project between machines.

### Conventions for this checklist

| Name                   | Meaning                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------- |
| **Local test project** | Suggested name: `TestLuthier` — a project created on one machine only                                 |
| **Travelling project**     | Suggested name: `VoyageLuthier` — the project shared between OS via Git                                      |
| **Test profile**       | File exported per OS: `profil-qa-macos.json`, `profil-qa-windows.json`, `profil-qa-linux.json`       |
| **Message bar**  | The band at the bottom of the window (above buttons): accent color = OK, red = error |

---

# Part 1 — Tests on each system

Each system has **its own block** (A, B, or C) with the same numbered steps 1 through 9. Check boxes **in all three blocks** before Part 2.

Steps are identical from one OS to another; only specific notes (installation, paths, formats) change.

---

## Epic 9 — Scaffold-only smoke (v1.0.0 — 2026-07-04)

> **Open Project…** removed. See also [checklist-qa-passe-unique.md § Epic 9](checklist-qa-passe-unique.md#epic-9--scaffold-only-smoke-v100--2026-07-04) for S9.1–S9.4 scenario details (non-empty guard, session regenerate, accent Preferences-only, characteristics).

- [ ] **Project** action bar: **Create New Project** and **Generate Project** only (no **Open Project…**).
- [ ] Non-empty folder guard after app restart (S9.1).
- [ ] Session regenerate with **Regenerate Project** confirm (S9.2).
- [ ] Accent via **Luthier appearance** (**Preferences** only); no `accentColor` in `.luthier.json` (S9.3).
- [ ] **Plugin Type** **Instrument** + **Plugin MIDI Output** → **Generate Project** → consistent CMake intent (S9.4, optional — see [single-pass S9.4](checklist-qa-passe-unique.md#s94--plugin-characteristics-optional)).

---

## A — macOS

**Date:** 2026-06-29
**Luthier version (About tab):** 1.0.0
**Install:** ✅ standalone app (`Luthier.app`) ☐ from sources

### A1 — First launch and window

- [x] Luthier opens without crash (if app is unsigned: authorization in **System Settings** if macOS asks).
- [x] You see four tabs: **Project**, **Preferences**, **Templates**, **About**.
- [x] **Project** tab is active at startup.
- [x] Resize the window, close Luthier, reopen: size and position are **roughly** restored (or window opens centered if screen changed — acceptable).
- [x] **About** tab: displayed version matches what you are testing.

### A2 — Default settings (Preferences tab)

**Identity and paths**

- [x] **Preferences** tab → **Identity** section: change **Manufacturer** (e.g. `QA Studio`).
- [x] Click **Generate** next to manufacturer / plugin codes: valid codes appear.
- [x] **Paths** section: **Choose…** for **Destination folder** → choose an existing folder.
- [x] **Choose…** for **JUCE directory** → point to your JUCE installation.

**Auto-save**

- [x] After a valid change, a small **Saved** badge flashes on the field.
- [x] Close and reopen Luthier: your **Preferences** values are still there.

**Accent color**

- [x] At top of **Preferences**, change **Luthier Accent Color**: tabs and buttons change color immediately (while you stay on this tab).
- [x] Switch to **Project** tab: picker may still show the **old** color — this is normal (the two tabs are not synced live).
- [x] Return to **Preferences**: new color is selected there.
- [x] Close and reopen Luthier: color chosen in **Preferences** is still there; both pickers take this value at startup.
- [x] **Create New Project**: **Project** picker takes color saved in **Preferences**.

**Profile export / import**

- [x] **Export Preferences…** → save `profil-qa-macos.json` (Desktop or Documents).
- [x] Success message in message bar (type *Preferences exported to…*).

📌 **GD note**: only the JSON filename is mentioned in the message, not the full path.

- [x] Change **Manufacturer** (e.g. `Autre Nom`).
- [x] **Import Preferences…** → choose `profil-qa-macos.json`.
- [x] Previous profile returns (manufacturer, color, paths).
- [x] **Invalid file test:** import a text file renamed to `.json` → error message, **your previous settings remain**.

### A3 — Create first project (Project tab)

- [x] **Create New Project** → message like *New project — defaults from Preferences.*
- [x] Fields match your **Preferences** (manufacturer, paths, checked formats).
- [x] **Project name**: `TestLuthier`.
- [x] **Display name**: `Test Luthier QA` (with spaces — allowed).
- [x] Leave or adjust **Version**, codes, **Destination folder**, **JUCE directory**.
- [x] **Plugin Type**: **Instrument** (you will retest another type in A5).
- [x] **Formats**: check **VST3** and **AU** (Audio Unit — Mac specific).
- [x] **Generate Project** becomes clickable when everything is valid.
- [x] Click **Generate Project** → success message with created folder path.
- [x] In **Finder**: `TestLuthier` folder contains `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validation (button stays grayed while invalid)**

- [x] Empty **Project name** or starting with a digit → error displayed.
- [x] All formats unchecked → **Generate Project** disabled.
- [x] **Manufacturer code** all lowercase → error (need one uppercase then lowercase).

### A4 — Session regenerate and generate guard *(replaces « Reopen » — Epic 9 archive)*

- [x] Change **Version** (e.g. `1.0.2`) **without** generating.
- [x] **Create New Project** → confirmation box → **No**: your changes remain; repeat → **Yes**: form reset.
- [ ] **Generate Project** on `TestLuthier` (current session) after **Version** change → **Regenerate Project** modal → **Yes** → files updated; `.git/` preserved.
- [ ] Restart Luthier → **Generate Project** on same folder → **blocked** (*folder not empty*).

> *Pre-Epic 9 archive: **Open Project…** / reopen steps no longer apply.*

### A5 — Project variants

- [x] **Create New Project** → **Plugin Type**: **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [x] **Create New Project** → **VST3** only (uncheck **Standalone**) → `TestLuthierVST3` → OK.
- [x] **Compilation** → **Preprocessor defs**: `QA_FLAG=1` → project `TestLuthierDefs` → verify line in generated `CMakeLists.txt` (no reopen in Luthier).
- [x] Project with **AU** checked → generation OK.

### A6 — Central binaries folder (optional)

- [x] **Artefacts** section: check **Copy to central artefacts folder**.
- [x] **macOS** path: **Choose…** (e.g. `~/Documents/ArtefactsQA`).
- [x] **Windows** and **Linux** fields: enter plausible paths for later (e.g. `D:/ArtefactsQA`, `/home/vous/ArtefactsQA`).
- [x] Regenerate `TestLuthier` → no validation error.

### A7 — Code templates (Templates tab)

- [x] File list: `PluginProcessor.cpp`, `.gitignore`, etc.
- [x] `PluginProcessor.cpp` → comment `// QA override macOS` → **Save override**.

📌 **GD note**: Should the message "Override active — used for new projects" appear in the message bar instead of under the source editor?

- [x] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → comment visible in `Source/PluginProcessor.cpp`.
- [x] **Reset to default** → regeneration: comment gone from new projects.

📌 **GD note**: does clicking **Reset to default** require clicking **Save override**?

- [x] **Load from file…** → external `.cpp` file → **Save override** to keep.
- [x] Unreadable or huge file → error message or clean behavior, no crash.

### A8 — Three settings do not mix

- [x] **Preferences**: `Manufacturer` = `Profil Global`.
- [x] **Project** open on `TestLuthier`: project manufacturer may differ — this is normal.
- [x] Change **Preferences** → **Project** unchanged.
- [x] **Import Preferences…** (`Import Test`) → **Project** unchanged.
- [x] **Create New Project** → form takes `Import Test`.
- [x] **Templates** changes visible in existing project only after **Generate Project**.

### A9 — CMake build (optional)

> Only if Xcode or CMake + compiler are installed.

- [x] Open generated folder (Xcode, VS Code, etc.).
- [x] Follow project `README.md`: configure + build.
- [x] Result: ✅ OK ☐ failure (toolchain) ☐ not tested

---

## B — Windows

**Date:** 2026-06-29  
**Luthier version (About tab):** 1.0.0  
**Install:** ✅ standalone app (`Luthier.exe`) ☐ from sources

### B1 — First launch and window

- [x] Luthier opens without crash (SmartScreen possible: **More info** → run for local build).
- [x] You see four tabs: **Project**, **Preferences**, **Templates**, **About**.
- [x] **Project** tab is active at startup.
- [x] Resize the window, close Luthier, reopen: size and position are **roughly** restored (or window opens centered if screen changed — acceptable).
- [x] **About** tab: displayed version matches what you are testing.

### B2 — Default settings (Preferences tab)

**Identity and paths**

- [x] **Preferences** tab → **Identity** section: change **Manufacturer** (e.g. `QA Studio`).
- [x] Click **Generate** next to manufacturer / plugin codes: valid codes appear.
- [x] **Paths** section: **Choose…** for **Destination folder** → choose an existing folder.

📌 **GD note**: I pointed to my Téléchargements folder, an error message says accents are forbidden > this should change, accented folder (and file) names are valid.

- [x] **Choose…** for **JUCE directory** → point to your JUCE installation.
- [x] When leaving a path field, `\` become `/` in display (normal on Windows).

📌 **GD note**: I actually see `/` directly.

**Auto-save**

- [x] After a valid change, a small **Saved** badge flashes on the field.
- [x] Close and reopen Luthier: your **Preferences** values are still there.

**Accent color**

- [x] At top of **Preferences**, change **Luthier Accent Color**: tabs and buttons change color immediately (while you stay on this tab).
- [x] Switch to **Project** tab: picker may still show the **old** color — this is normal (the two tabs are not synced live).
- [x] Return to **Preferences**: new color is selected there.
- [x] Close and reopen Luthier: color chosen in **Preferences** is still there; both pickers take this value at startup.
- [x] **Create New Project**: **Project** picker takes color saved in **Preferences**.

**Profile export / import**

- [x] **Export Preferences…** → save `profil-qa-windows.json`.
- [x] Success message in message bar (type *Preferences exported to…*).

📌 **GD note**: only the JSON filename is mentioned in the message, not the full path.

- [x] Change **Manufacturer** (e.g. `Autre Nom`).
- [x] **Import Preferences…** → choose `profil-qa-windows.json`.
- [x] Previous profile returns (manufacturer, color, paths).
- [x] **Invalid file test:** import a text file renamed to `.json` → error message, **your previous settings remain**.

### B3 — Create first project (Project tab)

- [x] **Create New Project** → message like *New project — defaults from Preferences.*
- [x] Fields match your **Preferences** (manufacturer, paths, checked formats).
- [x] **Project name**: `TestLuthier`.
- [x] **Display name**: `Test Luthier QA` (with spaces — allowed).
- [x] Leave or adjust **Version**, codes, **Destination folder**, **JUCE directory**.
- [x] **Plugin Type**: **Instrument** (you will retest another type in B5).
- [x] **Formats**: check **VST3** (and **Standalone** if you want); **AU** may stay checked for future Mac use — generation must **not** fail.
- [x] **Generate Project** becomes clickable when everything is valid.
- [x] Click **Generate Project** → success message with created folder path.
- [x] In **File Explorer**: `TestLuthier` folder contains `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validation (button stays grayed while invalid)**

- [x] Empty **Project name** or starting with a digit → error displayed.
- [x] All formats unchecked → **Generate Project** disabled.
- [x] **Manufacturer code** all lowercase → error (need one uppercase then lowercase).

### B4 — Session regenerate and generate guard *(replaces « Reopen » — Epic 9 archive)*

- [x] Change **Version** (e.g. `1.0.2`) **without** generating.
- [x] **Create New Project** → confirmation box → **No**: your changes remain; repeat → **Yes**: form reset.

📌 **GD note**: Yes button is on the left and No on the right in the modal, on macOS it's the opposite: I prefer the macOS display order

- [ ] **Generate Project** on `TestLuthier` (current session) → **Regenerate Project** modal → **Yes** → success.
- [ ] Restart Luthier → **Generate Project** on same folder → **blocked** (*folder not empty*).

> *Pre-Epic 9 archive: **Open Project…**, `Loaded … from` message, move + reopen — no longer apply.*

### B5 — Project variants

- [x] **Create New Project** → **Plugin Type**: **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [x] **Create New Project** → **VST3** only (uncheck **Standalone**) → `TestLuthierVST3` → OK.
- [x] **Compilation** → **Preprocessor defs**: `QA_FLAG=1` → project `TestLuthierDefs` → verify line in generated `CMakeLists.txt` (no reopen in Luthier).
- [x] **AU** checked (even if you won't build on Mac) → generation OK anyway.

### B6 — Central binaries folder (optional)

- [x] **Artefacts** section: check **Copy to central artefacts folder**.
- [x] **Windows** path: **Choose…** (e.g. `C:/Users/Vous/Documents/ArtefactsQA`).
- [x] **macOS** and **Linux** fields: enter plausible paths (e.g. `/Users/vous/Documents/ArtefactsQA`, `/home/vous/ArtefactsQA`).
- [x] Regenerate `TestLuthier` → no validation error.

### B7 — Code templates (Templates tab)

- [x] File list: `PluginProcessor.cpp`, `.gitignore`, etc.
- [x] `PluginProcessor.cpp` → comment `// QA override Windows` → **Save override**.

📌 **GD note**: Should the message "Override active — used for new projects" appear in the message bar instead of under the source editor?

- [x] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → comment visible in `Source/PluginProcessor.cpp`.
- [x] **Reset to default** → regeneration: comment gone from new projects.

📌 **GD note**: does clicking **Reset to default** require clicking **Save override**?

- [x] **Load from file…** → external `.cpp` file → **Save override** to keep.
- [x] Unreadable or huge file → error message or clean behavior, no crash.

### B8 — Three settings do not mix

- [x] **Preferences**: `Manufacturer` = `Profil Global`.
- [x] **Project** open on `TestLuthier`: project manufacturer may differ — this is normal.
- [x] Change **Preferences** → **Project** unchanged.
- [x] **Import Preferences…** (`Import Test`) → **Project** unchanged.
- [x] **Create New Project** → form takes `Import Test`.
- [x] **Templates** changes visible in existing project only after **Generate Project**.

### B9 — CMake build (optional)

> Only if Visual Studio, CMake, or Ninja are installed.

- [x] Open generated folder (Visual Studio, VS Code, etc.).
- [x] Follow project `README.md`: configure + build.
- [x] Result: ✅ OK ☐ failure (toolchain) ☐ not tested

---

## C — Linux

**Date:** 2026-06-29  
**Install:** ✅ standalone app ☐ from sources (`chmod +x` on executable if needed)

### C1 — First launch and window

- [x] Luthier opens without crash.

📌 **GD note**: app icon is generic, not the Luthier one.

- [x] You see four tabs: **Project**, **Preferences**, **Templates**, **About**.
- [x] **Project** tab is active at startup.
- [x] Resize the window, close Luthier, reopen: size and position are **roughly** restored (or window opens centered if screen changed — acceptable).

📌 **GD note**: on Linux, position and size are quite approximate on app relaunch...

- [x] **About** tab: displayed version matches what you are testing.

### C2 — Default settings (Preferences tab)

**Identity and paths**

- [x] **Preferences** tab → **Identity** section: change **Manufacturer** (e.g. `QA Studio`).
- [x] Click **Generate** next to manufacturer / plugin codes: valid codes appear.
- [x] **Paths** section: **Choose…** for **Destination folder** → choose an existing folder.

📌 **GD note**: I chose folder "Desktop/été 2026", but red message says characters are forbidden, yet they are valid here.

- [x] **Choose…** for **JUCE directory** → point to your JUCE installation.

**Auto-save**

- [x] After a valid change, a small **Saved** badge flashes on the field.
- [x] Close and reopen Luthier: your **Preferences** values are still there.

**Accent color**

- [x] At top of **Preferences**, change **Luthier Accent Color**: tabs and buttons change color immediately (while you stay on this tab).
- [x] Switch to **Project** tab: picker may still show the **old** color — this is normal (the two tabs are not synced live).
- [x] Return to **Preferences**: new color is selected there.
- [x] Close and reopen Luthier: color chosen in **Preferences** is still there; both pickers take this value at startup.
- [x] **Create New Project**: **Project** picker takes color saved in **Preferences**.

**Profile export / import**

- [x] **Export Preferences…** → save `profil-qa-linux.json`.
- [x] Success message in message bar (type *Preferences exported to…*).

📌 **GD note**: message shows JSON filename but not full path.

- [x] Change **Manufacturer** (e.g. `Autre Nom`).
- [x] **Import Preferences…** → choose `profil-qa-linux.json`.
- [x] Previous profile returns (manufacturer, color, paths).
- [x] **Invalid file test:** import a text file renamed to `.json` → error message, **your previous settings remain**.

### C3 — Create first project (Project tab)

- [x] **Create New Project** → message like *New project — defaults from Preferences.*
- [x] Fields match your **Preferences** (manufacturer, paths, checked formats).
- [x] **Project name**: `TestLuthier`.
- [x] **Display name**: `Test Luthier QA` (with spaces — allowed).
- [x] Leave or adjust **Version**, codes, **Destination folder**, **JUCE directory**.
- [x] **Plugin Type**: **Instrument** (you will retest another type in C5).
- [x] **Formats**: check **VST3** (and **Standalone** if you want); **AU** may stay checked for future Mac use — generation must **not** fail.
- [x] **Generate Project** becomes clickable when everything is valid.
- [x] Click **Generate Project** → success message with created folder path.
- [x] In **file manager**: `TestLuthier` folder contains `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validation (button stays grayed while invalid)**

- [x] Empty **Project name** or starting with a digit → error displayed.
- [x] All formats unchecked → **Generate Project** disabled.
- [x] **Manufacturer code** all lowercase → error (need one uppercase then lowercase).

### C4 — Session regenerate and generate guard *(replaces « Reopen » — Epic 9 archive)*

- [x] Change **Version** (e.g. `1.0.2`) **without** generating.
- [x] **Create New Project** → confirmation box → **No**: your changes remain; repeat → **Yes**: form reset.
- [ ] **Generate Project** on `TestLuthier` (current session) after change → **Regenerate Project** modal → **Yes** → success.
- [ ] Restart Luthier → **Generate Project** on same folder → **blocked**.

> *Pre-Epic 9 archive: **Open Project…** steps — no longer apply.*

### C5 — Project variants

- [x] **Create New Project** → **Plugin Type**: **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [x] **Create New Project** → **VST3** only (uncheck **Standalone**) → `TestLuthierVST3` → OK.
- [x] **Compilation** → **Preprocessor defs**: `QA_FLAG=1` → project `TestLuthierDefs` → verify line in generated `CMakeLists.txt` (no reopen in Luthier).
- [x] **AU** checked (even if you won't build on Mac) → generation OK anyway.

### C6 — Central binaries folder (optional)

- [x] **Artefacts** section: check **Copy to central artefacts folder**.
- [x] **Linux** path: **Choose…** (e.g. `/home/vous/Documents/ArtefactsQA`).
- [x] **macOS** and **Windows** fields: enter plausible paths (e.g. `/Users/vous/Documents/ArtefactsQA`, `D:/ArtefactsQA`).
- [x] Regenerate `TestLuthier` → no validation error.

### C7 — Code templates (Templates tab)

- [x] File list: `PluginProcessor.cpp`, `.gitignore`, etc.
- [x] `PluginProcessor.cpp` → comment `// QA override Linux` → **Save override**.
- [x] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → comment visible in `Source/PluginProcessor.cpp`.
- [x] **Reset to default** → regeneration: comment gone from new projects.
- [x] **Load from file…** → external `.cpp` file → **Save override** to keep.
- [x] Unreadable or huge file → error message or clean behavior, no crash.

### C8 — Three settings do not mix

- [x] **Preferences**: `Manufacturer` = `Profil Global`.
- [x] **Project** open on `TestLuthier`: project manufacturer may differ — this is normal.
- [x] Change **Preferences** → **Project** unchanged.
- [x] **Import Preferences…** (`Import Test`) → **Project** unchanged.
- [x] **Create New Project** → form takes `Import Test`.
- [x] **Templates** changes visible in existing project only after **Generate Project**.

### C9 — CMake build (optional)

> Only if CMake and a compiler are installed.

📌 **GD note**: I first created a new project then generated. Although destination folder was set (Desktop), a window automatically appeared asking me to select a folder for this. Looks like a Linux-specific bug, I didn't see this on macOS and Windows.

- [x] Open generated folder (VS Code, CLion, etc.).
- [x] Follow project `README.md`: configure + build.
- [x] Result: ✅ OK ☐ failure (toolchain) ☐ not tested

### Part 1 summary

| Block        | Steps 1–8 complete | Step 9 (optional) | Date |
| ----------- | -------------------- | ------------------- | ---- |
| A — macOS   | ☐                    | ☐                   |      |
| B — Windows | ☐                    | ☐                   |      |
| C — Linux   | ☐                    | ☐                   |      |

---

# Part 2 — Cross-platform workflow

> **Goal:** the same project goes from macOS → Windows → Linux (or other order), via **Git** (commit, push, pull), with Luthier changes on each machine.  
> **Estimated duration:** 2 to 4 h depending on your installs.

## 2.1 — Preparation (once)

- [x] Create an **empty** Git repo online (or shared on network USB key).
- [x] On **each** machine, install Luthier and JUCE (different **local** paths — intentional).
- [x] Decide work order, for example: **1. macOS → 2. Windows → 3. Linux**.

**Shared project name:** `VoyageLuthier`  
**Git repo:** https://github.com/tensquaresoftware/voyage-luthier

---

## 2.2 — Machine 1 (e.g. macOS) — Creation and first commit

- [x] Configure **Preferences** (manufacturer, destination, **local Mac** JUCE).
- [x] **Create New Project**.
- [x] **Project name**: `VoyageLuthier`.
- [x] **Display name**: `Voyage Cross QA macOS`.
- [x] **Version**: `1.0.0`.
- [x] Formats: **VST3** + **Standalone**; **AU** too if machine 1 = Mac.
- [x] **JUCE directory**: JUCE path **on this machine**.
- [x] **Artefacts** section: fill all **three** paths (Mac with **Choose…**, Windows and Linux manual entry — paths you will really use on other OS).
- [x] Enable copy to system folders & artefact folders
- [x] **Generate Project**.
- [x] Verify `.luthier.json` at project root.

### Git

- [x] In `VoyageLuthier` folder: `git init` (if not already done).
- [x] Verify `.gitignore` ignores build folders (Luthier-generated content).
- [x] `git add .` → `git commit -m "Initial VoyageLuthier project from macOS"` (free message).
- [x] Link remote repo → `git push`.

**Commit hash / note:** 2787d45 / "Initial commit: VoyageLuthier JUCE audio plugin project."

### Cursor

- [x] Build project without errors or warnings
- [x] Launch standalone app from Cursor without crash
- [x] Load VST3/AU versions without crash in DAW or AudioPluginHost from system folder
- [x] Load VST3/AU/Standalone versions without crash in DAW or AudioPluginHost from artefacts folder

---

## 2.3 — Machine 2 (e.g. Windows) — Clone, CMake build *(archive: no more Open Project…)*

- [x] `git clone` (or `git pull` if already cloned) of repo.
- [x] Open `.luthier.json` in editor → Workspace paths; adjust **Windows JUCE directory** manually if needed.
- [x] CMake build from cloned folder (no Luthier reload).
- [x] To **regenerate project**: **Create New Project** in Luthier + **empty** folder, or session regenerate on same machine/session.

> *Pre-Epic 9 archive: **Open Project…** / form reload — removed v1.0.0.*

### Cursor

- [x] Build project without errors or warnings
- [x] Launch standalone app from Cursor without crash
- [x] Load VST3 version without crash in DAW or AudioPluginHost from system folder
- [x] Load VST3/Standalone versions without crash in DAW or AudioPluginHost from artefacts folder

### Git

- [x] `git status`: `.luthier.json` (and regenerated files) modified.
- [x] Commit: *« Version 1.1.0 — Windows settings »*.
- [x] Push to remote repo.

---

## 2.4 — Machine 3 (e.g. Linux) — Pull, CMake build

- [x] `git pull` — you should see machine 2 changes.
- [x] Edit `.luthier.json` or **Preferences** for **Linux** JUCE path; CMake build.
- [x] **Templates** tab → local override (comment `// Linux QA`) → **Save override** (local to this install — normal).
- [x] To regenerate project with **Version** `1.2.0` and `LINUX_QA=1`: **Create New Project** + generate in empty folder, or session regenerate.

### Cursor

- [x] Build project without errors or warnings
- [x] Launch standalone app from Cursor without crash
- [x] Load VST3 version without crash in DAW or AudioPluginHost from system folder
- [x] Load VST3/Standalone versions without crash in DAW or AudioPluginHost from artefacts folder

### Git

- [x] Commit **project only** (not local Luthier templates): `.luthier.json`, `CMakeLists.txt`, `Source/`, etc.
- [x] Push.

---

## 2.5 — Return to machine 1 (e.g. macOS) — Final sync

- [ ] `git pull`.
- [ ] Verify `.luthier.json`: **Version** `1.2.0`, **Preprocessor defs** contains `LINUX_QA=1`.
- [ ] **Mac** JUCE path in `.luthier.json` or **Preferences**; CMake build.
- [ ] Regenerate project if needed: session regenerate or **Create New Project** + empty folder.

---

## 2.6 — Preferences profiles between machines (outside Git)

Global Luthier settings **do not travel** with the Git project. Test the manual procedure:

- [x] On machine 1: **Export Preferences…** → `voyage-profil.json`.
- [x] Transfer file (cloud, USB key, email).
- [x] On machine 2: **Import Preferences…** → profile in **Preferences**; **Project** form unchanged until **Create New Project**.
- [x] Adjust **JUCE directory** and **Destination folder** for machine 2 (local paths).
- [x] Git repo `VoyageLuthier` is **not** overwritten by import (expected behavior).

---

## 2.7 — Cross-platform edge cases

- [x] **Paths in `.luthier.json`**: open file in text editor — paths use `/` even on Windows.
- [x] ~~**Missing sidecar + Open**~~ *(removed)* — Luthier no longer offers reopen; sidecar remains optional reference in repo.
- [x] **Git conflict**: merge `.luthier.json` like any source file; CMake build after resolution.
- [ ] ❌ **Corrupt prefs file** (advanced test, disposable machine): back up `preferences.json`, replace content with `{` → relaunch Luthier → warning in message bar, default or fallback values — **no** crash. Restore backup after test. GD: app crashes on macOS (not tested on Windows & Linux), on second launch it starts without crash.

Luthier config file locations:

| System | Folder (approximate)           |
| ------- | -------------------------------- |
| macOS   | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\`        |
| Linux   | `~/.config/Luthier/`             |

---

## 2.8 — Cross-platform summary

| Step               | Machine | Displayed version | Display name    | Git OK ? |
| ------------------- | ------- | ---------------- | --------------- | -------- |
| Creation (2.2)      |         | 1.0.0            | Voyage Cross QA |          |
| After Windows (2.3) |         | 1.1.0            | … Win           |          |
| After Linux (2.4)   |         | 1.2.0            | (unchanged or …) |          |
| Final Mac (2.5)     |         | 1.2.0            | … Final         |          |

- [x] On **all three** OS, clone Git latest revision → **consistent CMake build** (JUCE/destination paths adjusted manually in `.luthier.json` if needed).
- [ ] ❌ No Luthier crash during entire Part 2 workflow. GD: yes, see 2.7.

---

# Issue tracking grid

| #   | OS      | Section | What were you doing? | Expected result | Actual result | Severity (blocking / annoying / minor) |
| --- | ------- | ------- | ------------------ | ---------------- | --------------- | ------------------------------------ |
| 1   | Windows | 2.3     | **Generate Project** on cloned `VoyageLuthier` via Git | Regeneration OK, `.git` intact | `[WinError 5] Access denied` on `.git/objects/…` — Luthier tries to delete entire folder including `.git`; Git objects read-only on Windows | **Blocking** (fix in progress: `core/project_writer.py`) |
| 2   |         |         |                    |                  |                 |                                      |
| 3   |         |         |                    |                  |                 |                                      |

**Severity:**

- **Blocking** — cannot continue the test.
- **Annoying** — workaround possible but painful.
- **Minor** — cosmetic or rare case.

*Section:* e.g. `A3`, `B7`, `C2`, `2.4`, etc.

---

## QA completion criteria

QA is **successful** for a release if:

- [x] All **three** Part 1 blocks are fully checked ([A — macOS](#a--macos), [B — Windows](#b--windows), [C — linux](#c--linux)) without blockers.
- [x] Part 2 (steps 2.1 through 2.8) is complete without blockers (Git + reopen on at least **two** OS minimum; ideal **three**).
- [x] All blockers documented in the grid have a ticket or product decision.

---

## GD notes

### Part 1

- Red color for errors: I want a brighter / less pastel red.

- When I create a new valid project, click Generate Project then click Create New Project, a modal warns me the project wasn't saved, yet Generate Project is supposed to do that, right?

- In modals with Yes and No buttons, I prefer No/Yes order on all 3 OS. There should always be a default button in accent color, default adapted to context and danger level of the operation.

---

## References

- [User manual (EN)](../user/user-manual.md)
