# {projectDisplayName}

Version: {projectVersion}  
Manufacturer: {manufacturerName}  
Formats: {pluginFormats}

## Build Instructions

### Prerequisites

#### Windows

- Windows 10 or later
- **Cursor** or **VS Code** with **CMake Tools** (and C/C++ debugging if you use **F5**)
- CMake 3.22+ (add to system PATH during installation)
- Visual Studio 2022 with "Desktop development with C++" workload
- JUCE 8 installed at `C:\Program Files\JUCE` (or set `JUCE_DIR` if elsewhere)

#### macOS

- macOS 13 or later (tested on recent releases)
- **Cursor** or **VS Code** with **CMake Tools** (and C/C++ debugging if you use **F5**)
- CMake 3.22+
- Ninja build system
- JUCE 8 installed at `/Applications/JUCE` (or set `JUCE_DIR` if elsewhere)

#### Linux

- Linux (e.g. Ubuntu 22.04; other distros: install equivalent packages)
- **Cursor** or **VS Code** with **CMake Tools** (and C/C++ debugging if you use **F5**)
- CMake 3.22+
- Ninja and a GDB-capable toolchain (example: `sudo apt install ninja-build build-essential gdb`)
- JUCE 8 installed at `/usr/local/JUCE` (or set `JUCE_DIR` if elsewhere)

### Environment Setup

JUCE is auto-detected at standard locations (`C:/Program Files/JUCE` on Windows, `/Applications/JUCE` on macOS, `/usr/local/JUCE` on Linux). If installed elsewhere, set `JUCE_DIR`:

**Windows:**

```powershell
# System environment variable: JUCE_DIR = C:\path\to\JUCE
```

**macOS:**

```bash
export JUCE_DIR=/path/to/JUCE
```

**Linux:**

```bash
export JUCE_DIR=/path/to/JUCE
```

### Build

**Important:** Build directories are separated by platform and architecture (`Builds/Windows`, `Builds/macOS/ARM`, `Builds/macOS/Intel`, `Builds/macOS/Intel-Rosetta`, `Builds/macOS/Universal`, `Builds/Linux`) to avoid mixing files when switching between configurations.

After building, plugins are copied according to the **USER OPTIONS** section at the top of `CMakeLists.txt`:
- **System folders**: for immediate DAW testing
- **Central artefacts folder**: for centralized organization (if `COPY_TO_ARTEFACTS_DIR` is ON)

#### macOS (Apple Silicon)

```bash
# Configure (using Ninja)
cmake -B Builds/macOS/ARM -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_OSX_ARCHITECTURES=arm64

# Build all formats
cmake --build Builds/macOS/ARM --config Debug

# Or build specific format
cmake --build Builds/macOS/ARM --target {projectName}_Standalone --config Debug
cmake --build Builds/macOS/ARM --target {projectName}_AU --config Debug
cmake --build Builds/macOS/ARM --target {projectName}_VST3 --config Debug
```

#### macOS (Intel) — native on Mac Intel

**Note:** On Apple Silicon, this preset is rejected at configure; use "macOS Intel-Rosetta" instead. On Mac Intel, the Apple Silicon (ARM) preset is rejected at configure—stay on this Intel native flow.

```bash
# Configure (using Ninja)
cmake -B Builds/macOS/Intel -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_OSX_ARCHITECTURES=x86_64

# Build all formats
cmake --build Builds/macOS/Intel --config Debug

# Or build specific format
cmake --build Builds/macOS/Intel --target {projectName}_Standalone --config Debug
cmake --build Builds/macOS/Intel --target {projectName}_AU --config Debug
cmake --build Builds/macOS/Intel --target {projectName}_VST3 --config Debug
```

#### macOS (Intel-Rosetta) — x86_64 on Apple Silicon

When building for Intel compatibility on an Apple Silicon Mac, use the Intel-Rosetta preset. Build outputs go to your configured central artefacts folder under `macOS/Intel-Rosetta/` (path set in `CMakeLists.txt` via `ARTEFACTS_DIR_MACOS`). On Mac Intel, this preset is rejected at configure; use "macOS Intel" instead.

