# Luthier — Full smoke test (3 OS)

**Version / target tag:** _enter the tag tested (e.g. `1.0.0-rc1`, `1.0.0`)_  
**Expected About revision:** consistent with the tag tested  
**Audience:** tester — self-contained workflow, executable step by step  
**App language:** English (labels quoted as shown on screen)

---

## How to use this guide

1. **Fill in the session sheet** (next section) before you start.
2. **Run phases in order** **P** → **A** → **B** → **C** → **D** (D can wait until A/B/C are done).
   - **Phase P**: **Preferences** tab only (realistic profile + shared file across 3 OS) — **without** Generate.
   - **Phases A / B / C**: **Project** tab (generation, build, DAW) — **Import** master prefs file at the start.
3. For **each row** in the table: perform the action, verify the expected result, check **✅ OK** *or* **❌ KO** (one of the two only), note remarks in the last column if needed.
4. If **❌ KO** blocks the rest of the phase, note severity in the **issue grid** (end of document) and decide whether to continue (annoying/minor) or stop the phase (blocking).
5. Steps marked **(opt)** are optional — they do not block release.

**Column legend**

| Column | Meaning |
| --- | --- |
| **✅ OK** | Behavior matches expected result |
| **❌ KO** | Incorrect or blocking behavior for this step |
| **Notes** | Observations, screenshots, workaround, proposed severity |

---

## Session sheet

| Field | Value |
| --- | --- |
| **Tester** | _name_ |
| **Start date** | _YYYY-MM-DD_ |
| **Commit / tag tested** | _tag or commit SHA_ |
| **Smoke test end date** | _YYYY-MM-DD_ |
| **Luthier build source** | GitHub Release — artefacts from tag tested (`.github/workflows/release.yml`) |
| **GitHub CI** (pytest 3 OS) | ☐ green on tested commit ☐ not verified |
| **DAW used** | ☐ Ableton Live ☐ JUCE AudioPluginHost ☐ both |
| **Cursor / VS Code** | Version: _…_ |
| **Dev machine** | _model / OS version_ |
| **Shared prefs file** | _path to exported luthier-smoke-prefs.json_ |

### Phase progress

| Phase | Description | ~ Duration | ✅ Done | Date | Open blockers |
| --- | --- | --- | :---: | --- | --- |
| **P** | Preferences (3 OS + shared file) | 60 min | ☐ | _date_ | — |
| **A** | Project — macOS smoke (Apple Silicon) | 45 min | ☐ | _date_ | — |
| **B** | Project — Windows smoke | 45 min | ☐ | _date_ | — |
| **C** | Project — Linux smoke | 45 min | ☐ | _date_ | — |
| **D** | Cross-OS Git (generated project) | 45 min | ☐ | _date_ | — |

---

## What CI already covers (do not retest here)

CI (`.github/workflows/pytest.yml`) runs **pytest on Ubuntu, Windows, and macOS** on every push/PR. You do **not** need to manually replay logic covered by automated tests (Generate guards, dirty guard, preferences, file generation, etc.) **unless** you want double validation before release.

The **release CD** (`.github/workflows/release.yml`) builds and publishes PyInstaller bundles on each semver tag. You do **not** need to build locally for this smoke test.

**This guide covers what CI/CD does not see:** real UI on release bundle, file dialogs, macOS quarantine, Cursor/CMake Tools, JUCE build of generated project, DAW loading, copies to system/artefact folders.

---

## v1 product model — read before testing

| Before (Epics 1–8) | Now (v1.0.0 — starter project) |
| --- | --- |
| **Open Project…** to reload `.luthier.json` | **Removed** — Luthier never re-reads the sidecar |
| Edit project on another machine via Luthier | **Impossible** — no reopen |
| **Generate** on existing folder | **Blocked** except **in-session regeneration** (same app open, explicit confirmation) |
| « Open on Win → Generate » workflow | **Replaced by** Git clone → manual edit or CMake build |

| Artefact | Travels between OS? | How |
| --- | --- | --- |
| Generated JUCE project | ✅ Yes | **Git** |
| Project settings via Luthier on remote machine | ❌ No | — |
| Luthier profile (`preferences.json`, templates) | ✅ Yes (opt.) | **Export / Import Preferences…** |
| Workspace paths (JUCE, destination) | ⚠️ Per machine | Phase **P**: realistic profile + **Export / Import** on all 3 OS → master file before any generation |

