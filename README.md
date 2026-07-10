# Luthier

A Projucer-inspired desktop GUI for **one-shot generation** of ready-to-build CMake-based JUCE starter projects.

![Luthier](luthier.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/tensquaresoftware/luthier)
[![GUI: PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=for-the-badge)](https://doc.qt.io/qtforpython/)
[![Sponsor](https://img.shields.io/badge/Sponsor-Ten%20Square%20Software-ff69b4?style=for-the-badge&logo=github-sponsors&logoColor=white)](https://github.com/sponsors/tensquaresoftware)

> 💛 If you find this project useful, consider [sponsoring its development](https://github.com/sponsors/tensquaresoftware) — every contribution helps keep the work going!

Luthier is a self-contained [PySide6](https://doc.qt.io/qtforpython/) desktop app that generates ready-to-build, CMake-based JUCE plugin projects (AU / VST3 / Standalone): fill a form, validate inline, and generate a complete starter project once. After generation, continue development in your IDE — Luthier does **not** reload or reopen existing projects. Your defaults live in a persistent preferences file; each generate also writes a **write-only** `.luthier.json` sidecar as metadata for you or AI tools.

**Further reading:** [User manual (EN)](docs/user/user-manual.md) · [Manuel utilisateur (FR)](docs/user/manuel-utilisateur.md) · [JUCE/CMake guide (EN)](docs/user/guides/juce-cmake-and-luthier-guide.md) · [Documentation index](docs/README.md)

## Features

- **Project** — one scrollable page for the whole plugin:
  - identity: technical/display names, version, manufacturer, copyright, website, e-mail, plugin & manufacturer codes, auto-computed bundle ID, with live inline validation;
  - plugin type (Instrument, Audio Effect, MIDI Effect), decoupled **plugin characteristics** (synth/MIDI flags, Audio I/O preset, VST MIDI channel counts), and **plugin description** (CMake `DESCRIPTION`);
  - formats (AU, VST3, Standalone);
  - compilation: C++ standard, preprocessor definitions, header search paths;
  - workspace: per-OS destination and JUCE paths with tree-style grouping;
  - artefacts: copy to system plugin folders and/or a central per-OS directory.
- **Generate guard** — blocked when the destination `{folder}/{projectName}/` is non-empty (including hidden files like `.git/` or `.DS_Store`); **session regenerate** in the same app session rewrites the tree except `.git` after a destructive confirm.
- **Preferences** — persistent defaults (identity, workspace, accent colour, default artefact settings) stored as JSON in the OS configuration directory.
- **Templates** — view, edit, replace, or reset the C++ source templates (`PluginProcessor` / `PluginEditor`) used for new projects; overrides persist on disk.
- **Write-only `.luthier.json`** — configuration snapshot written at generate; optional reference for humans or tooling — Luthier never reads it back into the form.

## Requirements

- Python 3.11+
- Dev setup: `pip install -r requirements-dev.txt` (includes PySide6, pytest, PyInstaller — see [CONTRIBUTING.md](CONTRIBUTING.md))
- Runtime-only install: `pip install -r requirements.txt` (PySide6 only)
- No external dependencies beyond PySide6: the CMake project templates ship inside Luthier (`templates/`) and the generation engine is built in (`core/`).

## Run from source

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
.venv/bin/python main.py           # Windows: .venv\Scripts\python main.py
```

Check that the bundled templates are reachable (headless):

```bash
.venv/bin/python main.py --check     # Windows: .venv\Scripts\python main.py --check
```

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for full developer setup (venv, pytest, bundle build) and **[docs/dev/architecture.md](docs/dev/architecture.md)** for the three-layer design and module contracts.

## Build a standalone app

PyInstaller bundles templates and resources into a self-contained app (build on each target OS — no cross-compilation):

```bash
.venv/bin/python publish/build-dist.py
```

On Windows: `.venv\Scripts\python.exe publish/build-dist.py`

| OS      | Output                                      |
| ------- | ------------------------------------------- |
| macOS   | `dist/Luthier.app`                          |
| Windows | `dist/Luthier/Luthier.exe` + `_internal/`   |
| Linux   | `dist/Luthier/Luthier` + `_internal/`       |

Platform variants, headless bundle checks, and timings: see **[CONTRIBUTING.md](CONTRIBUTING.md#build-a-standalone-bundle-optional-extended-step)**.

## Supporting the project

Luthier is developed in my free time, alongside a day job as an instructional designer. [Cursor](https://cursor.com) has been a key part of my workflow for building this tool and related projects.

If you find Luthier useful, sponsoring on [GitHub Sponsors](https://github.com/sponsors/tensquaresoftware) is the most direct way to help cover tooling costs and keep development going. Every contribution, no matter the size, is genuinely appreciated.

Also see **[Matrix-Control](https://github.com/tensquaresoftware/matrix-control)** — a cross-platform SysEx MIDI editor for the Oberheim Matrix-1000 (JUCE 8 plugin) from the same author.

## License

Luthier is released under the [MIT License](LICENSE).

Packaged builds are distributed with Qt (via PySide6) under the LGPLv3 — see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