```bash
# Configure (using preset)
cmake --preset default-macos-x86_64-rosetta

# Build all formats
cmake --build --preset default-macos-x86_64-rosetta

# Or manual mode
cmake -B Builds/macOS/Intel-Rosetta -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_OSX_ARCHITECTURES=x86_64
cmake --build Builds/macOS/Intel-Rosetta --config Debug
```

#### macOS (Universal)

For **distribution**, build a Universal Binary (Apple Silicon + Intel in a single `.vst3` / `.component` / `.app`). One file works on both Apple Silicon and Intel Macs. Note: binaries are ~2× larger and builds take longer than single-architecture builds.

```bash
# Configure (using preset)
cmake --preset default-macos-universal

# Build all formats
cmake --build --preset default-macos-universal

# Or manual mode
cmake -B Builds/macOS/Universal -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64"
cmake --build Builds/macOS/Universal --config Debug

# Or build specific format
cmake --build Builds/macOS/Universal --target {projectName}_Standalone --config Debug
cmake --build Builds/macOS/Universal --target {projectName}_AU --config Debug
cmake --build Builds/macOS/Universal --target {projectName}_VST3 --config Debug
```

To verify the binary contains both architectures: `lipo -archs Builds/macOS/Universal/{projectName}_artefacts/Debug/{projectName}.vst3/Contents/MacOS/{projectName}` (should show `arm64 x86_64`).

#### Windows

```powershell
# Configure (using Visual Studio 2022)
cmake -B Builds/Windows -G "Visual Studio 17 2022" -DCMAKE_BUILD_TYPE=Debug

# Build all formats
cmake --build Builds/Windows --config Debug

# Or build specific format
cmake --build Builds/Windows --target {projectName}_Standalone --config Debug
cmake --build Builds/Windows --target {projectName}_VST3 --config Debug
```

**Note:** Audio Unit (AU) format is only available on macOS. On Windows, only VST3 and Standalone formats are built.

### Using Cursor or VS Code

The project uses **CMake Presets** for flexible configuration. Simply:

1. Open the project folder in **Cursor** or **VS Code** (CMake Tools extension installed)
2. Select your preferred CMake preset when prompted:
   - **Windows**: `default-windows` → builds to `Builds/Windows`
   - **macOS Apple Silicon (Native)**: `default-macos-arm64` → builds to `Builds/macOS/ARM`
   - **macOS Intel (Native on Mac Intel)**: `default-macos-x86_64` → builds to `Builds/macOS/Intel`
   - **macOS Intel-Rosetta (x86_64 on Apple Silicon)**: `default-macos-x86_64-rosetta` → builds to `Builds/macOS/Intel-Rosetta`
   - **macOS Universal (Distribution)**: `default-macos-universal` → builds to `Builds/macOS/Universal`
   - **Linux**: `default-linux` → builds to `Builds/Linux`

3. Build the project:
   - **Recommended**: `Cmd+Shift+B` (macOS) / `Ctrl+Shift+B` (Windows/Linux) if mapped to the default build task, or **F7** if you use CMake Tools defaults
   - **Or** command palette: `Cmd+Shift+P` / `Ctrl+Shift+P` → **CMake: Build**
   - **Or** **Tasks: Run Task** → choose a build task

**Switching presets**: Click the preset name in the status bar or use the palette → **CMake: Select Configure Preset**. CMake output paths (including debug `launch.json` placeholders) follow the active preset.

#### C++ IntelliSense (no false red squiggles on JUCE includes)

1. **Wait for CMake to finish configuring** after opening the folder (status bar). IntelliSense needs the same include paths and defines as the active CMake target.
2. **Ninja / Makefile** presets generate `compile_commands.json` in the build tree; CMake Tools is set to **copy it to the project root** so tools that look there can find it. The root copy is gitignored.
3. This template uses **CMake Tools** plus **Microsoft C/C++** with CMake as the configuration provider. **clangd** is disabled in `.vscode/settings.json` and listed under **unwantedRecommendations** in `.vscode/extensions.json` so you do not get duplicate or conflicting diagnostics from two language servers.
4. **Windows** with the **Visual Studio** generator may not emit `compile_commands.json`; C/C++ IntelliSense still follows CMake Tools once configuration succeeds.

