---
Organization: Ten Square Software
Author: Guillaume DUPONT
Project: Luthier
Title: Luthier User Manual
Version: 1.0
Product-Version: 1.0.0
Created: 2026-06-26
Updated: 2026-06-28
References:
  - docs/architecture.md
  - CONTRIBUTING.md
  - docs/manuel-utilisateur.md
  - README.md
---

# Luthier User Manual

This manual guides you through Luthier, a desktop app for **creating**, **reopening**, and **regenerating** CMake-based JUCE projects (audio plugins and/or Standalone apps).

It is written for people new to JUCE or the audio-project build toolchain: each section explains what a setting is for first, then how to use it in the interface. Tables and lists remain for quick reference. The surrounding text is meant to steer you away from the most common pitfalls.

> **Interface language** — Luthier displays in **English**. All UI labels cited below match what you see on screen exactly.
>
> **French translation** — See [manuel-utilisateur.md](manuel-utilisateur.md) for the French edition of this manual.

---

## Table of contents

1. [What is Luthier?](#1-what-is-luthier)
2. [Before you start](#2-before-you-start)
3. [Installing and running Luthier](#3-installing-and-running-luthier)
4. [The main window](#4-the-main-window)
5. [Three kinds of settings for your JUCE projects](#5-three-kinds-of-settings-for-your-juce-projects)
6. [First launch](#6-first-launch)
7. [Project tab](#7-project-tab)
8. [Preferences tab](#8-preferences-tab)
9. [Templates tab](#9-templates-tab)
10. [About tab](#10-about-tab)
11. [Typical workflows](#11-typical-workflows)
12. [What Luthier generates](#12-what-luthier-generates)
13. [Where your data is stored](#13-where-your-data-is-stored)
14. [Field validation rules](#14-field-validation-rules)
15. [Path normalization](#15-path-normalization)
16. [Messages, errors, and troubleshooting](#16-messages-errors-and-troubleshooting)
17. [Using the standalone app](#17-using-the-standalone-app)

---

## 1. What is Luthier?

Luthier helps you **create JUCE projects** (AU/VST3/Standalone) without hand-editing CMake files. You fill in a form in the project editor, Luthier validates your input as you type, and when you click **Generate Project** it writes a complete project folder ready to open in your IDE and build with CMake.

In practice, Luthier sits **upstream** of compilation: it prepares the JUCE project skeleton (CMake files, starter source code, plugin metadata). The next step — configuring CMake, building, and testing in a DAW — happens in whichever development environment you choose (Visual Studio, Xcode, Cursor, Antigravity, Ninja, etc.).

Luthier can also **reopen** a project it created earlier, let you change settings, and **regenerate** the files in place. You do not have to start from scratch every time you change a name, format, or JUCE path.

Think of it as a Projucer-style workflow (which Luthier is largely inspired by), oriented toward **portable CMake projects** and **repeatable regeneration**. If you have used the Projucer before, you will recognise familiar concepts (plugin identity, formats, manufacturer codes). If not, the sections below walk through them step by step.

### What Luthier does

- Builds AU, VST3, and/or Standalone JUCE projects from a single form in the project editor.
- Writes `CMakeLists.txt`, `CMakeUserPresets.json`, source files, optional IDE helpers, and the **companion file** `.luthier.json` (full configuration snapshot for reopening the project).
- Stores your **default values** (manufacturer, paths, plugin type, accent colour, and so on) in a preferences file on your machine (`preferences.json`).
- Lets you customize the **C++ source templates** used for every new project (`PluginProcessor.h/.cpp` and `PluginEditor.h/.cpp`).
- Reopens existing projects via `.luthier.json`, or by reading legacy `CMakeLists.txt` when no companion file is present.

### What Luthier does not do

- It does not compile your JUCE project — you still use CMake and your IDE or toolchain (Visual Studio, Xcode, Cursor, Antigravity, Ninja, etc.).
- It does not download or install JUCE for you — you point Luthier at an existing JUCE folder on disk.
- It does not sync settings across machines automatically — use **Export Preferences…** / **Import Preferences…** to move profiles manually (handy if, for example, you are an independent developer working for multiple clients).

These limits are intentional: Luthier stays a lightweight, predictable generator. Once the project folder exists, you keep full control over your toolchain, JUCE updates, and deployment.

---

## 2. Before you start

Before opening Luthier, make sure you have the items below. You do not need to master everything upfront: most users set up **Preferences** first, generate a test project, then refine as they go.

### You will need

- A **JUCE SDK** installed somewhere on your computer (or a path you plan to use).
- A **destination folder** where new project folders should be created (for example your Desktop folder or Documents, etc.).
- **CMake 3.22+** and a C++ toolchain appropriate for your platform (details in each generated project's `README.md`).
- Basic familiarity with **plugin formats** on your platform (AU on macOS, VST3 on Windows/macOS/Linux, Standalone for a desktop app build).

### What is JUCE?

**JUCE** is a widely used open-source C++ framework for audio plugins and cross-platform audio applications. It provides the audio API, VST3/AU/Standalone wrappers, and much of the boilerplate code for a plugin.

Luthier generates projects that *use* JUCE but does not ship it in the repository: you need the SDK on your machine. Download it from [juce.com](https://juce.com) or clone the [JUCE repository](https://github.com/juce-framework/JUCE), unpack it wherever you like, then point **JUCE directory** at that folder. That path is the default so CMake knows where to find JUCE at generation time.

Nothing stops you from using a **separate JUCE copy per JUCE project**: set a project-specific **JUCE directory** on the **Project** tab (see [§11.2](#112-juce-project-with-a-specific-juce-version)). Many teams place that copy **inside the project folder** (for example `MySynth/JUCE/`) to pin the framework version and avoid a global JUCE update breaking every project at once.

### Supported platforms

Luthier runs on **Windows**, **macOS**, and **Linux**. Depending on your profile, you can run it from source (Python + PySide6), handy for contributors, or as a **standalone app** built with PyInstaller on each platform. Both offer the same interface. Only installation differs — see [§17](#17-using-the-standalone-app).

---

## 3. Installing and running Luthier

Choose the path that matches how you use Luthier. If you are just getting started and received an installer or archive, use the standalone app. If you work in the Luthier repository itself, follow the developer setup.

### From source (developers)

This path requires Python 3.11+ and a virtual environment. See [CONTRIBUTING.md](../CONTRIBUTING.md) in the repository for full setup. In short:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
.venv/bin/python main.py           # Windows: .venv\Scripts\python main.py
```

### Standalone app (end users)

Download or build the bundle for your system, then launch the app like any native application — no Python installation required on the machine. Project templates and GUI libraries are bundled in the distributed folder — see [§17](#17-using-the-standalone-app) for platform-specific details.

---

## 4. The main window

Luthier’s interface is deliberately simple: one tab per major task, a central form, and action buttons at the bottom. Take a moment to locate the four areas below. They come back throughout this manual.

When Luthier opens, you see:

```
┌──────────────────────────────────────────────────┐
│  Project │ Preferences │ Templates │ About       │  ← 1. Tab bar
├──────────────────────────────────────────────────┤
│                                                  │
│              Active tab content                  │  ← 2. Scrollable form or editor
│                                                  │
├──────────────────────────────────────────────────┤
│        Status message (centred, full width)      │  ← 3. Dedicated status bar
├──────────────────────────────────────────────────┤
│          [Action buttons for this tab]           │  ← 4. Bottom action bar
└──────────────────────────────────────────────────┘
```

### Tab bar

| Tab | Purpose |
|-----|---------|
| **Project** | Configure the JUCE project you are working on right now. |
| **Preferences** | Edit global defaults that pre-fill new projects. |
| **Templates** | View and customize the C++ / `.gitignore` templates used at generation time. |
| **About** | Credits, version, and links. |

### Status line

The status line is your main feedback after an important action (generation, open, import). After most operations, a short message appears in a **dedicated bar above the action buttons**, centred across the full window width:

- **Success** messages use the **accent colour** (customizable — magenta by default).
- **Error** messages use red.
- Long paths wrap to multiple lines instead of crowding the buttons.

Examples: *"Project generated at /Users/you/Documents/MySynth"*, *"Loaded MySynth from …"*, *"Preferences imported from client-a.json"*.

Preferences auto-save shows a small **Saved** badge on the edited field only — it does not use this global status bar.

### Action bar

The buttons at the bottom **change with the active tab**:

| Tab | Buttons |
|-----|---------|
| **Project** | **Create New Project**, **Open Project…**, **Generate Project** |
| **Preferences** | **Import Preferences…**, **Export Preferences…** |
| **Templates** | **Load from file…**, **Reset to default**, **Save override** |
| **About** | *(none)* |

### Window size and position

Luthier remembers your window size, position, and maximized state between sessions. If the saved position is no longer valid (for example you unplugged a monitor), the window opens centred at a comfortable default size.

---

## 5. Three kinds of settings for your JUCE projects

The most common source of confusion for new users is mixing up **the current JUCE project**, **default values**, and **starter source code**. Luthier keeps these three areas in separate tabs. The table below summarises the logic.

Understanding this distinction answers most questions like “I changed Preferences — why didn’t my open project update?”

| Area | Tab | Scope | Answers the question |
|------|-----|-------|----------------------|
| **Current project** | Project | One JUCE project at a time | *How is **this** JUCE project configured?* |
| **Global defaults** | Preferences | Whole app, all future projects | *What values should I reuse every time?* |
| **Global templates** | Templates | Whole app, all generated projects | *What boilerplate source code should new projects start from?* |

**Important rules:**

- Editing **Preferences** does **not** change the **Project** tab until you click **Create New Project** (or restart the app for the initial population).
- **Open Project…** and **Generate Project** never write to `preferences.json`.
- Customizations on the **Templates** tab apply on every **Generate Project**. However, **Export Preferences…** only exports the **Preferences** profile. Template overrides stay in Luthier’s `templates/` config folder (see [§13](#13-where-your-data-is-stored)). Copy them separately when you move machines.

In short: **Preferences** and **Templates** prepare the future. **Project** describes the JUCE project you are working on *right now*. Generation reads **Project** (and templates) only — never the other way around.

---

## 6. First launch

On the very first start, Luthier initialises a local profile with sensible factory defaults. You can generate a project right away, but spending a few minutes in **Preferences** (manufacturer, paths, JUCE) will save time on every JUCE project after that.

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
| Destination folder | your **Desktop** (path for your OS and user profile) |
| JUCE directory | empty (placeholder hints per OS, e.g. `/Applications/JUCE` on macOS) |
| Plugin type | Instrument (Synth) |
| Formats | AU, VST3, Standalone — all checked |
| C++ standard | C++17 |
| Preprocessor defs, Header search paths | empty |
| Copy to system plugin folders | off |
| Copy to central artefacts folder | off |
| Artefact paths (Windows / macOS / Linux) | empty |
| **Accent colour** (`accentColor`) | Magenta (`#A45C94`) — Projucer-inspired default |

### Recommended first steps

Here is a simple sequence to confirm everything is in place — from the Luthier form to the first project folder on disk:

1. Open **Preferences** and set your **Manufacturer**, codes, **Destination folder**, and **JUCE directory**.
2. Switch to **Project**, enter a **Project name**, and click **Generate Project**.
3. Open the generated folder in your IDE. Read the project's `README.md` for prerequisites and build commands, then run CMake configure + build.

If generation succeeds but the build fails, the issue is usually on the toolchain side (CMake, compiler, JUCE path) — the generated `README.md` is the right place to start troubleshooting.

---

## 7. Project tab

This is where you describe **one** JUCE project: its name, identity, formats, compilation options, and where binaries go after a build. Think of this tab as the “identity sheet” for the project Luthier will write to disk.

The tab is one scrollable page divided into five sections. Fields marked with an asterisk (*) are required. Luthier flags errors as you type and keeps **Generate Project** disabled until the form is valid.

### Luthier Accent Color

At the top of the **Project** tab — above **Project Info** — the **Luthier Accent Color** row lets you pick one of **twelve preset colours** for the application interface. While you stay on this tab, the change applies **immediately**: active tab, action buttons, **Saved** badges, links, field validation marks, and success messages in the status bar.

The same control appears at the top of the **Preferences** tab (above **Identity**). Each tab has **its own** picker — they do not update each other in real time.

| Tab | Effect of choosing a colour |
|-----|----------------------------|
| **Preferences** | **Immediate** save to `preferences.json` (no **Saved** badge). Appearance updates while you stay on this tab. |
| **Project** | **Visual change for the session** only; **not** written to `preferences.json`. |

When you switch tabs, Luthier applies the colour from the **active tab’s** picker. The **Project** picker picks up the value stored in **Preferences** at **startup** and when you click **Create New Project**.

The persisted colour is stored under the key **`accentColor`** in `preferences.json`. It is also included when you **Export Preferences…**, so each exported profile can carry its own accent — handy if you work for **several clients or brands**: assign a distinct colour per client (for example teal for Client A, amber for Client B), export one JSON file per context, and **import** the right profile before starting work. At a glance, the tab bar and buttons tell you whether you are in the right “workspace”, even before you read the manufacturer name on the form.

Changing the accent colour does **not** change project fields, templates, or generated JUCE files — only Luthier’s appearance. Only a change in **Preferences** (or **Import Preferences…**) updates `preferences.json`.

### 7.1 Project Info

This section covers the plugin **identity** (names, version, manufacturer, codes) and essential **paths** (where to create the project, where JUCE lives). Manufacturer and plugin codes may look cryptic at first: they matter mainly for macOS hosts (Audio Unit) and must follow strict rules — hence the **Generate** button and the table below.

| Field | Required | Description |
|-------|----------|-------------|
| **Project name** * | Yes | Technical name — folder name and CMake target. Must start with a letter. Letters, digits, `-`, `_` only. |
| **Display name** | No | Name shown in hosts (DAW, Standalone app). Letters, digits, spaces, `-`, and `_` allowed (e.g. `My Synth 1`). If empty, **Project name** is used. |
| **Version** * | Yes | Plugin version string (default `1.0.0` for new projects). |
| **Manufacturer** * | Yes | Your company or personal name. |
| **Copyright** | No | Copyright line in generated metadata. |
| **Website** | No | Optional URL. |
| **E-mail** | No | Optional contact. |
| **Manufacturer code** * | Yes | GarageBand-compatible AU code: first **uppercase** letter, then three **lowercase** letters (e.g. `Myco`). **Generate** button fills a random valid code. |
| **Plugin code** * | Yes | GarageBand-compatible AU code: first **uppercase** letter, then three **lowercase** letters or digits (e.g. `Mypl`, `Dem0`). `DEMO` is reserved by Apple. Same **Generate** button as manufacturer code. |
| **Bundle ID** | — | Read-only. Computed from manufacturer + project name. |
| **Destination folder** * | Yes | **Parent** folder where Luthier creates the project subfolder named after **Project name**. Example: `~/Documents` + `MySynth` → `~/Documents/MySynth`. |
| **JUCE directory** | No | Path to your JUCE SDK **for this project**. Pre-filled from Preferences on a new project. Can differ per project (multiple versions or copies of JUCE). |

Each path row in **Project Info** (**Destination folder** and **JUCE directory**) is laid out as **label → Choose… → text field**. **Choose…** opens the native folder picker. You can still type or paste a path manually. Luthier normalizes paths to forward slashes — see [§15 Path normalization](#15-path-normalization).

### 7.2 Plugin Type

The plugin type determines how JUCE wires audio and MIDI inputs/outputs in the generated processor. You can pick only **one** at a time. Change it before the first generation if needed, or regenerate after editing.

Pick exactly one:

| Type | Meaning |
|------|---------|
| **Instrument** (Synth) | Receives MIDI, produces audio. |
| **Audio Effect** | Processes incoming audio. |
| **MIDI Effect** | Processes MIDI only — no audio I/O. |

### 7.3 Formats

Formats define **what shape** your JUCE project is built as: a DAW module (AU, VST3) or a desktop app (Standalone). Check at least the one you plan to test first. You can add others later by regenerating the project.

Select **at least one**:

- **AU** (Audio Unit, macOS compatible only)
- **VST3** (Virtual Studio Technology, Windows/macOS/Linux compatible)
- **Standalone**

If none are checked, **Generate Project** stays disabled and a hint appears under the checkboxes.

**Note:** AU is only built on macOS. On Windows and Linux, CMake drops that format at build time. Leaving the checkbox enabled keeps AU in the project for when you open it on a Mac later without regenerating.

### 7.4 Compilation

These settings are passed through to the generated `CMakeLists.txt`. For a first project, the defaults (C++17, empty fields) are usually fine. Come back here when you need preprocessor flags or extra header search paths.

| Field | Description |
|-------|-------------|
| **C++ standard** | C++17, C++20, or C++23. |
| **Preprocessor defs** | One definition per line (e.g. `MY_FLAG=1`). |
| **Header search paths** | One path per line, relative to the project root. |

**Preprocessor defs** — C++ macros passed to the compiler (one per line). Useful for conditional code (`MY_DEBUG=1`) without editing CMake by hand. Luthier injects them into `CMakeLists.txt` as `target_compile_definitions`.

**Header search paths** — extra header folders the compiler should know about, **relative to the project root** (e.g. `libs/my-sdk/include`). Luthier injects them as `target_include_directories`.

### 7.5 Artefacts

After each successful build, you often want to **find the built binary** (plugin or Standalone) without digging through `Builds/` folders. This section configures two complementary mechanisms: copy to DAW scan locations, and copy to a central folder you define.

This mechanism centralizes your projects' compiled binaries in a single folder, organized by platform and architecture, so you can find, archive, or prepare them for distribution without digging through each project's build directory.

The options below are injected into CMake cache variables at generation time. Actual build-time behaviour is documented in the generated project's `README.md`.

| Option | Description |
|--------|-------------|
| **Copy to system plugin folders** | Copy to standard DAW scan locations — handy for testing the result right after a build. |
| **Copy to central artefacts folder** | When checked, enables the three directory fields below. |

When **Copy to central artefacts folder** is on:

| Field | Description |
|-------|-------------|
| **Windows** | Target path used on Windows builds. |
| **macOS** | Target path used on macOS builds. |
| **Linux** | Target path used on Linux builds. |

The path for **your current OS** has a **Choose…** button. The other two are typed or pasted manually, because a folder picker on your machine cannot produce a valid path for another OS (for example `D:\Plugins` while running on macOS). It is fine to leave the other fields empty if you develop on a single platform for now.

#### Cloud and shared storage (Dropbox, OneDrive, NAS…)

A practical setup is to point each path at the **same logical folder** inside a cloud or network sync service — for example `Dev/Artefacts/JUCE` within your Dropbox, OneDrive, or NAS mount. You still enter **three paths** (one per OS), because each system expresses that location differently:

| OS | Example path |
|----|----------------|
| macOS | `/Users/you/Dropbox/Dev/Artefacts/JUCE` |
| Windows | `C:\Users\you\Dropbox\Dev\Artefacts\JUCE` |
| Linux | `/home/you/Dropbox/Dev/Artefacts/JUCE` |

After each build, Luthier copies binaries into **platform subfolders** under that root: `macOS/` (with an architecture subfolder such as `ARM/` or `Universal/`), `Windows/`, and `Linux/`. When you build the same project on several machines, sync merges those branches into one tree — useful for archiving or preparing a release without manual sorting:

```
Dev/Artefacts/JUCE/
├── macOS/
│   ├── ARM/
│   │   ├── AU/
│   │   └── VST3/
│   └── Universal/
├── Windows/
│   └── VST3/
└── Linux/
    └── VST3/
```

Typical workflow: create the project on one machine and set the artefact path with the `Choose…` button. Clone the repository on your other systems, reopen the project in Luthier, and enter the **equivalent local path** for each OS before building there.

Artefact settings belong to **this project**. They may differ from your global Preferences defaults.

### 7.6 Project actions

Three buttons structure a project's life cycle in Luthier: start from a blank form, reopen existing work, or write the displayed configuration to disk. Each has a distinct role — confusing them is another frequent source of mistakes.

#### Create New Project

Use this when you want to **start another JUCE project** without wiping your global defaults. It resets the form:

- **Cleared:** project name, display name (version reset to `1.0.0`).
- **Re-populated from `preferences.json`:** everything else — manufacturer, codes, destination, JUCE directory, type, formats, compilation, artefacts.

If you edited the form since the last stable state (open, reset, or cold start), Luthier asks:

> *The project form has unsaved changes. Discard them and start a new project?*

**No** keeps your edits. **Yes** resets. The default button is **No**.

**Create New Project** does **not** modify `preferences.json`.

#### Open Project…

This reloads a project **already generated** by Luthier into the form. It does not change your preferences or templates. You get back the configuration stored in the project (ideally via the companion file `.luthier.json`).

Opens a folder picker. Select a **project directory** previously generated by Luthier (contains `CMakeLists.txt` and ideally `.luthier.json`).

- Only the **Project** tab updates.
- **Preferences** and **Templates** are unchanged.

**Reading your project:**

1. If `.luthier.json` exists and is valid, Luthier loads the full configuration from this companion file.
2. Otherwise Luthier tries to parse `CMakeLists.txt` (legacy projects without a companion file).

**After moving a project folder:** open it at the **new location**. **Destination folder** updates to the parent of the folder you selected — the old path is not kept.

#### Generate Project

This is the step that **actually writes files** to disk (CMake, sources, companion file, optional IDE helpers). Until you click it, form changes exist only inside Luthier.

Creates or regenerates the project from the **Project** tab only:

- writes to `Destination folder` / `Project name`.
- embeds **JUCE directory** in `CMakeLists.txt` when set.
- applies your **Templates** overrides if any.
- writes `.luthier.json`, the companion file with a full configuration snapshot.

**Generate Project** does **not** read or write **Preferences**.

**Destination folder behaviour:**

- The field stays visible so you can regenerate in one click after **Open Project…**.
- If empty or pointing to a non-existent folder, Luthier opens a folder picker before continuing.
- If a folder with the same project name already exists, Luthier asks before overwriting.

After a successful generation, Luthier remembers the destination parent folder for the next **Choose…** dialog.

**Generate Project** is enabled only when all required fields are valid and templates are available.

---

## 8. Preferences tab

The **Preferences** tab saves you from retyping the same information for every new JUCE project: default manufacturer, codes, usual destination folder, JUCE path, default formats, and so on. It is **not** where you name a specific project. That stays in **Project**.

### 8.1 Sections

At the top of the tab, **Luthier Accent Color** (see [§7 Luthier Accent Color](#luthier-accent-color)) uses the same twelve-preset picker as on **Project**. **This** is where the choice is **saved** to `preferences.json` and included in exported profiles. The **Project** tab picker is independent — it realigns only at startup or via **Create New Project**.

| Section | Contents |
|---------|----------|
| **Identity** | Manufacturer, codes (each with **Generate**), Copyright, Website, E-mail |
| **Paths** | Destination folder, JUCE directory — both with **Choose…** |
| **Plugin Type** | Default Instrument / Audio Effect / MIDI Effect |
| **Formats** | Default AU / VST3 / Standalone checkboxes |
| **Compilation** | Default C++ standard, preprocessor defs, header paths |
| **Artefacts** | Same copy options and per-OS paths as Project (**Choose…** for the host OS, text entry for the other two) |

There are **no** project-specific fields here (no project name, version, or bundle ID). If you edit Preferences while a project is already open in **Project**, it is normal that the Project screen does not change — click **Create New Project** to see the new defaults on a fresh form.

### 8.2 Auto-save

Unlike many applications, Luthier has no **Save** button in Preferences: every valid field is **saved immediately** to `preferences.json`. You can close the app without worrying about forgetting to save, as long as the field shows no error.

When a field saves, a small **"Saved"** badge flashes briefly on that field (using the current accent colour).

Invalid fields block saving until corrected.

### 8.3 Import Preferences…

Import **replaces** your entire local profile with a previously exported JSON file — useful for restoring a backup or switching between profiles (clients, machines, studios).

1. Choose a JSON file (exported profile, backup, another machine).
2. If valid, it **replaces** the entire current preferences profile and updates `preferences.json` (including **`accentColor`** when present in the file).
3. The Preferences tab reloads; the imported accent colour applies immediately **on this tab**.

**Import does not change the Project tab** (including the colour picker). Use **Create New Project** to apply the new defaults — accent colour included — to a fresh form.

If the file is invalid, an error dialog appears and your previous profile is kept.

### 8.4 Export Preferences…

Export creates a **copy** of your current preferences in a file you choose. The local `preferences.json` is not modified. You can export several named profiles (`client-a.json`, `client-b.json`, `home.json`, etc.) and reimport them later.

The exported JSON contains the same fields as your live profile, including **`accentColor`**, so appearance and defaults travel together when you move or switch profiles.

Use this to back up profiles or share them between machines (one file per client, per studio, etc.).

Export is blocked if any preference field is currently invalid.

### 8.5 Multi-client workflow

If you develop for several brands or clients, export one profile per context and import it before each new JUCE project. You keep manufacturer codes, paths, metadata, and a **distinct accent colour** consistent without retyping everything — and you can spot the active client at a glance from the UI colours.

1. Configure **Preferences** for **Client A** (defaults + **Luthier Accent Color**) → **Export Preferences…** → `client-a.json`.
2. Repeat for **Client B** with a different colour → `client-b.json`.
3. Before starting a JUCE project for a client → **Import Preferences…** → pick the right file (accent and fields update in **Preferences**).
4. **Create New Project** → form matches that profile.

The project you had open stays unchanged until you create or open another one.

---

## 9. Templates tab

Templates are the **model source files** Luthier copies into every new project: audio processor (`PluginProcessor.h/.cpp`), editor UI (`PluginEditor.h/.cpp`), `.gitignore`. Customise them once here if you want all future JUCE projects to start from your own code skeleton (usual includes, class layout, Git rules, etc.).

Templates are **global**: the same files are used for **every** project you generate.

### Editable files

| File | Role |
|------|------|
| `PluginProcessor.h` / `.cpp` | Main audio/MIDI processor skeleton |
| `PluginEditor.h` / `.cpp` | Plugin editor UI skeleton |
| `.gitignore` | Git ignore rules for new projects |

Select a file from the dropdown, edit in the syntax-highlighted editor, then **Save override** to persist your version. Until you save the override, your edits will not be used at generation time. Remember **Save override** before leaving the tab.

### Actions

| Button | Effect |
|--------|--------|
| **Load from file…** | Loads an external file into the editor **without saving**. Use **Save override** to persist. |
| **Reset to default** | Removes your override. The built-in Luthier template is restored. |
| **Save override** | Stores the editor content as your personal override. |

Status line under the editor:

- *"Override active — used for new projects."* when you have a custom version.
- *"Showing the built-in default."* otherwise.

Overrides are stored in the `templates/` subfolder of Luthier’s config directory, **separate from** `preferences.json`. Importing preferences does **not** import template overrides. If you move to another machine, export/import prefs and copy or recreate your template overrides if needed (see [§13](#13-where-your-data-is-stored)).

---

## 10. About tab

Informational tab: Luthier version, credits, and useful links. No effect on your projects.

Use the e-mail and GitHub links to contact the author and visit their GitHub page.

---

## 11. Typical workflows

The scenarios below cover the most common combinations. Each assumes Luthier is installed and you have at least set **JUCE directory** in **Preferences**.

### 11.1 Brand-new JUCE project (one JUCE install)

The most common case: one JUCE SDK, one destination folder, several JUCE projects in a row with the same defaults.

1. Set **Preferences** once (manufacturer, destination, JUCE path).
2. On **Project**, enter **Project name** and adjust options (generate a unique **Plugin code** per project).
3. Click **Generate Project**.
4. Open the output folder in your IDE. Follow the generated `README.md` to configure and build with CMake.

For another JUCE project: **Create New Project** → adjust → **Generate Project**.

### 11.2 JUCE project with a specific JUCE version

Useful when this project must stay on a JUCE branch or version different from your other projects. The SDK path is stored **in the project**, not only in Preferences.

1. **Create New Project** (JUCE directory populated from Preferences).
2. Change **JUCE directory** on the **Project** tab to the branch or copy you need.
3. **Generate Project** — the SDK path is stored in the project and the companion file `.luthier.json`.

### 11.3 Resume and tweak an existing project

You already generated a project and want to change a format, code, or path: reopen it, edit the form, regenerate. Luthier rewrites files in place (with confirmation if the folder already exists).

1. **Open Project…** → select the project folder.
2. Edit fields on **Project**.
3. **Generate Project** to rewrite files in place.

If you moved the project folder in the meantime, open it at its new location first. **Destination folder** updates automatically.

### 11.4 Switch client profile between projects

Typical flow for a freelance or multi-brand developer: import the right JSON (defaults **and accent colour**), create a fresh form, generate — without touching the previously open project.

1. **Import Preferences…** → client profile JSON (fields and accent colour updated in **Preferences**).
2. **Create New Project**.
3. Fill identity fields → **Generate Project**.

Your previously open project is untouched.

### 11.5 Customize starting source code

Do this once before a batch of generations: your template overrides will be injected into **all** projects generated afterwards (new or regenerated).

1. Open **Templates** → select `PluginProcessor.cpp` (or another file).
2. Edit → **Save override**.
3. **Generate Project** on any new or existing project — your override is used.

---

## 12. What Luthier generates

When you click **Generate Project**, Luthier creates a folder named after **Project name** inside **Destination folder**. The example below shows a typical layout. Exact files depend on the formats checked and the target platform.

Given a valid **Project name** `MySynth` and **Destination folder** `~/Documents`, Luthier creates `~/Documents/MySynth/` containing:

| Output | Description |
|--------|-------------|
| `CMakeLists.txt` | Main JUCE CMake project |
| `CMakeUserPresets.json` | Multi-platform CMake presets (debug/release per OS) |
| `Source/` | Processor and editor `.h` / `.cpp` from templates |
| `.luthier.json` | Companion file: full configuration snapshot for reopen |
| `.gitignore` | From template (customizable) |
| `.vscode/` and `.cursorrules` | **Optional** helpers for VS Code and Cursor (CMake presets, build tasks, suggested extensions). Safe to ignore or delete if you use Xcode, Visual Studio, or another IDE. |
| `CMake/CopyVst3Elevated.ps1` | Windows VST3 copy helper |
| `README.md` | Generated project readme |

Generation uses atomic writes: files are built in a temporary folder and swapped in place to reduce the risk of a half-written project.

The generated `README.md` in the project folder documents prerequisites (CMake, compiler, Ninja), CMake presets per platform, and artefact copy behaviour — start there for your first build.

---

## 13. Where your data is stored

Luthier splits data between **application configuration** (defaults, templates, window state) and **each generated project folder**. Knowing what lives where helps with backups, moving machines, or understanding why a setting “comes back” after an action.

| Location | Contents | Changed by |
|----------|----------|------------|
| `preferences.json` | Global defaults profile (`accentColor`, manufacturer, paths, …) | First launch, Preferences auto-save, accent picker (**Preferences** tab), Import |
| `app_state.json` | Last destination parent, last import/export folder, window geometry | Successful Generate, Import/Export paths, window resize/move |
| Exported `*.json` files | Preference profile copies (including `accentColor`) | Export Preferences… (manual files you choose) |
| Template overrides (`templates/`) | Custom template content | Save override, Reset |
| Generated project folder | CMake project + companion file `.luthier.json` | Generate Project |

Typical **Luthier config directory** locations:

| Platform | Path |
|----------|------|
| Windows | `%LOCALAPPDATA%\Luthier\` (e.g. `C:/Users/You/AppData/Local/Luthier/`) |
| macOS | `~/Library/Preferences/Luthier/` |
| Linux | `~/.config/Luthier/` |

You will find `preferences.json`, `app_state.json`, and the `templates/` subfolder ( **Templates** tab overrides) there.

**Key idea:** global settings live in this config directory on your machine. Per-JUCE-project settings live in the **Project** tab while you edit, then in the project folder and the companion file `.luthier.json` after generation. To share a project with a colleague, send the **project folder**. To share your usual form values, export **Preferences**.

---

## 14. Field validation rules

Luthier validates fields **as you type** rather than only when you click Generate: errors appear next to the field and **Generate Project** stays greyed out until the form is fully valid. This is guidance, not an arbitrary lock. Fix the flagged field and the button re-enables.

| Field | Rule |
|-------|------|
| Project name | Starts with a letter. Only letters, digits, `-`, `_`. |
| Display name | Letters, digits, space, `-`, `_` only (e.g. `My Synth 1`). |
| Version | Non-empty. |
| Manufacturer | Non-empty. |
| Manufacturer code | First uppercase letter, then 3 lowercase letters (GarageBand AU). |
| Plugin code | First uppercase letter, then 3 lowercase letters or digits (GarageBand AU). `DEMO` is reserved. |
| Destination folder | Non-empty. No accented characters in the path. |
| JUCE directory | Optional. If set, no accented characters. |
| Formats | At least one checked. |
| Artefact paths | When central copy is enabled, paths must not contain accented characters. |

Optional text fields (Copyright, Website, E-mail, preprocessor defs) accept any content unless otherwise noted.

**Plugin identity codes** — Luthier enforces the casing rules required by GarageBand 10.3 and recommended by JUCE for Audio Unit plugins. This avoids a common pitfall: the project builds successfully, but the AU plugin does not appear in GarageBand because the codes used the wrong case (e.g. all lowercase or all digits). Use **Generate** next to either code field for a random compliant value.

---

## 15. Path normalization

On Windows, paths are often written with backslashes (`\`). On macOS and Linux, with forward slashes (`/`). So that your projects and config files stay readable and portable across machines, Luthier **normalises** display and storage to forward slashes, without changing what the path means on your disk.

Luthier stores and displays folder paths with **forward slashes** (`/`) on every platform. This keeps `preferences.json`, `.luthier.json`, and generated CMake settings consistent when you work on Windows, macOS, or Linux — or copy projects between machines.

**Affected fields:** Destination folder, JUCE directory, and the three central-artefact paths (Windows / macOS / Linux).

**When normalization runs:**

- when you **leave** a path field (Tab or click elsewhere) — backslashes become forward slashes and leading/trailing spaces are trimmed.
- when you pick a folder with **Choose…**.
- when Luthier **saves** preferences, **generates** a project, **opens** a project, or **imports** a profile.

**Examples** (what you enter → what Luthier stores):

| You enter | Stored value |
|-----------|--------------|
| `C:\Users\Dev\Projects` | `C:/Users/Dev/Projects` |
| `D:\Plugins\VST3` | `D:/Plugins/VST3` |
| `  /opt/juce  ` | `/opt/juce` |

Unix-style paths are kept as-is (except trimming). Normalization does **not** rewrite drive letters or verify that a path exists on disk.

---

## 16. Messages, errors, and troubleshooting

If something does not work as expected, start with the **status line** (accent-coloured or red message) and the hints next to form fields. Most blockers come from a missing required field, an invalid path, or a folder that is not a Luthier project.

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
| Invalid `.luthier.json` | Dialog: companion file invalid or unreadable. |
| No plugin formats in opened project | Dialog: no formats detected. |
| Import invalid JSON | Warning dialog. Previous preferences kept. |
| Export with invalid fields | Error message. File not written. |
| Templates missing (broken install) | Generate disabled. Error at startup in the status bar. |
| Overwrite existing project | Confirmation dialog before replacing folder. |
| Unsaved Project edits + Create New Project | Confirmation dialog. Default **No**. |

### Tips

A few pointers when behaviour surprises you. Most follow the logic in [§5](#5-three-kinds-of-settings-for-your-juce-projects) rather than an application fault.

- **Plugin missing in GarageBand** — check that manufacturer and plugin codes follow the GarageBand casing rules ([§14](#14-field-validation-rules)). Use **Generate** to replace invalid codes.
- **"Generate Project" is greyed out** — check required fields (*), formats, and artefact paths when central copy is on.
- **Wrong destination after move** — use **Open Project…** at the new folder location. Do not rely on an old destination path.
- **Preferences change not on Project tab** — expected. Click **Create New Project** to apply.
- **Regenerate without edits** — Open → **Generate Project** should produce a consistent project. The companion file preserves full state.

---

## 17. Using the standalone app

Besides running from Python sources, Luthier can be distributed as a **standalone application** — convenient if you do not want to install Python or clone the repository. The interface behaves the same. Only installation and the install folder differ.

| Platform | Typical output |
|----------|----------------|
| Windows | `Luthier.exe` inside a `Luthier/` folder with `_internal/` |
| macOS | `Luthier.app` |
| Linux | `Luthier` executable inside a `Luthier/` folder with `_internal/` |

**Important:** distribute the **entire** folder. The executable alone is not enough. Templates and Qt libraries live alongside it in the `_internal/` subfolder.

### First run on Windows (unsigned builds)

Windows SmartScreen may warn on first launch. Use **More info** → **Run anyway** for local builds. Windows Defender may scan files on first start — this can add a short delay, not a failure.

### First run on Linux

If the binary is not executable: `chmod +x Luthier/Luthier`. You may need X11 or Wayland display server for the GUI.

### Headless check

From a terminal (useful for CI or verifying a bundle):

```bash
# Windows
dist\Luthier\Luthier.exe --check

# macOS
dist/Luthier.app/Contents/MacOS/Luthier --check

# Linux
dist/Luthier/Luthier --check
```

Exit code `0` means the bundled templates are reachable.

---

## Quick reference card

Once you have read the concepts above, use this table to find an action quickly:

| I want to… | Do this |
|------------|---------|
| Start a fresh JUCE project | **Create New Project** → fill name → **Generate Project** |
| Reopen existing work | **Open Project…** → edit → **Generate Project** |
| Change default manufacturer / paths | **Preferences** (auto-saves) |
| Use defaults on a new form | **Create New Project** after editing Preferences |
| Move prefs to another machine | **Export Preferences…** / **Import Preferences…** |
| Set a colour per client or brand | **Luthier Accent Color** in **Preferences** → **Export Preferences…** |
| Custom processor boilerplate | **Templates** → edit → **Save override** |
| Pin a JUCE version to one project | Set **JUCE directory** on **Project** tab |

---

*Luthier — Ten Square Software — User Manual*