**macOS — Luthier app scope:** standalone `Luthier.app` requires an **Apple Silicon (arm64)** Mac. Intel Macs are **not** supported for the app. **Generated projects** remain buildable for Intel Mac via CMake presets `macos-debug-x86_64` (out of scope for this smoke test Phase A).

---

## Common prerequisites (all phases)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-01 | Verify **Git** installed (`git --version`) | Version displayed | ☐ | ☐ | Required Phase D |
| P-02 | Verify **CMake** ≥ 3.22 (`cmake --version`) | Version ≥ 3.22 | ☐ | ☐ | |
| P-03 | Verify compiler + **Ninja** (macOS/Linux) or **VS 2026 + CMake 4.2+** (Windows; legacy VS 2022 + CMake 3.22: presets `windows-*-vs2022`) | Tool available | ☐ | ☐ | VS 2026 presets since rc3; build validated rc4 |
| P-04 | Install **Cursor** (or VS Code) + **CMake Tools** and **C/C++** extensions | Extensions active | ☐ | ☐ | |
| P-05 | Prepare working folder **with accents** possible (e.g. `Téléchargements/été 2026`) | Folder created | ☐ | ☐ | Validates Luthier UI paths |
| P-06 | Install / locate **JUCE** (full checkout, not headers only) | Path noted below | ☐ | ☐ | |
| P-07 | Prepare **Ableton Live** *or* **AudioPluginHost** JUCE build (`extras/AudioPluginHost`) | At least one tool ready | ☐ | ☐ | |
| P-08 | Download and extract GitHub Release zip for current OS (**Obtain the build** section) | Build ready before Phase P on each machine | ☐ | ☐ | |

### Reference paths (adapt to your machine)

