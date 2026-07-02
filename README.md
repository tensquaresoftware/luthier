# Luthier

A Projucer-inspired desktop GUI for creating, reopening, and configuring CMake-based JUCE audio plugin projects.

![Luthier](luthier.png)

Luthier is a self-contained [PySide6](https://doc.qt.io/qtforpython/) desktop app that generates ready-to-build, CMake-based JUCE plugin projects (AU / VST3 / Standalone): fill a form, validate inline, and generate. It can also reopen an existing generated project to tweak and regenerate it, and stores your defaults in a persistent preferences file — no hand-editing of configuration scripts.

## Features

- **Project** — one scrollable page for the whole plugin:
  - identity: technical/display names, version, manufacturer, copyright, website, e-mail, plugin & manufacturer codes, auto-computed bundle ID, with live inline validation;
  - plugin type (Instrument, Audio Effect, MIDI Effect) and formats (AU, VST3, Standalone);
  - compilation: C++ standard, preprocessor definitions, header search paths;
  - artefacts: copy to system plugin folders and/or a central per-OS directory.
- **Preferences** — persistent defaults (identity + default artefact settings) stored as JSON in the OS configuration directory.
- **Templates** — view, edit, replace, or reset the C++ source templates (`PluginProcessor` / `PluginEditor`) used for new projects; overrides persist on disk.
- **Reopen a project** — read an existing generated project back into the form and regenerate it in place.

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

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for full developer setup (venv, pytest, bundle build) and **[_bmad-output/architecture.md](_bmad-output/architecture.md)** for the three-layer design and module contracts.

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

## License

Luthier is released under the [MIT License](LICENSE).

Packaged builds are distributed with Qt (via PySide6) under the LGPLv3 — see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
