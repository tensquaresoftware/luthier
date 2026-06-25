---
Organization: Ten Square Software
Author: Guillaume DUPONT
Project: Luthier
Title: Luthier User Manual
Version: 1.0
Product-Version: 1.0.0
Created: 2026-06-26
Updated: 2026-06-26
References:
  - docs/ARCHITECTURE.md
  - CONTRIBUTING.md
  - docs/MANUEL-UTILISATEUR.md
  - README.md
---

# Luthier User Manual

This manual describes Luthier as shipped today: a desktop app for creating, reopening, and regenerating CMake-based JUCE audio plugin projects. The interface is in **English**. All UI labels cited below match what you see on screen.

> **French translation** — See [MANUEL-UTILISATEUR.md](MANUEL-UTILISATEUR.md) for the French edition of this manual.

---

## Table of contents

1. [What is Luthier?](#1-what-is-luthier)
2. [Before you start](#2-before-you-start)
3. [Installing and running Luthier](#3-installing-and-running-luthier)
4. [The main window](#4-the-main-window)
5. [Three kinds of settings](#5-three-kinds-of-settings)
6. [First launch](#6-first-launch)
7. [Project tab](#7-project-tab)
8. [Preferences tab](#8-preferences-tab)
9. [Templates tab](#9-templates-tab)
10. [About tab](#10-about-tab)
11. [Typical workflows](#11-typical-workflows)
12. [What Luthier generates](#12-what-luthier-generates)
13. [Where your data is stored](#13-where-your-data-is-stored)
14. [Field validation rules](#14-field-validation-rules)
15. [Messages, errors, and troubleshooting](#15-messages-errors-and-troubleshooting)
16. [Using the standalone app](#16-using-the-standalone-app)

---

## 1. What is Luthier?

Luthier helps you **create JUCE plugin projects** without hand-editing CMake files. You fill in a form, Luthier validates your input as you type, and when you click **Generate Project** it writes a complete project folder ready to open in your IDE and build with CMake.

Luthier can also **reopen** a project it created earlier, let you change settings, and **regenerate** the files in place.

Think of it as a Projucer-style workflow (which Luthier is largely inspired by), oriented toward **portable CMake projects** and **repeatable regeneration**.

### What Luthier does

- Builds AU, VST3, and/or Standalone plugin projects from a single form.
- Writes `CMakeLists.txt`, `CMakeUserPresets.json`, source files, IDE helpers, and a `.luthier.json` sidecar.
- Stores your **default values** (manufacturer, paths, plugin type, and so on) in a preferences file on your machine.
- Lets you customize the **C++ source templates** used for every new project.
- Reopens existing projects via `.luthier.json`, or by reading legacy `CMakeLists.txt` when no sidecar is present.

### What Luthier does not do

- It does not compile your plugin — you still use CMake and your IDE or toolchain (Cursor, Xcode, Visual Studio, Ninja, etc.).
- It does not download or install JUCE for you — you point Luthier at an existing JUCE folder on disk.
- It does not sync settings across machines automatically — use **Export Preferences…** / **Import Preferences…** to move profiles manually.

---

## 2. Before you start

### You will need

- A **JUCE SDK** installed somewhere on your computer (or a path you plan to use).
- A **destination folder** where new project folders should be created (for example your Documents folder or Desktop).
- Basic familiarity with **plugin formats** on your platform (AU on macOS, VST3 everywhere, Standalone for a desktop app build).

### Supported platforms

Luthier runs on **macOS**, **Windows**, and **Linux**. You can run it from source (Python + PySide6) or as a **standalone app** built with PyInstaller on each platform — see [§16](#16-using-the-standalone-app).

---

## 3. Installing and running Luthier

### From source (developers)

See [CONTRIBUTING.md](../CONTRIBUTING.md) in the repository for full setup. In short:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
.venv/bin/python main.py           # Windows: .venv\Scripts\python main.py
```

### Standalone app (end users)

Download or build the bundle for your OS. Launch the app like any native application — no Python installation required. See [§16](#16-using-the-standalone-app).

---

## 4. The main window

When Luthier opens, you see four areas:

```
┌──────────────────────────────────────────────────┐
│  Project │ Preferences │ Templates │ About       │  ← Tab bar
├──────────────────────────────────────────────────┤
│                                                  │
│              Active tab content                  │  ← Scrollable form or editor
│                                                  │
├──────────────────────────────────────────────────┤
│        Status message (centred, full width)     │  ← Dedicated status bar
├──────────────────────────────────────────────────┤
│          [Action buttons for this tab]           │  ← Bottom action bar
└──────────────────────────────────────────────────┘
```

### Tab bar

| Tab | Purpose |
|-----|---------|
| **Project** | Configure the plugin you are working on right now. |
| **Preferences** | Edit global defaults that pre-fill new projects. |
| **Templates** | View and customize the C++ / `.gitignore` templates used at generation time. |
| **About** | Credits, version, and links. |

### Bottom action bar

The buttons at the bottom **change with the active tab**:

| Tab | Buttons |
|-----|---------|
| **Project** | **Create New Project**, **Open Project…**, **Generate Project** |
| **Preferences** | **Import Preferences…**, **Export Preferences…** |
| **Templates** | **Load from file…**, **Reset to default**, **Save override** |
| **About** | *(none)* |

### Status line

After most operations, a short message appears in a **dedicated bar above the action buttons**, centred across the full window width:

- **Success** messages use the accent colour (magenta).
- **Error** messages use red.
- Long paths wrap to multiple lines instead of crowding the buttons.

Examples: *"Project generated at /Users/you/Documents/MySynth"*, *"Loaded MySynth from …"*, *"Preferences imported from client-a.json"*.

Preferences auto-save shows a small **Saved** badge on the edited field only — it does not use this global status bar.

### Window size and position

Luthier remembers your window size, position, and maximized state between sessions. If the saved position is no longer valid (for example you unplugged a monitor), the window opens centred at a comfortable default size.

---

## 5. Three kinds of settings

Understanding these three areas prevents most confusion.

| Area | Tab | Scope | Answers the question |
|------|-----|-------|----------------------|
| **Current project** | Project | One plugin at a time | *How is **this** plugin configured?* |
| **Global defaults** | Preferences | Whole app, all future projects | *What values should I reuse every time?* |
| **Global templates** | Templates | Whole app, all generated projects | *What boilerplate source code should new projects start from?* |

**Important rules:**

- Editing **Preferences** does **not** change the **Project** tab until you click **Create New Project** (or restart the app for the initial seed).
- **Open Project…** and **Generate Project** never write to `preferences.json`.
- **Templates** overrides apply to every generation but are not included when you export preferences.

---

## 6. First launch

### What happens automatically

1. Luthier creates **`preferences.json`** in your OS application config folder (first run only).
2. Factory defaults are written — see the table below.
3. The **Project** tab opens as a **new project**: identity fields empty, everything else copied from preferences.

### Factory defaults (first `preferences.json`)

| Setting | Initial value |
|---------|---------------|
| Manufacturer | `My Company` |
| Manufacturer code | `Myco` |
| Plugin code | `Mypl` |
| Copyright, Website, E-mail | empty |
| Destination folder | your **Desktop** (via the OS API) |
| JUCE directory | empty (placeholder hints per OS, e.g. `/Applications/JUCE` on macOS) |
| Plugin type | Instrument (Synth) |
| Formats | AU, VST3, Standalone — all checked |
| C++ standard | C++17 |
| Preprocessor defs, Header search paths | empty |
| Copy to system plugin folders | off |
| Copy to central artefacts folder | off |
| Artefact paths (Windows / macOS / Linux) | empty |

### Recommended first steps

1. Open **Preferences** and set your **Manufacturer**, codes, **Destination folder**, and **JUCE directory**.
2. Switch to **Project**, enter a **Project name**, and click **Generate Project**.
3. Open the generated folder in your IDE and run CMake configure + build.

---

## 7. Project tab

Intro text at the top:

> *Configure your JUCE project by entering the information below. Fields marked with an asterisk (\*) are mandatory. A new project is pre-configured based on the default settings entered in the Preferences tab.*

The tab is one scrollable page divided into five sections.

### 7.1 Project Info

Identity and paths for **this** plugin.

| Field | Required | Description |
|-------|----------|-------------|
| **Project name** * | Yes | Technical name — folder name and CMake target. Must start with a letter; letters, digits, `-`, `_` only. |
| **Display name** | No | Shown name in hosts. If empty, the project name is used. |
| **Version** * | Yes | Plugin version string (default `1.0.0` for new projects). |
| **Manufacturer** * | Yes | Your company or personal name. |
| **Copyright** | No | Copyright line in generated metadata. |
| **Website** | No | Optional URL. |
| **E-mail** | No | Optional contact. |
| **Manufacturer code** * | Yes | Exactly 4 letters (JUCE four-char code). |
| **Plugin code** * | Yes | Exactly 4 alphanumeric characters. |
| **Bundle ID** | — | Read-only. Computed from manufacturer + project name. |
| **Destination folder** * | Yes | **Parent** folder where Luthier creates the project subfolder named after **Project name**. Example: `~/Documents` + `MySynth` → `~/Documents/MySynth`. |
| **JUCE directory** | No | Path to your JUCE SDK **for this project**. Pre-filled from Preferences on a new project; can differ per project (multiple JUCE versions). |

Each path row is laid out as **label → Choose… → text field**. **Choose…** opens the native folder picker. You can still type or paste a path manually.

### 7.2 Plugin Type

Pick exactly one:

| Type | Meaning |
|------|---------|
| **Instrument** (Synth) | Receives MIDI, produces audio. |
| **Audio Effect** | Processes incoming audio. |
| **MIDI Effect** | Processes MIDI only — no audio I/O. |

### 7.3 Formats

Select **at least one**:

- **AU** (macOS Audio Unit)
- **VST3**
- **Standalone**

If none are checked, **Generate Project** stays disabled and a hint appears under the checkboxes.

### 7.4 Compilation

| Field | Description |
|-------|-------------|
| **C++ standard** | C++17, C++20, or C++23. |
| **Preprocessor defs** | One definition per line (e.g. `MY_FLAG=1`). |
| **Header search paths** | One path per line, relative to the project root. |

### 7.5 Artefacts

Controls where built plugins are **copied after each build** (written into CMake cache variables).

| Option | Description |
|--------|-------------|
| **Copy to system plugin folders** | Install-style copy to standard OS plugin locations when enabled in CMake. |
| **Copy to central artefacts folder** | When checked, enables the three directory fields below. |

When **Copy to central artefacts folder** is on:

| Field | Description |
|-------|-------------|
| **Windows** | Target path used on Windows builds. |
| **macOS** | Target path used on macOS builds. |
| **Linux** | Target path used on Linux builds. |

These paths are typed **manually** — there is no **Choose…** button, because a folder picker on your current machine cannot produce a valid path for another OS (for example `D:\Plugins` while running on macOS).

Artefact settings belong to **this project**. They may differ from your global Preferences defaults.

### 7.6 Project actions

#### Create New Project

Starts a fresh project form:

- **Cleared:** project name, display name (version reset to `1.0.0`).
- **Re-seeded from `preferences.json`:** everything else — manufacturer, codes, destination, JUCE directory, type, formats, compilation, artefacts.

If you edited the form since the last stable state (open, reset, or cold start), Luthier asks:

> *The project form has unsaved changes. Discard them and start a new project?*

**No** keeps your edits; **Yes** resets. The default button is **No**.

**Create New Project** does **not** modify `preferences.json`.

#### Open Project…

Opens a folder picker. Select a **project directory** previously generated by Luthier (contains `CMakeLists.txt` and ideally `.luthier.json`).

- Only the **Project** tab updates.
- **Preferences** and **Templates** are unchanged.

**Reading your project:**

1. If `.luthier.json` exists and is valid, Luthier loads the full configuration from it.
2. Otherwise Luthier tries to parse `CMakeLists.txt` (legacy projects).

**After moving a project folder:** open it at the **new location**. **Destination folder** updates to the parent of the folder you selected — the old path is not kept.

#### Generate Project

Creates or regenerates the project from the **Project** tab only:

- Writes to `Destination folder` / `Project name`.
- Embeds **JUCE directory** in `CMakeLists.txt` when set.
- Applies your **Templates** overrides if any.
- Writes `.luthier.json` with a full snapshot of the configuration.

**Generate Project** does **not** read or write **Preferences**.

**Destination folder behaviour:**

- The field stays visible so you can regenerate in one click after **Open Project…**.
- If empty or pointing to a non-existent folder, Luthier opens a folder picker before continuing.
- If a folder with the same project name already exists, Luthier asks before overwriting.

After a successful generation, Luthier remembers the destination parent folder for the next **Choose…** dialog.

**Generate Project** is enabled only when all required fields are valid and templates are available.

---

## 8. Preferences tab

Intro text:

> *These are reusable defaults: they pre-fill the matching fields when you create a new project, so you don't retype them each time. They are saved on this machine only and are never imposed on the projects you generate.*

### 8.1 Sections

| Section | Contents |
|---------|----------|
| **Identity** | Manufacturer, codes, Copyright, Website, E-mail |
| **Paths** | Destination folder, JUCE directory — both with **Choose…** |
| **Plugin Type** | Default synth / effect / MIDI |
| **Formats** | Default AU / VST3 / Standalone checkboxes |
| **Compilation** | Default C++ standard, preprocessor defs, header paths |
| **Artefacts** | Same copy options and per-OS paths as Project (text entry only for artefact paths) |

There are **no** project-specific fields here (no project name, version, or bundle ID).

### 8.2 Auto-save

Every valid change is **saved immediately** to `preferences.json`. You do not click a Save button.

When a field saves, a small **"Saved"** badge flashes briefly on that field (orange accent).

Invalid fields block saving until corrected.

### 8.3 Import Preferences…

1. Choose a JSON file (exported profile, backup, another machine).
2. If valid, it **replaces** the entire current preferences profile and updates `preferences.json`.
3. The Preferences tab reloads.

**Import does not change the Project tab.** Use **Create New Project** to apply the new defaults to a fresh form.

If the file is invalid, an error dialog appears and your previous profile is kept.

### 8.4 Export Preferences…

Saves the **current** preferences to a JSON file you choose. Does **not** modify `preferences.json` on disk.

Use this to back up profiles or share them between machines (one file per client, per studio, etc.).

Export is blocked if any preference field is currently invalid.

### 8.5 Multi-client workflow

1. Configure Preferences for **Client A** → **Export Preferences…** → `client-a.json`.
2. Repeat for **Client B** → `client-b.json`.
3. Before starting a plugin for a client → **Import Preferences…** → pick the right file.
4. **Create New Project** → form matches that profile.

The project you had open stays unchanged until you create or open another one.

---

## 9. Templates tab

Templates are **global**: the same files are used for **every** project you generate.

### Editable files

| File | Role |
|------|------|
| `PluginProcessor.h` / `.cpp` | Main audio/MIDI processor skeleton |
| `PluginEditor.h` / `.cpp` | Plugin editor UI skeleton |
| `.gitignore` | Git ignore rules for new projects |

Select a file from the dropdown, edit in the syntax-highlighted editor, then **Save override** to persist your version.

### Actions

| Button | Effect |
|--------|--------|
| **Load from file…** | Loads an external file into the editor **without saving**. Use **Save override** to persist. |
| **Reset to default** | Removes your override; the built-in Luthier template is restored. |
| **Save override** | Stores the editor content as your personal override. |

Status line under the editor:

- *"Override active — used for new projects."* when you have a custom version.
- *"Showing the built-in default."* otherwise.

Overrides live in the application config directory, **separate from** `preferences.json`. Importing preferences does **not** import template overrides.

---

## 10. About tab

Displays the Luthier logo, organization (**Ten Square Software**), author, contact e-mail, GitHub link, version, and revision date.

Click the e-mail or GitHub line to open your browser or mail client.

---

## 11. Typical workflows

### 11.1 Brand-new plugin (one JUCE install)

1. Set **Preferences** once (manufacturer, destination, JUCE path).
2. On **Project**, enter **Project name** and adjust options.
3. Click **Generate Project**.
4. Open the output folder in your IDE; configure and build with CMake.

For another plugin: **Create New Project** → adjust → **Generate Project**.

### 11.2 Plugin using a specific JUCE version

1. **Create New Project** (JUCE directory seeded from Preferences).
2. Change **JUCE directory** on the **Project** tab to the branch or copy you need.
3. **Generate Project** — the path is stored in the project and sidecar.

### 11.3 Resume and tweak an existing project

1. **Open Project…** → select the project folder.
2. Edit fields on **Project**.
3. **Generate Project** to rewrite files in place.

If you moved the folder, open it at the new path first.

### 11.4 Switch client profile between projects

1. **Import Preferences…** → client profile JSON.
2. **Create New Project**.
3. Fill identity fields → **Generate Project**.

Your previously open project is untouched.

### 11.5 Customize starting source code

1. Open **Templates** → select `PluginProcessor.cpp` (or another file).
2. Edit → **Save override**.
3. **Generate Project** on any new or existing project — your override is used.

---

## 12. What Luthier generates

Given a valid **Project name** `MySynth` and **Destination folder** `~/Documents`, Luthier creates `~/Documents/MySynth/` containing:

| Output | Description |
|--------|-------------|
| `CMakeLists.txt` | Main JUCE plugin CMake project |
| `CMakeUserPresets.json` | Multi-platform CMake presets (debug/release per OS) |
| `Source/` | Processor and editor `.h` / `.cpp` from templates |
| `.luthier.json` | Full configuration snapshot for reopen |
| `.gitignore` | From template (customizable) |
| `.vscode/` | Settings, tasks, launch configs for VS Code |
| `.cursorrules` | Cursor IDE hints |
| `CMake/CopyVst3Elevated.ps1` | Windows VST3 copy helper |
| `README.md` | Generated project readme |

Generation uses atomic writes: files are built in a temporary folder and swapped in place to reduce the risk of a half-written project.

---

## 13. Where your data is stored

| Location | Contents | Changed by |
|----------|----------|------------|
| `preferences.json` | Global defaults profile | First launch, Preferences auto-save, Import |
| `app_state.json` | Last destination parent, last import/export folder, window geometry | Successful Generate, Import/Export paths, window resize/move |
| Exported `*.json` files | Preference profile copies | Export Preferences… (manual files you choose) |
| Template overrides (config dir) | Custom template content | Save override, Reset |
| Generated project folder | CMake project + `.luthier.json` | Generate Project |

Config file paths depend on your OS (standard *application config* location for Luthier).

**Key idea:** global settings live in Luthier's config. Per-project settings live in the **Project** tab and, after generation, in the project folder and `.luthier.json`.

---

## 14. Field validation rules

Luthier validates fields as you type. Invalid fields show an error hint; **Generate Project** stays disabled until everything required is valid.

| Field | Rule |
|-------|------|
| Project name | Starts with a letter; only letters, digits, `-`, `_`. |
| Display name | Letters, digits, space, `-`, `_` only. |
| Version | Non-empty. |
| Manufacturer | Non-empty. |
| Manufacturer code | Exactly 4 letters. |
| Plugin code | Exactly 4 alphanumeric characters. |
| Destination folder | Non-empty; no accented characters in the path. |
| JUCE directory | Optional; if set, no accented characters. |
| Formats | At least one checked. |
| Artefact paths | When central copy is enabled, paths must not contain accented characters. |

Optional text fields (Copyright, Website, E-mail, preprocessor defs) accept any content unless otherwise noted.

---

## 15. Messages, errors, and troubleshooting

Global operation feedback (Generate, Open, Create New Project, Import/Export Preferences) appears in the **dedicated status bar** above the action buttons — see [§4 Status line](#status-line). The table below lists typical messages.

### Status messages (success)

| Action | Typical message |
|--------|-----------------|
| Generate | `Project generated at /path/to/ProjectName` |
| Open | `Loaded ProjectName from /path/to/folder` |
| Create New Project | `New project — defaults from Preferences.` |
| Import preferences | `Preferences imported from filename.json.` |
| Export preferences | `Preferences exported to filename.json.` |

### Common errors

| Situation | What happens |
|-----------|--------------|
| Open non-Luthier folder | Dialog: *Not a JUCE plugin project* or parse error with missing fields listed. |
| Invalid `.luthier.json` | Dialog: sidecar invalid or unreadable. |
| No plugin formats in opened project | Dialog: no formats detected. |
| Import invalid JSON | Warning dialog; previous preferences kept. |
| Export with invalid fields | Error message; file not written. |
| Templates missing (broken install) | Generate disabled; error at startup in the status bar. |
| Overwrite existing project | Confirmation dialog before replacing folder. |
| Unsaved Project edits + Create New Project | Confirmation dialog; default **No**. |

### Tips

- **"Generate Project" is greyed out** — check required fields (*), formats, and artefact paths when central copy is on.
- **Wrong destination after move** — use **Open Project…** at the new folder location; do not rely on an old destination path.
- **Preferences change not on Project tab** — expected; click **Create New Project** to apply.
- **Regenerate without edits** — Open → **Generate Project** should produce an consistent project; the sidecar preserves full state.

---

## 16. Using the standalone app

Luthier can be packaged as a self-contained application (no Python on the target machine).

| Platform | Typical output |
|----------|----------------|
| macOS | `Luthier.app` |
| Windows | `Luthier.exe` inside a `Luthier/` folder with `_internal/` |
| Linux | `Luthier` executable inside a `Luthier/` folder with `_internal/` |

**Important:** distribute the **entire** folder — the executable alone is not enough; templates and Qt libraries live alongside it.

### First run on Windows (unsigned builds)

Windows SmartScreen may warn on first launch. Use **More info** → **Run anyway** for local builds. Windows Defender may scan files on first start — this can add a short delay, not a failure.

### First run on Linux

If the binary is not executable: `chmod +x Luthier/Luthier`. You may need X11 or Wayland display server for the GUI.

### Headless check

From a terminal (useful for CI or verifying a bundle):

```bash
# macOS
Dist/Luthier.app/Contents/MacOS/Luthier --check

# Windows
Dist\Luthier\Luthier.exe --check

# Linux
Dist/Luthier/Luthier --check
```

Exit code `0` means the bundled templates are reachable.

---

## Quick reference card

| I want to… | Do this |
|------------|---------|
| Start a fresh plugin | **Create New Project** → fill name → **Generate Project** |
| Reopen existing work | **Open Project…** → edit → **Generate Project** |
| Change default manufacturer / paths | **Preferences** (auto-saves) |
| Use defaults on a new form | **Create New Project** after editing Preferences |
| Move prefs to another machine | **Export Preferences…** / **Import Preferences…** |
| Custom processor boilerplate | **Templates** → edit → **Save override** |
| Pin a JUCE version to one project | Set **JUCE directory** on **Project** tab |

---

*Luthier — Ten Square Software — User Manual*