If the **CMake** status bar or a **terminal task** still shows **“Task has errors”** after a build that actually finished successfully, it is often a **false positive** from CMake Tools **output parsers** matching harmless lines (for example `cmake -E echo` from post-build copy steps). The generated `.vscode/settings.json` disables the generic **`cmake`** parser and keeps **compiler** parsers (`gcc`, `gnuld`, `msvc`, …). **Build** tasks in `tasks.json` use **no** `problemMatcher` so the shell task does not re-flag the same output—use the **Problems** panel for real compiler diagnostics.

### Build Artefacts

After building, plugins are automatically copied according to the **USER OPTIONS** section at the top of `CMakeLists.txt`:

1. **System folders** (`COPY_TO_SYSTEM_FOLDERS`): Copies to standard locations where DAWs scan
   - **Windows**: VST3 → `C:\Program Files\Common Files\VST3\`. At each build, a **UAC prompt** appears—click **Yes** to copy. If you click No, the build still succeeds but the plugin is not copied.
   - **macOS**: `~/Library/Audio/Plug-Ins/Components/` (AU), `~/Library/Audio/Plug-Ins/VST3/` (VST3)
   - **Linux**: `~/.vst3/`

2. **Central custom folder** (`COPY_TO_ARTEFACTS_DIR`): Organized location for all projects
   - Paths injected at generation (`ARTEFACTS_DIR_*`)
   - **Structure**: `{{ARTEFACTS_DIR}}/{{OS}}/{{arch}}/{{format}}/`
   - **Windows**: `Windows/VST3/`, `Windows/Standalone/`
   - **macOS**: `macOS/ARM/`, `Intel/`, `Intel-Rosetta/`, or `Universal/` (each contains `AU/`, `VST3/`, `Standalone/`)
   - **Linux**: `Linux/VST3/`, `Linux/Standalone/`

The destination **automatically matches your selected preset**. No manual configuration needed.

### Build Artefact Copy Configuration

Control where plugins are copied after each build by editing the **USER OPTIONS** section at the top of `CMakeLists.txt`:

- **`USER_COPY_TO_SYSTEM_FOLDERS`**: `ON`/`OFF`
  - Copies to standard locations where DAWs scan: **macOS/Linux** use JUCE’s built-in copy to user plugin folders; **Windows VST3** uses an elevated copy to `C:\Program Files\Common Files\VST3\` (UAC prompt when enabled)
  - **Use case**: Instant testing in your DAW
  
- **`USER_COPY_TO_ARTEFACTS_DIR`**: `ON`/`OFF`
  - Copies to central custom folder (paths `ARTEFACTS_DIR_*`)
  - Organized by platform and architecture
  - **Use case**: Centralized management, backup, distribution prep

Both can be enabled simultaneously for maximum convenience.

### Debugging

Debug configurations use the active CMake preset’s build directory (`cmake.buildDirectory`). Press **F5** when the **C/C++** extension and debugger back end match your OS (**cppvsdbg** on Windows, **lldb** on macOS, **cppdbg**/GDB on Linux for Standalone).

- **macOS**: Standalone; AU in Logic Pro; VST3 in Reaper; AU in Ableton Live—edit `launch.json` if your DAW is installed in a non-default location.
- **Windows**: Standalone; VST3 in Reaper (default executable path targets `C:\Program Files\REAPER (x64)\reaper.exe`—change it if Reaper lives elsewhere).
- **Linux**: **Standalone** is configured with **GDB** in `launch.json`. There is no default Linux Reaper path in the template; duplicate a launch entry and set the `program` path to your DAW if you need plugin debugging.

**JUCE Audio Plugin Host (`AudioPluginHost`):** In your JUCE checkout, `extras/AudioPluginHost` builds on **macOS, Windows, and Linux** (CMake or Projucer). Use it as a **lightweight host** to load and debug AU/VST3 quickly without a full DAW, in addition to **Standalone** and the DAW entries in `launch.json`.

### Command Line Usage (Advanced)

For advanced users or CI/CD:

```bash
# List available presets
cmake --list-presets

# Configure with a specific preset
cmake --preset default-macos-universal

# Build with the preset
cmake --build --preset default-macos-universal

# Or chain them
cmake --preset default-macos-universal && cmake --build --preset default-macos-universal
```