| Role | macOS | Windows | Linux |
| --- | --- | --- | --- |
| **JUCE** | `/Volumes/Guillaume/Dev/SDKs/JUCE` | `C:/Users/Guillaume/Dev/SDKs/JUCE` | `/home/guillaume/Dev/SDKs/JUCE` |
| **Root artefacts** (if centralized copy) | `/Users/Guillaume/Library/CloudStorage/Dropbox/Dev/Artefacts/` | `C:/Users/Guillaume/Dropbox/Dev/Artefacts` | `/home/guillaume/Dropbox/Dev/Artefacts` |
| **Luthier config** | `~/Library/Preferences/Luthier/` | `%LOCALAPPDATA%\Luthier\` | `~/.config/Luthier/` |
| **System VST3** | `~/Library/Audio/Plug-Ins/VST3/` | `C:/Program Files/Common Files/VST3/` | `~/.vst3/` |
| **System AU** (macOS) | `~/Library/Audio/Plug-Ins/Components/` | — | — |

**Test projects**

| Name | Usage |
| --- | --- |
| `SmokeTest` | One local generation per OS (Phases A / B / C) |
| `SmokeRegen` | Regeneration guards (A4 / B4 / C4) |
| `VoyageLuthier` | Shared Git repo — Phase D ([example](https://github.com/tensquaresoftware/voyage-luthier)) |

---

## Obtain the Luthier build (GitHub Release — before each OS phase)

This smoke test validates **CD-published artefacts** on semver tag — not a local build. After `git push origin <tag>`, CI publishes a [GitHub Release](https://github.com/tensquaresoftware/luthier/releases) with four zips: `Luthier-<tag>-{macos,windows,linux,docs}.zip`.

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| R-01 | Open Release for **tag tested** on GitHub | Release marked **Pre-release** if tag has suffix (`-rc1`, `-beta2`, …) | ☐ | ☐ | |
| R-02 | Download `Luthier-<tag>-macos.zip` (Phases **P-A** and **A**), `-windows.zip` (**P-B** / **B**), `-linux.zip` (**P-C** / **C**) | Archives present; non-zero size | ☐ | ☐ | |
| R-03 | **macOS:** extract zip → `Luthier.app`; if « is damaged »: `xattr -cr /path/to/Luthier.app` then launch; else `--check` | Exit code **0** on `--check`; app starts | ☐ | ☐ | Browser quarantine = normal on unsigned build |
| R-04 | **Windows:** extract → `Luthier\Luthier.exe`; launch or `--check` | Code **0**; app starts | ☐ | ☐ | |
| R-05 | **Linux:** extract → executable `Luthier/Luthier`; launch or `--check` | Code **0**; app starts | ☐ | ☐ | |
| R-06 | **About** tab on each OS | Version = **tag tested**; revision date consistent | ☐ | ☐ | |

---

## Phase P — Preferences (3 OS, shared file)

**Goal:** validate the **Preferences** tab with a profile close to a **real use case**, then build `luthier-smoke-prefs.json` by moving it across **three machines**. **Do not** open the **Project** tab or click **Generate Project** during Phase P.

**Mandatory order:** **P-A** (macOS) → **Export** → **P-B** (Windows) → **Export** → **P-C** (Linux) → **master Export** → Phases **A / B / C** (Project).

**Target file:** `luthier-smoke-prefs.json` (Dropbox, USB, etc.) — note path in session sheet.

**Workspace rule:** on each OS, fill in **host** rows only (destination + JUCE via **Choose…** when available). Other OS paths arrive via **Import** from previous steps.

**Suggested realistic profile** (adapt to your environment; see also [Reference paths](#reference-paths-adapt-to-your-machine)):

| Preferences area | Suggested values |
| --- | --- |
| **Plugin identity** | Manufacturer *Ten Square Software* (or yours); manufacturer/plugin codes via **Generate**; plausible site and email |
| **Default formats** | **VST3** + **AU** + **Standalone** checked |
| **Workspace (host OS)** | Destination with accents (UI path test); JUCE = real SDK path |
| **Artefacts** | **Copy to system folders** + **Copy to central artefacts folder** ON; **host OS** paths (cloud artefacts folder if you use one) |
| **Luthier appearance** | Change accent preset; verify tree connectors under Workspace / Artefacts |

---

### P-A — macOS (Apple Silicon)

**Prerequisites:** R-01 through R-03 (release build extracted).

#### P-A-0 — Launch (shell, without Project)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-A-001 | Launch Luthier (double-click `Luthier.app`) | No crash | ☐ | ☐ | |
| P-A-002 | Browse tabs | **Project**, **Preferences**, **Templates**, **About** visible | ☐ | ☐ | |
| P-A-003 | Look for **Open Project…** | **Absent** everywhere | ☐ | ☐ | |
| P-A-004 | Area above action buttons (**Create New Project** / **Generate Project**) | **No** message until any Project action (bar collapsed) | ☐ | ☐ | |

#### P-A-1 — Preferences tab (realistic profile, macOS)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-A-101 | **Preferences → Workspace** | 6 fields: destination + JUCE × 3 OS | ☐ | ☐ | |
| P-A-102 | **Choose…** buttons | **macOS** rows only | ☐ | ☐ | |
| P-A-103 | **Choose…** **macOS** destination → folder **with accents** | No red error; **Saved** badge possible | ☐ | ☐ | |
| P-A-104 | **macOS** JUCE (real path). **Do not** enter Windows/Linux manually | Field accepted | ☐ | ☐ | |
| P-A-110 | **Plugin identity**: manufacturer, codes (**Generate**), site, email — credible profile | No red error | ☐ | ☐ | |
| P-A-111 | **Default formats**: **VST3** + **AU** + **Standalone** | Checked without conflict | ☐ | ☐ | |
| P-A-120 | **Artefacts**: system + central copies **ON**; real **macOS** paths | Valid fields | ☐ | ☐ | |
| P-A-130 | **Luthier appearance**: change preset | Theme updated on all tabs | ☐ | ☐ | |
| P-A-131 | Tree connectors under **Workspace** / **Artefacts** | Visible | ☐ | ☐ | |

#### P-A-2 — Persistence, Export, Import

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-A-150 | Close Luthier, relaunch | **macOS** Preferences preserved | ☐ | ☐ | |
| P-A-160 | **Export Preferences…** → `luthier-smoke-prefs.json` | File created (v1 — macOS only) | ☐ | ☐ | Copy to shared storage |
| P-A-170 | Change a pref → **Import Preferences…** (P-A-160 file) | Profile restored (round-trip) | ☐ | ☐ | |

---

### P-B — Windows

**Prerequisites:** R-04; file exported in **P-A-160**.

#### P-B-0 — Launch

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-B-001 | Launch `Luthier\Luthier.exe` | No crash | ☐ | ☐ | |
| P-B-002 | Tabs + absence of **Open Project…** | As expected | ☐ | ☐ | |
| P-B-003 | Status bar (Project button area) | Collapsed (no Project action) | ☐ | ☐ | |

#### P-B-1 — Import + complete Preferences (Windows)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-B-101 | **Import Preferences…** (`luthier-smoke-prefs.json` v1) | macOS profile + identity + formats + appearance restored | ☐ | ☐ | |
| P-B-102 | **Choose…** **Windows** rows only | As expected | ☐ | ☐ | |
| P-B-103 | **Windows** destination (accents via **Choose…**) | No red error | ☐ | ☐ | |
| P-B-104 | **Windows** JUCE (real path) | Field accepted | ☐ | ☐ | |
| P-B-120 | **Artefacts**: real **Windows** paths (if enabled in P-A) | Valid fields | ☐ | ☐ | |
| P-B-130 | Verify **Luthier appearance** + tree connectors | Unchanged / consistent after Import | ☐ | ☐ | |

#### P-B-2 — Export

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-B-150 | Close / reopen | Values preserved | ☐ | ☐ | |
| P-B-160 | **Export Preferences…** → update `luthier-smoke-prefs.json` | v2 — macOS + Windows | ☐ | ☐ | |

---

### P-C — Linux

**Prerequisites:** R-05; file exported in **P-B-160**.

#### P-C-0 — Launch

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-C-001 | Launch Luthier | No crash | ☐ | ☐ | |
| P-C-002 | Tabs + absence of **Open Project…** | As expected | ☐ | ☐ | |
| P-C-003 | Status bar | Collapsed | ☐ | ☐ | |
| P-C-004 | Launcher icon / taskbar | Visible (or `.desktop`) | ☐ | ☐ | Minor if absent |

#### P-C-1 — Import + complete Preferences (Linux)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-C-101 | **Import Preferences…** (v2) | **macOS** + **Windows** paths + identity profile present | ☐ | ☐ | |
| P-C-102 | **Choose…** **Linux** rows only | OK | ☐ | ☐ | |
| P-C-103 | **Linux** destination (accents via **Choose…**) | No red error | ☐ | ☐ | |
| P-C-104 | **Linux** JUCE (real path) | Field accepted | ☐ | ☐ | |
| P-C-120 | **Artefacts**: real **Linux** paths | Valid fields | ☐ | ☐ | |

#### P-C-2 — Master export

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| P-C-150 | Close / reopen; **Import** round-trip (C-160 file) | OK | ☐ | ☐ | |
| P-C-160 | **Export Preferences…** → **master `luthier-smoke-prefs.json`** | **6 real Workspace paths** + complete realistic profile | ☐ | ☐ | Use for Phases A/B/C |

---

## Phase A — Project (macOS Apple Silicon)

**Machine:** **Apple Silicon** Mac (M1/M2/M3/M4…) — **not** Intel Mac.  

**Prerequisites:** Phase **P** complete; **master `luthier-smoke-prefs.json`** file (P-C-160).

### A0 — Preparation (Import prefs, Project tab)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| A-001 | Launch Luthier (or resume after Phase P-A) | No crash | ☐ | ☐ | Shell UI already covered in P-A-001–004 |
| A-002 | **Import Preferences…** (P-C-160 master file) | 6 Workspace paths + identity + formats + appearance restored | ☐ | ☐ | |
| A-003 | **Preferences**: verify Phase P profile (identity, formats, macOS Artefacts) | As expected without manual re-entry | ☐ | ☐ | |
| A-004 | **Project** tab | **No** accent color picker; status bar collapsed until any Project action | ☐ | ☐ | |

### A3 — Initial generation (`SmokeTest`)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| A-301 | **Create New Project** | Blank form, defaults from Preferences; status message visible above action buttons (e.g. *New project — defaults from Preferences.*) | ☐ | ☐ | |
| A-302 | **Project name** = `SmokeTest`; formats inherited from Preferences (VST3 + AU + Standalone if configured in P-A) | Formats checked without UI conflict | ☐ | ☐ | |
| A-303 | **Artefacts**: options and paths already set in Phase P — verify **macOS** consistency | Valid fields | ☐ | ☐ | |
| A-304 | **Generate Project** | Success; message with path using **`/`** (forward slashes) | ☐ | ☐ | Note absolute path: '/Users/Guillaume/Desktop/été 2026/SmokeTest' |
| A-305 | Open generated folder in Finder | Present: `CMakeLists.txt`, `CMakeUserPresets.json`, `Source/`, `.luthier.json`, `.gitignore`, `README.md`, `.vscode/`, `.cursorrules` | ☐ | ☐ | |
| A-306 | Open `.luthier.json` | Workspace paths present; **no** `accentColor` key | ☐ | ☐ | |

### A4 — Generate guards

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| A-401 | **Close and relaunch Luthier** (fresh session) | App restarts normally | ☐ | ☐ | |
| A-402 | Without changing destination: **Project name** = `SmokeTest` → **Generate Project** | **Blocked**: modal + bar *This folder already exists and is not empty…* | ☐ | ☐ | |
| A-403 | **Create New Project** → **Project name** = `SmokeRegen` → **Generate Project** | Success in a **new** folder | ☐ | ☐ | |
| A-404 | In `SmokeRegen` folder: `git init`, `git add .`, `git commit -m "init"` | Git repo initialized | ☐ | ☐ | Prepares next test |
| A-405 | **Without closing Luthier**: on `SmokeRegen`, change **Version** → `2.0.0` → **Generate Project** | **Regenerate Project** modal; default **No**; choose **Yes** → success | ☐ | ☐ | |
| A-406 | Verify on disk | Files reflect `2.0.0`; `.git/` folder **still present** | ☐ | ☐ | |

### A5 — Create New Project and dirty guard

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| A-501 | Right after successful **Generate**: click **Create New Project** | **No** « unsaved changes » modal | ☐ | ☐ | |
| A-502 | Change a field (e.g. version) **without** generating → **Create New Project** | Confirmation modal; **No** default; **No** cancels, **Yes** resets | ☐ | ☐ | |

### A6 — Templates **(opt.)**

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| A-601 | **Templates** → override `PluginProcessor.cpp` → **Save override** | Override saved | ☐ | ☐ | |
| A-602 | **Create New Project** → new name → **Generate Project** | Override visible in generated sources | ☐ | ☐ | |
| A-603 | **Reset to default** → new generation | No override in sources | ☐ | ☐ | |

### A7 — Cursor: open, presets, build

**Target project:** `SmokeTest` folder created in A-304.

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| A-701 | Cursor → **File → Open Folder…** → `SmokeTest` folder | Opens without blocking error | ☐ | ☐ | |
| A-702 | Verify `.vscode/` | `settings.json`, `tasks.json`, `launch.json` present | ☐ | ☐ | |
| A-703 | Wait for CMake configuration to finish (status bar) | Configure **successful** (no red failure) | ☐ | ☐ | |
| A-704 | Palette (`Cmd+Shift+P`) → **CMake: Select Configure Preset** | **macOS** presets listed (`macos-debug-arm64`, `macos-release-arm64`, …) | ☐ | ☐ | |
| A-705 | Select **`macos-debug-arm64`** | Consistent build folder (e.g. `Builds/macOS/ARM/Debug`) | ☐ | ☐ | **Do not** use `macos-debug-x86_64` on this test (ARM host) unless intentional Rosetta test |
| A-706 | **CMake: Build** or `Cmd+Shift+B` | Build **without error** | ☐ | ☐ | |
| A-707 | **Problems** panel | No **errors**; no **project** warnings (third-party JUCE header warnings = note minor) | ☐ | ☐ | |
| A-708 | Build logs / terminal | Traces of copy to **system** and **artefacts** folders visible | ☐ | ☐ | |

### A8 — Standalone and plugin loading

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| A-801 | **Run and Debug** → **Standalone** config → **F5** | Standalone opens **without crash**; clean shutdown | ☐ | ☐ | |
| A-802 | Finder: `~/Library/Audio/Plug-Ins/VST3/` | `SmokeTest.vst3` (or equivalent name) present | ☐ | ☐ | |
| A-803 | Finder: `~/Library/Audio/Plug-Ins/Components/` | `SmokeTest.component` present | ☐ | ☐ | |
| A-804 | DAW: rescan plugins if needed | Scan completes without error | ☐ | ☐ | Tested with Ableton Live 12 |
| A-805 | Load **VST3** from **system** folder | No crash; plugin UI visible | ☐ | ☐ | Tested with Ableton Live 12 |
| A-806 | Load **AU** from **system** folder | No crash | ☐ | ☐ | Tested with Ableton Live 12 |
| A-807 | **Artefacts** folder: under `…/macOS/ARM/` (or equivalent) | VST3, AU, Standalone present | ☐ | ☐ | |
| A-808 | Load **VST3** from **artefacts** | No crash | ☐ | ☐ | Tested with AudioHostPlugin |
| A-809 | Load **AU** from **artefacts** | No crash | ☐ | ☐ | Tested with AudioHostPlugi |
| A-810 | Launch **Standalone** from **artefacts** folder | No crash | ☐ | ☐ | |

---

## Phase B — Project (Windows)


**Important:** `SmokeTest` project path **ASCII only** (no accents — MSVC limitation): projects generated on Desktop.  
**Prerequisites:** Phase **P** complete; master prefs file (P-C-160).

### B0 — Preparation (Import prefs)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| B-001 | Launch Luthier (shell UI: see P-B-001–003) | No crash | ☐ | ☐ | |
| B-002 | **Import Preferences…** (P-C-160 master file) | Full profile restored (6 Workspace paths + identity + appearance) | ☐ | ☐ | |
| B-003 | **Preferences**: verify without re-entry (Windows Artefacts if enabled in P-B) | As expected | ☐ | ☐ | |

### B3 — Initial generation (`SmokeTest`)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| B-301 | **Create New Project** | Blank form; status message visible above action buttons (e.g. *New project — defaults from Preferences.*) | ☐ | ☐ | |
| B-302 | **Project name** = `SmokeTest`; formats inherited from Preferences | OK | ☐ | ☐ | |
| B-303 | **Artefacts**: verify consistency from Phase P | OK | ☐ | ☐ | |
| B-304 | **Generate Project** | Success; paths displayed with **`/`** (not `\`) | ☐ | ☐ | Path: C:/Users/Guillaume/Desktop |
| B-305 | Folder contents | Required files present (see A-305) | ☐ | ☐ | |
| B-306 | `.luthier.json` | Workspace OK; **no** `accentColor` | ☐ | ☐ | |

### B4 — Generate guards

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| B-401 | Close / relaunch Luthier | OK | ☐ | ☐ | |
| B-402 | **Generate** to existing `SmokeTest` folder | Blocked (modal + bar) | ☐ | ☐ | |
| B-403 | **Create New Project** → `SmokeRegen` → **Generate** | Success | ☐ | ☐ | |
| B-404 | `git init` + commit in `SmokeRegen` | `.git/` created | ☐ | ☐ | |
| B-405 | **Generate** in folder with `.git/` | No WinError / access denied | ☐ | ☐ | rc2/rc3: WinError 32 — OK **rc4** (W2-04) |
| B-406 | In-session regeneration (version `2.0.0`, modal **Yes**) | Success; `.git/` preserved | ☐ | ☐ | OK **rc4** (W2-05) |

### B5 — Create New Project and dirty guard

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| B-501 | **Create New Project** right after Generate | No unsaved modal | ☐ | ☐ | |
| B-502 | Change field → **Create New Project** | Modal; **No** default | ☐ | ☐ | |
| B-503 | Modal **No** / **Yes** button order | Inverted vs Mac = **minor** if functional | ☐ | ☐ | |

### B6 — Templates **(opt.)**

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| B-601 | Template override → Generate new project | Override visible | ☐ | ☐ | |
| B-602 | **Reset to default** → Generate | Override absent | ☐ | ☐ | |

### B7 — Cursor: build

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| B-701 | Open `SmokeTest` folder in Cursor | Smooth | ☐ | ☐ | OK **rc4** (W3-01) |
| B-702 | `.vscode/` + CMake configure | Successful | ☐ | ☐ | |
| B-703 | Preset **`windows-debug`** | Build dir `Builds/Windows` | ☐ | ☐ | VS 2026 |
| B-704 | **CMake: Build** / `Ctrl+Shift+B` | No error | ☐ | ☐ | |
| B-705 | **Problems** | No project errors | ☐ | ☐ | |
| B-706 | **UAC** prompt on system VST3 copy | Click **Yes**; artefact logs visible | ☐ | ☐ | |

### B8 — Standalone and plugins

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| B-801 | **F5** Standalone | No crash | ☐ | ☐ | |
| B-802 | `C:/Program Files/Common Files/VST3/` | VST3 present | ☐ | ☐ | |
| B-803 | DAW: **system** VST3 | No crash | ☐ | ☐ | |
| B-804 | DAW: **artefacts** VST3 | No crash | ☐ | ☐ | |
| B-805 | Standalone from **artefacts** | No crash | ☐ | ☐ | |

---

## Phase C — Project (Linux)


**Prerequisites:** Phase **P** complete; master prefs file (P-C-160).

### C0 — Preparation (Import prefs)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| C-001 | Launch Luthier (shell UI: see P-C-001–004) | No crash | ☐ | ☐ | |
| C-002 | **Import Preferences…** (P-C-160 master file) | Full profile restored | ☐ | ☐ | |
| C-003 | Close / reopen: window size | Size roughly preserved; position not guaranteed (Wayland = minor) | ☐ | ☐ | |

### C3 — Generation (`SmokeTest`)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| C-301 | **Create New Project** → `SmokeTest`; **VST3** + **Standalone** | OK; status message visible after **Create New Project** (e.g. *New project — defaults from Preferences.*) | ☐ | ☐ | |
| C-302 | **Generate Project** | Success; paths with `/` | ☐ | ☐ | |
| C-303 | Files + `.luthier.json` | As expected (see A-305 / A-306) | ☐ | ☐ | |

### C4 — Generate guards

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| C-401 | Fresh session → Generate to existing `SmokeTest` | Blocked | ☐ | ☐ | |
| C-402 | `SmokeRegen` + `git init` + session regeneration | OK; `.git/` preserved | ☐ | ☐ | |

### C5 — Dirty guard

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| C-501 | Create New Project after Generate / after edit | Same behavior as A-501 / A-502 | ☐ | ☐ | |

### C6 — Templates **(opt.)**

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| C-601 | Override + Generate + Reset | As expected A6 | ☐ | ☐ | |

### C7 — Cursor: build

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| C-701 | Open `SmokeTest`; preset **`linux-debug`** | `Builds/Linux/Debug` | ☐ | ☐ | |
| C-702 | Build without error; Problems clean | OK | ☐ | ☐ | |
| C-703 | Copy logs to `~/.vst3/` and artefacts | Visible | ☐ | ☐ | |

### C8 — Standalone and plugins

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| C-801 | **F5** Standalone | No crash | ☐ | ☐ | |
| C-802 | `~/.vst3/` + DAW system | VST3 loadable | ☐ | ☐ | Tested with AudioHostPlugin |
| C-803 | Artefacts + Standalone artefacts | No crash | ☐ | ☐ | |

---

## Phase D — Cross-platform Git smoke (generated project)

Validates that the **JUCE project** travels via Git and builds on each OS **without** reopening the project in Luthier.  
**Prerequisites:** Phases A, B, C complete (or at minimum generation OK on each OS).

### D0 — Preparation

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| D-001 | Create or empty remote repo `VoyageLuthier` (GitHub or local) | Repo ready | ☐ | ☐ | URL: |
| D-002 | JUCE installed on **each** machine with local paths noted | Ready for D1–D3 | ☐ | ☐ | |

### D1 — Machine 1 (macOS Apple Silicon) — Creation

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| D-101 | Luthier: **Create New Project** → `VoyageLuthier`, v `1.0.0`, **VST3** + **Standalone** + **AU** | Form OK | ☐ | ☐ | |
| D-102 | Workspace + Artefacts filled for **3 OS**; system + artefacts copies **ON** | OK | ☐ | ☐ | |
| D-103 | **Generate Project** | Folder + `.luthier.json` | ☐ | ☐ | |
| D-104 | `git init` → `git add .` → `git commit` → `git push` | Remote repo up to date | ☐ | ☐ | |
| D-105 | Cursor: preset **`macos-debug-arm64`** → build | No project error or warning | ☐ | ☐ | |
| D-106 | **F5** Standalone + **system** and **artefacts** plugins | No crash | ☐ | ☐ | |

### D2 — Machine 2 (Windows)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| D-201 | `git clone` of repo | Local copy OK | ☐ | ☐ | OK **rc4** (W4-01) |
| D-202 | Edit `.luthier.json`: **`juceDirWindows`** (local JUCE path) | File saved | ☐ | ☐ | |
| D-203 | Cursor: **`windows-debug`** → build | No error | ☐ | ☐ | |
| D-204 | Standalone **F5** + system VST3 + artefacts | No crash | ☐ | ☐ | |
| D-205 | (opt.) Edit `Source/` → commit → push | Remote up to date | ☐ | ☐ | |

> **Do not** use **Generate Project** on the clone after Luthier restart (non-empty folder). Full regeneration = empty folder + new Luthier session on machine 1, or **in-session** regeneration on machine 1.

### D3 — Machine 3 (Linux)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| D-301 | `git pull` (or clone) | Up to date | ☐ | ☐ | |
| D-302 | Edit **Linux** JUCE in `.luthier.json` | OK | ☐ | ☐ | See **D-302** box below |
| D-303 | Cursor: **`linux-debug`** → build + plugins | As expected D-204 | ☐ | ☐ | |
| D-304 | (opt.) commit + push if changes | OK | ☐ | ☐ | I changed the GUI text to "Voyage Luthier - Linux" |

### D4 — Return to machine 1 (macOS)

| ID | Action | Expected result | ✅ OK | ❌ KO | Notes |
| --- | --- | --- | :---: | :---: | --- |
| D-401 | `git pull` | Sources + `.luthier.json` + `CMakeLists.txt` consistent | ☐ | ☐ | |
| D-402 | Adjust **macOS** JUCE if needed → build + plugins | Still OK | ☐ | ☐ | |
| D-403 | During D1–D4: Luthier used **only in D1** | No Luthier crash | ☐ | ☐ | |

> **D-302 — Edit Linux JUCE in `.luthier.json`**
>
> On the **Linux** machine, after clone or pull of the `VoyageLuthier` repo:
>
> 1. Open the cloned folder in Cursor (or editor).
> 2. Open `.luthier.json` at project root.
> 3. Locate the **`juceDirLinux`** key (or equivalent Linux workspace key per sidecar schema).
> 4. Replace the value with the **local JUCE path on this machine** (e.g. `/home/guillaume/Dev/SDKs/JUCE`).
> 5. Save — **do not** use Luthier to reopen the project.
> 6. Continue with **D-303**: preset `linux-debug` → build.
>
> **macOS** and **Windows** paths in the same file remain those of the other machines; only the **Linux host** path must match the current machine.

---

## Success criteria (v1.0.0 release go)

**Smoke test verdict (10/07/2026):** ✅ **GO** — phases P, A, B, C, D complete; issues #1–#2 resolved; accepted minors listed below.

| ID | Criterion | ✅ OK | ❌ KO | Notes |
| --- | --- | :---: | :---: | --- |
| G-00 | Phase **P** complete (P-A → P-C, master file exported) | ☐ | ☐ | |
| G-01 | Phase **A** complete (A0 + A3–A8, excl. opt.) | ☐ | ☐ | |
| G-02 | Phase **B** complete (B0 + B3–B8, excl. opt.) | ☐ | ☐ | Build/regen validated rc4 |
| G-03 | Phase **C** complete (C0 + C3–C8, excl. opt.) | ☐ | ☐ | |
| G-04 | Phase **D** complete (D1–D4 minimum) | ☐ | ☐ | D2 validated rc4 |
| G-05 | **No blocking** issues open in grid below | ☐ | ☐ | #1–#2 resolved rc3/rc4 |
| G-06 | Known minors accepted (if present) | ☐ | ☐ | B-503, C-003, P-C-004 |


---

## Issue grid (fill in as you go)

For each significant **❌ KO**, add a row. Reference the step **ID** (e.g. `A-705`).

| # | Step ID | OS | Summary | Expected | Actual | Severity | Next |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _ | _ | _ | _ | _ | _ | _ | _ |

**Severity:** **blocking** = cannot continue or data loss risk; **annoying** = painful workaround; **minor** = cosmetic or rare case.

---

## No longer necessary to test

- **Open Project…** → Generate round-trip without change
- Byte-for-byte fidelity after Open on another machine
- Sidecar migration / Open fallback CMake regex
- « Open on Windows → Generate » workflow on Git clone
- **Luthier on Intel Mac** (out of v1.0.0 scope)
- Manually replay all logic already covered by **pytest CI** (unless double-check decision)
- Local PyInstaller build (`publish/build-dist.py`) or run from sources — covered by **release CD** on tag

---

## References

- [User manual (EN)](../user/user-manual.md)
- [Windows smoke test add-on](./smoke-test-windows-addon.md) — optional Windows supplement for Phase B build/regen + D2
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — bundle build, CI
- Generated project README (`SmokeTest/README.md`) — Cursor presets, debugging
- [QA checklist archive (beta)](./archive/v1.0.0-beta/checklist-qa-pre-release-v1.md)
