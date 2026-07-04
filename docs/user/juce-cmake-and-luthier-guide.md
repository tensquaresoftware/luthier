# JUCE, CMake, and Luthier — understanding the paths to create an audio project

> **Reference document** — written in July 2026 by Guillaume DUPONT, author of [Luthier](https://github.com/tensquaresoftware/luthier).  
> **Audience:** hobbyist or beginner developers in JUCE and CMake who want to understand *why* and *how* to start a cross-platform audio project without getting lost in the toolchain jungle.

**See also:** [Repository README](../../README.md) · [User manual (EN)](user-manual.md) · [Manuel utilisateur (FR)](manuel-utilisateur.md) · [Guide (FR)](guide-juce-cmake-et-luthier.md)

---

## Table of contents

1. [Introduction](#1-introduction)
2. [What JUCE enables](#2-what-juce-enables)
3. [What you need to start a JUCE project](#3-what-you-need-to-start-a-juce-project)
4. [Two main approaches: Projucer or CMake](#4-two-main-approaches-projucer-or-cmake)
5. [Projucer: what it does, its constraints, its limits](#5-projucer-what-it-does-its-constraints-its-limits)
6. [What the JUCE team recommends today](#6-what-the-juce-team-recommends-today)
7. [Managing a JUCE / CMake project yourself](#7-managing-a-juce--cmake-project-yourself)
8. [Luthier: a skeleton generator to save time](#8-luthier-a-skeleton-generator-to-save-time)
9. [Luthier's deliberate limits](#9-luthiers-deliberate-limits)
10. [Summary: which path to choose?](#10-summary-which-path-to-choose)
11. [Further reading](#11-further-reading)

---

## 1. Introduction

If you want to create an **audio plugin** (VST3, AU…) or a **standalone** audio/MIDI application for Windows, macOS, and Linux, you will sooner or later run into **[JUCE](https://juce.com/)** — an open-source C++ framework designed exactly for that.

But JUCE does not just provide libraries: it also offers **tools** to structure and build your projects. That is where beginners often hit a legitimate question:

> *Should I use **Projucer** (the app shipped with JUCE) or **CMake** (a generic build system)?*

This document retraces several months of reflection around that choice, the role of **Projucer**, the rise of **CMake**, and the place of **Luthier** — a project generator I built to simplify getting started.

The goal is not to turn you into a CMake expert overnight, but to give you a **durable mental map**: a view you can reread a year from now and immediately find your bearings again.

---

## 2. What JUCE enables

### In brief

**JUCE** (*Jules' Utility Class Extensions*) is a C++ framework that abstracts differences between operating systems and plugin formats. You write your code once; JUCE largely handles adaptation to each platform.

### What we focus on here (simplified scope)

| Product type | Description | Typical formats |
|--------------|-------------|-----------------|
| **Audio plugin** | Signal processing or generation inside a DAW | **VST3**, **AU** (macOS), **Standalone** (self-contained plugin build) |
| **Standalone GUI app** | Self-contained audio/MIDI app with a graphical interface | Native executable (.app, .exe…) |
| **Effect / instrument / MIDI effect** | Plugin subtypes by role | VST3/AU categories set automatically |

> **Note — CLAP and JUCE 9**  
> The **CLAP** format is gaining adoption in the open-source audio ecosystem. A **JUCE 9 pre-release** is announced with ongoing CLAP work. At the time of writing (2026), CLAP is not yet the default path for production projects; VST3 and AU remain the references. Watch [JUCE releases](https://github.com/juce-framework/JUCE/releases) and the [JUCE forum](https://forum.juce.com/) for updates.

### Supported platforms

For the scope targeted by Luthier and most indie projects:

- **Windows** (Visual Studio or related tools)
- **macOS** (Xcode or Ninja + command-line tools)
- **Linux** (GCC/Clang, often via Ninja or Makefiles)

JUCE also covers iOS, Android, and other formats (AAX, LV2, AUv3…), but this document deliberately stays focused on the **desktop + VST3/AU/Standalone** trio, which matches most personal and independent projects.

### What JUCE saves you from reinventing

- Connection to each OS **audio APIs** (Core Audio, WASAPI, ALSA/JACK…)
- Encapsulation of **plugin formats** (VST3, AU…)
- Cross-platform **graphical interface** (buttons, sliders, windows…)
- **MIDI**, audio files, basic DSP, etc.

In short: JUCE is the **engine and chassis**; you bring the **business logic** (your synth, your effect, your SysEx editor…).

---

## 3. What you need to start a JUCE project

### Common foundation: the JUCE SDK

Whichever path you choose, you need **JUCE itself** — the SDK folder containing modules, internal CMake build tools, Projucer, examples, etc.

- Official site: [juce.com](https://juce.com/)
- GitHub repository: [github.com/juce-framework/JUCE](https://github.com/juce-framework/JUCE)
- License: free for open-source projects (AGPL) or commercial depending on your use — see [juce.com/legal](https://juce.com/legal)

### Path A — The “classic” Projucer + native IDE approach

This is the historical workflow, still very common:

| Element | Role |
|---------|------|
| **JUCE SDK** | Framework and tools |
| **Projucer** | Desktop app to create/configure the project |
| **Native IDE** | Xcode (macOS), Visual Studio (Windows), Makefile (Linux) |

**Typical flow:**

1. Open Projucer → *New Project* → choose “Audio Plug-in” or “GUI Application”
2. Set options (name, manufacturer codes, VST3/AU formats…)
3. Click **Save and Open in IDE**
4. Code in Xcode or Visual Studio
5. Build and test from the IDE

### Path B — The “modern” CMake + IDE of your choice approach

This is the path **recommended by the JUCE team** for new projects:

| Element | Role |
|---------|------|
| **JUCE SDK** | Framework (referenced from CMake) |
| **CMake** (≥ 3.22) | System that *describes* how to build the project |
| **CMake Presets** | Shortcuts to configure/build by OS and Debug/Release |
| **IDE or Terminal** | Cursor, VS Code, CLion, or a plain editor + Terminal |

**Essential official documentation:**

- [CMake API — JUCE documentation](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
- [CMake examples in the JUCE repository](https://github.com/juce-framework/JUCE/tree/master/examples/CMake) (audio plugin, GUI app, console app)
- [Download CMake](https://cmake.org/download/)
- [JUCE tutorials](https://juce.com/learn/tutorials) and [general documentation](https://juce.com/learn/documentation)

**Typical flow:**

1. Create a project folder with a `CMakeLists.txt` (by hand, by copying an example, or via a generator like Luthier)
2. Configure: `cmake --preset macos-debug-arm64` (example)
3. Build: `cmake --build --preset macos-debug-arm64`
4. Code in the IDE of your choice; reconfigure CMake when the build description changes

### What about text editor + Terminal only?

**Yes, it is possible.** CMake is designed to be driven from the command line. A minimal editor + Terminal is enough if you accept:

- no advanced C++ autocompletion without `compile_commands.json`
- no integrated visual debugging (except via `lldb`/`gdb` on the CLI)
- a steeper learning curve

In practice, most developers use an IDE or enriched editor (VS Code + CMake Tools, Cursor, CLion…) that *consumes* CMake files without imposing a proprietary format.

---

## 4. Two main approaches: Projucer or CMake

Before going into detail, here is the fundamental distinction:

```
┌────────────────────────────────────────────────────────────────────┐
│                        PROJUCER                                    │
│  SSOT = .jucer file (XML)                                          │
│  Output = native IDE projects (Builds/Xcode, Builds/VS…)           │
│  Regeneration = overwrites the IDE view on every Save              │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                         CMAKE                                      │
│  SSOT = CMakeLists.txt (+ optional include files)                  │
│  Output = build cache + binaries (Builds/…)                        │
│  Reconfigure = rereads CMakeLists.txt, does not touch your sources │
└────────────────────────────────────────────────────────────────────┘
```

Both approaches can produce **the same working plugin**. What changes is **who holds the truth** (SSOT: Single Source Of Truth) about configuration and the file list — and **how** the IDE resynchronizes.

---

## 5. Projucer: what it does, its constraints, its limits

### What Projucer actually does

Projucer is a **desktop application** shipped with JUCE. It is first and foremost a **configuration form** and a **project file explorer**, not an IDE.

When you click **Save** or **Save and Open in IDE**, Projucer:

1. **Saves** the `.jucer` file (XML) — the **source of truth** on the Projucer side
2. **Regenerates** native project files in the `Builds/` folder:
   - `.xcodeproj` for Xcode
   - `.sln` / `.vcxproj` for Visual Studio
   - Makefile for Linux
3. **Opens** the IDE on that generated project (if requested)

> **Important point:** Projucer does **not** generate a `CMakeLists.txt`. It injects configuration directly (source files, modules, defines…) into the Xcode or Visual Studio format.

### The golden rule every Projucer user eventually learns

> **Create and organize your source files from Projucer** (File Explorer in the sidebar), **not directly from Xcode or Visual Studio**.

**Why?**

The `.jucer` file contains the file tree (`MAINGROUP`). On every save, Projucer **rewrites** the IDE project from that tree. If you add a `.cpp` only in Xcode, it will be missing from the `.jucer`: on the next Projucer Save, it **disappears from the build**.

It is not Xcode “forgetting” your file — it is Projucer **resynchronizing the IDE from its own base**, overwriting the previous IDE configuration.

### What Projucer handles well

- Complete form for **metadata** (name, version, company, plugin codes…)
- **Format** choices (VST3, AU, Standalone, AAX…)
- **JUCE modules** to link, compilation options
- Built-in **file explorer** with automatic resync to the IDE
- Export to **officially supported IDEs**

### Structural limits

| Limit | Explanation |
|-------|-------------|
| **No native CMake export** | Projucer exporters target Xcode, VS, Makefile, Android — not CMake |
| **Single SSOT (.jucer)** | All resync relies on this file; hard to mix with an “IDE-first” workflow |
| **Destructive IDE regeneration** | Every Save can overwrite changes made only in the IDE |
| **Two responsibilities merged** | Project **metadata** and source **tree** in the same tool |
| **Agentic IDEs not targeted** | Cursor, Antigravity, etc. do not consume `.xcodeproj`; they want CMake + `compile_commands.json` |

Projucer remains **excellent** for those who work in “Xcode + Projucer” mode and accept its rules. It becomes **constraining** as soon as you want a workflow centered on a modern editor, AI, or multi-IDE CMake.

---

## 6. What the JUCE team recommends today

The official direction has been clear for several major versions:

> **For new projects, prefer CMake.**

Concrete indicators:

- Dedicated documentation: [CMake API](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
- Official examples in `examples/CMake/` (plugin, GUI app, console app)
- High-level CMake functions: `juce_add_plugin`, `juce_add_gui_app`, `juce_add_console_app`
- Projucer **has not been removed** and remains maintained — but it is no longer the preferred starting path

### Why CMake?

| Advantage | Detail |
|-----------|--------|
| **IDE-agnostic** | Same project opened in Cursor, VS Code, CLion, or Terminal |
| **Industry standard** | Skill reusable outside JUCE |
| **No opaque IDE regeneration** | You edit the build description; CMake reconfigures |
| **Easier CI/CD** | GitHub Actions, cross builds, OS/architecture matrices |
| **Agentic coding** | AI can read and edit `CMakeLists.txt` like any other text |

Projucer and CMake are not enemies: they are two **project management philosophies**. JUCE supports both, but steers newcomers toward CMake.

---

## 7. Managing a JUCE / CMake project yourself

If you create a CMake project “by hand” (by copying JUCE examples or following the [CMake API](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)), here is what day-to-day work involves.

### The two files you will encounter most

#### `CMakeLists.txt`

This is your project's **build plan**. It answers questions such as:

- What is the project name and version?
- Where is JUCE?
- Which `.cpp` files to compile?
- What plugin type (instrument, effect…) and which formats (VST3, AU, Standalone)?
- Which JUCE modules to link?
- Which compilation options (`C++20`, defines…)?

**This file lives and grows with your project.** It is not a “generate once and forget” file.

#### `CMakeUserPresets.json`

These are **shortcuts** to invoke CMake without retyping options:

```json
{
  "configurePresets": [
    {
      "name": "macos-debug-arm64",
      "generator": "Ninja",
      "binaryDir": "Builds/macOS/ARM/Debug",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_OSX_ARCHITECTURES": "arm64"
      }
    }
  ]
}
```

In practice:

```bash
cmake --preset macos-debug-arm64    # configure
cmake --build --preset macos-debug-arm64   # build
```

Presets encapsulate differences between **macOS arm64 / macOS x86_64 / Windows / Linux**, Debug vs Release.

### What you will need to do yourself (or delegate to AI)

Once the initial skeleton is in place, day-to-day development involves:

| Situation | Typical CMake action |
|-----------|----------------------|
| New class / new `.cpp` | Add the file to the `PLUGIN_SOURCES` list (or equivalent) |
| New resource (font, image) | Add a `juce_add_binary_data` block or update existing sources |
| New JUCE module | Add `juce::juce_xxx` in `target_link_libraries` |
| Unit tests | Create a dedicated `add_executable` / `juce_add_console_app` target |
| Custom build option | Add `option()` or `set()` with clear comments |

Then **reconfigure** CMake (often automatic in IDEs with the CMake Tools extension).

### Resynchronizing the IDE

Unlike Projucer, there is no magic “Save and Open” button. Resync means:

```bash
cmake --preset <your-preset>
```

The IDE rereads `compile_commands.json` and updates indexing. **Your source files are never overwritten** by this operation.

### Two developer profiles

| Profile | Who maintains CMake over time? |
|---------|--------------------------------|
| **Agentic IDE** (Cursor, etc.) | AI, on demand (“add this class to the build”) — **approach recommended by Luthier's author** |
| **Classic IDE** (VS Code + CMake Tools, CLion…) | You, by editing `CMakeLists.txt` — the standard JUCE/CMake community workflow |

Both profiles are valid. The difference is *who* types the changes, not *whether* they are needed.

---

## 8. Luthier: a skeleton generator to save time

### What is Luthier?

**Luthier** is a desktop application (Python + PySide6) I created to address a personal frustration: starting a **properly configured** JUCE/CMake project requires many technical decisions in the first minute (plugin codes, multi-OS presets, formats, copy to system folders…).

Luthier offers a **form** inspired by Projucer — but produces a native **JUCE CMake project** directly, ready to open in Cursor or any other IDE.

Site / repository: [github.com/tensquaresoftware/luthier](https://github.com/tensquaresoftware/luthier)

### What Luthier generates

For a new project, Luthier creates in particular:

| File / folder | Content |
|---------------|---------|
| `CMakeLists.txt` | Complete build description (JUCE, plugin, base sources) |
| `CMakeUserPresets.json` | Debug/Release presets for macOS (arm64 + x86_64), Windows, Linux |
| `Source/` | `PluginProcessor` / `PluginEditor` skeleton (or app equivalent) |
| `.luthier.json` | **Write-only** JSON sidecar: snapshot of metadata entered at Generate — Luthier **never reads it back** |
| `.vscode/`, `.cursorrules` | Help opening the project in a modern IDE |

### What you get in practice

- **Immediate time savings**: no need to copy-paste and manually adapt JUCE CMake examples
- **Working skeleton**: configurable, buildable, testable right after generation
- **Cross-platform**: presets ready for the 3 desktop OSes
- **Plugin formats**: AU, VST3, Standalone (according to your form choices)
- **Advanced starting options**: automatic copy to system plugin folders, centralized artifacts folder, C++ standard, base defines…

In a few minutes, you go from “nothing” to a project that builds — and you can focus on **your business code**.

---

## 9. Luthier's deliberate limits

This is the heart of Luthier's **current vision**, refined after months of development and real-world use.

### Luthier is not a full “CMake Projucer”

Building a tool capable of:

- reopening an existing project,
- changing its characteristics (instrument → effect, adding MIDI out…),
- resynchronizing the IDE environment,

**without breaking anything**, requires merge mechanisms, protected zones in CMake, and configuration migration — a considerable investment, comparable to mature community tools like [FRUT](https://github.com/McMartin/FRUT) (`.jucer` → CMake conversion), but with an extra GUI layer and brownfield safety.

For my personal use — and for most agentic IDE users — **that is not the right effort/benefit ratio**.

### What Luthier does (and does not do)

| ✅ Luthier does | ❌ Luthier does not |
|----------------|---------------------|
| Generate the **initial skeleton** once | Reopen and reconfigure an existing project |
| Set up CMake + presets + base sources | Manage the source tree as development progresses |
| Write `.luthier.json` as an **archive of initial metadata** | Cleanly merge a `CMakeLists.txt` that has become complex |
| Accelerate **day 0** of the project | Replace Projucer for all scenarios |

Luthier thus recovers the spirit of my first command-line tool — the **JUCE-Project-Generator** — questions, smart defaults, a generated project, **done**.

### What happens after generation?

Once the project is created and development has started:

1. **Your sources** live in `Source/` (and elsewhere) — created and organized **from your IDE**, freely
2. **Your `CMakeLists.txt` evolves** — by you, or by AI if you use Cursor, for example
3. **Do not run another Luthier generation over the project** — that would overwrite accumulated work
4. **Reconfigure CMake** when you change the build description:
   ```bash
   cmake --preset macos-debug-arm64
   cmake --build --preset macos-debug-arm64
   ```

The `.luthier.json` file remains a **snapshot** of the initial choices (name, codes, formats…). It can serve as a reference for you or for AI, but Luthier is not meant to read it back to modify the project.

### Why AI is a good “CMake maintainer”

In an agentic IDE, asking:

> *“Create the `FooBar` class in `Source/Core/` and add it to the build”*

…typically triggers:

- creation of the `.h` / `.cpp` files
- update of the source list in `CMakeLists.txt`
- optional project reconfiguration

That is **more fluid** than going back to a generator form — especially when the project has accumulated hundreds of files and very specific CMake blocks (BinaryData, tests, post-build hooks…).

**That is the approach I recommend** as Luthier's author and as a daily JUCE plugin developer.

---

## 10. Summary: which path to choose?

### Comparison table

| Criterion | Projucer + native IDE | Manual CMake | **Luthier → CMake** |
|-----------|----------------------|--------------|---------------------|
| Initial learning curve | Low | High | **Low** |
| Cursor / agentic IDE compatible | No (natively) | Yes | **Yes** |
| Multi-IDE / CI | Limited | Yes | **Yes** |
| Source management over time | From Projucer only | From the IDE | **From the IDE** |
| Reconfigure project later | Via Projucer (with constraints) | Edit CMake | **Edit CMake / AI** |
| JUCE 2026 recommendation | Maintained legacy | ✅ Reference | ✅ **Startup accelerator** |

### Simplified decision tree

```
You are starting a NEW JUCE desktop project (plugin or audio app)
│
├─ Do you want to stay 100% in Xcode/VS + Projucer?
│  └─► Projucer (classic workflow, strict file rules)
│
├─ Do you know CMake well and enjoy configuring everything by hand?
│  └─► Copy examples/CMake + JUCE CMake API
│
└─ Do you want modern CMake + a free IDE (Cursor…) + a fast start?
   └─► Luthier (initial generation) → then normal development + AI
```

### The sentence to remember

> **Luthier saves you from the day-0 mountain.**  
> **CMake and your IDE carry you through every day after that.**

---

## 11. Further reading

### Official JUCE documentation

- [JUCE documentation](https://juce.com/learn/documentation)
- [JUCE tutorials](https://juce.com/learn/tutorials)
- [CMake API (GitHub)](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
- [CMake examples](https://github.com/juce-framework/JUCE/tree/master/examples/CMake)

### Related tools and projects

- [Luthier](https://github.com/tensquaresoftware/luthier) — skeleton generator (this document)
- [FRUT / Jucer2CMake](https://github.com/McMartin/FRUT) — `.jucer` → CMake conversion (different, community approach)
- [CMake — official site](https://cmake.org/)

### Quick glossary

| Term | Short meaning |
|------|---------------|
| **SSOT** | *Single Source of Truth* — the one reference that holds |
| **DAW** | *Digital Audio Workstation* — Logic Pro, Reaper, Ableton… |
| **VST3 / AU** | Audio plugin formats (Steinberg / Apple) |
| **Standalone** | Plugin build that runs as a self-contained application |
| **Preset (CMake)** | Named shortcut to configure/build with a set of options |
| **SDK** | *Software Development Kit* — here, the full JUCE folder |
| **Sidecar** | Auxiliary file (`.luthier.json`) stored next to the project |

---

*Last updated: 04/07/2026 — Ten Square Software / Guillaume DUPONT*
