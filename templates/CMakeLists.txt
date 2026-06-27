# JUCE audio plugin project (CMake). Do not remove cmake_minimum_required / project() order.
cmake_minimum_required(VERSION 3.22)

# IDE: compile_commands.json (Ninja / Makefile generators). Set before project() so generation picks it up.
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Platform-specific configuration
if(APPLE)
    # Real host arch (uname -m): reliable on Apple Silicon even when CMake runs under Rosetta
    execute_process(COMMAND uname -m OUTPUT_VARIABLE HOST_ARCH OUTPUT_STRIP_TRAILING_WHITESPACE)
    # Architecture is set per-preset in CMakeUserPresets.json (arm64 for Apple Silicon, x86_64 for Intel)
    if(NOT CMAKE_OSX_ARCHITECTURES)
        set(CMAKE_OSX_ARCHITECTURES "arm64" CACHE STRING "Build architectures for macOS (arm64 or x86_64)")
    endif()
    # Preset vs host consistency: avoid wrong preset for the current machine
    # - Apple Silicon: reject "macOS Intel" (native); use "macOS Intel-Rosetta"
    # - Mac Intel: reject "macOS Intel-Rosetta" and "macOS Apple Silicon" (ARM); use "macOS Intel" (native)
    if(HOST_ARCH STREQUAL "arm64")
        # Rosetta builds use .../Intel-Rosetta, so they do not match .../Intel/?$ at end of path.
        if(CMAKE_BINARY_DIR MATCHES "Builds/macOS/Intel/?$")
            message(FATAL_ERROR
                "On Apple Silicon, do not use the 'macOS Intel' preset (default-macos-x86_64; meant for native Mac Intel). Use 'macOS Intel-Rosetta' instead (preset default-macos-x86_64-rosetta): in Cursor select that preset. To list all presets: cmake --list-presets.")
        endif()
    elseif(HOST_ARCH STREQUAL "x86_64" OR HOST_ARCH STREQUAL "i386")
        if(CMAKE_BINARY_DIR MATCHES "Intel-Rosetta")
            message(FATAL_ERROR
                "On Mac Intel, do not use the 'macOS Intel-Rosetta' preset (default-macos-x86_64-rosetta; meant for Apple Silicon). Use 'macOS Intel' instead (preset default-macos-x86_64): in Cursor select that preset. To list all presets: cmake --list-presets.")
        endif()
        if(CMAKE_BINARY_DIR MATCHES "Builds/macOS/ARM/?$")
            message(FATAL_ERROR
                "On Mac Intel, do not use the 'macOS Apple Silicon' preset (default-macos-arm64). Use 'macOS Intel' instead (preset default-macos-x86_64): in Cursor select that preset. To list all presets: cmake --list-presets.")
        endif()
    endif()
    # Use Ninja generator on macOS if not specified
    if(NOT CMAKE_GENERATOR)
        find_program(NINJA_EXE ninja)
        if(NINJA_EXE)
            set(CMAKE_GENERATOR "Ninja" CACHE INTERNAL "")
        endif()
    endif()
elseif(WIN32)
    # Use Visual Studio generator on Windows if not specified
    if(NOT CMAKE_GENERATOR)
        set(CMAKE_GENERATOR "Visual Studio 17 2022" CACHE INTERNAL "")
    endif()
endif()

project({projectName} VERSION {projectVersion})

# =============================================================================
# PLUGIN COPY CONFIGURATION
# COPY_TO_SYSTEM_FOLDERS: ON/OFF — copies plugins to standard DAW scan locations
#   Windows: VST3 → C:\Program Files\Common Files\VST3\ (UAC prompt)
#   macOS: AU → ~/Library/Audio/Plug-Ins/Components/, VST3 → ~/Library/Audio/Plug-Ins/VST3/
#   Linux: VST3 → ~/.vst3/
# COPY_TO_ARTEFACTS_DIR: ON/OFF — copies build outputs to a central custom folder
#   (ARTEFACTS_DIR_WINDOWS/MACOS/LINUX, organized by platform and architecture)
# Override at configure time: cmake .. -DUSER_COPY_TO_ARTEFACTS_DIR=ON
# =============================================================================

set(USER_COPY_TO_SYSTEM_FOLDERS {copyToSystemFolders})
set(USER_COPY_TO_ARTEFACTS_DIR {copyToArtefactsDir})

set(COPY_TO_SYSTEM_FOLDERS ${{USER_COPY_TO_SYSTEM_FOLDERS}} CACHE BOOL "Copy plugins to system folders after build (all OS)")
set(COPY_TO_ARTEFACTS_DIR ${{USER_COPY_TO_ARTEFACTS_DIR}} CACHE BOOL "Copy build outputs to central artefacts folder (organized by platform/architecture)")

set(ARTEFACTS_DIR_WINDOWS "{artefactsDirWindows}")
set(ARTEFACTS_DIR_MACOS   "{artefactsDirMacos}")
set(ARTEFACTS_DIR_LINUX   "{artefactsDirLinux}")

set(CMAKE_CXX_STANDARD {cxxStandard})
set(CMAKE_CXX_STANDARD_REQUIRED ON)

{juceDirSetLine}# Reference JUCE: priority cache (preset/-D), then ENV, then platform default
# Portable logic - works on any platform regardless of where the project was generated
set(JUCE_DIR_CANDIDATE "")
if(DEFINED JUCE_DIR AND NOT JUCE_DIR STREQUAL "" AND EXISTS "${{JUCE_DIR}}")
    set(JUCE_DIR_CANDIDATE "${{JUCE_DIR}}")
elseif(DEFINED ENV{{JUCE_DIR}} AND NOT "$ENV{{JUCE_DIR}}" STREQUAL "")
    set(JUCE_DIR_CANDIDATE "$ENV{{JUCE_DIR}}")
elseif(APPLE AND EXISTS "/Applications/JUCE")
    set(JUCE_DIR_CANDIDATE "/Applications/JUCE")
elseif(WIN32 AND EXISTS "C:/Program Files/JUCE")
    set(JUCE_DIR_CANDIDATE "C:/Program Files/JUCE")
elseif(UNIX AND EXISTS "/usr/local/JUCE")
    set(JUCE_DIR_CANDIDATE "/usr/local/JUCE")
endif()

if(JUCE_DIR_CANDIDATE STREQUAL "")
    message(FATAL_ERROR "JUCE not found. Set JUCE_DIR (e.g. export JUCE_DIR=/Applications/JUCE) or use -DJUCE_DIR=/path/to/JUCE")
endif()

set(JUCE_DIR "${{JUCE_DIR_CANDIDATE}}" CACHE PATH "Path to JUCE installation" FORCE)

if(NOT EXISTS "${{JUCE_DIR}}")
    message(FATAL_ERROR "JUCE not found at ${{JUCE_DIR}}. Check JUCE_DIR path.")
endif()

add_subdirectory(${{JUCE_DIR}} "${{CMAKE_BINARY_DIR}}/JUCE")

# ============================================================================
# SOURCE FILES
# Add your new .cpp files here (keep them sorted alphabetically for clarity)
# ============================================================================

set(PLUGIN_SOURCES
    # Core
    Source/PluginProcessor.cpp
    Source/PluginEditor.cpp
    
    # Add your new source files below
)

# =============================================================================
# PLUGIN CONFIGURATION
# =============================================================================

# Platform-specific plugin formats (filter out AU on Windows)
set(PLUGIN_FORMATS_LIST {pluginFormats})
if(NOT APPLE)
    # Remove AU from formats on non-Apple platforms
    string(REPLACE "AU " "" PLUGIN_FORMATS_LIST "${{PLUGIN_FORMATS_LIST}}")
    string(REPLACE " AU" "" PLUGIN_FORMATS_LIST "${{PLUGIN_FORMATS_LIST}}")
    string(REPLACE "AU" "" PLUGIN_FORMATS_LIST "${{PLUGIN_FORMATS_LIST}}")
    string(STRIP "${{PLUGIN_FORMATS_LIST}}" PLUGIN_FORMATS_LIST)
endif()

# COPY_PLUGIN_AFTER_BUILD: JUCE built-in copy for macOS and Linux only.
# On Windows, COPY_PLUGIN_AFTER_BUILD is OFF; VST3 → Program Files is done by CopyVST3ToSystemFolder (UAC).
# macOS: AU → ~/Library/Audio/Plug-Ins/Components/, VST3 → ~/Library/Audio/Plug-Ins/VST3/
# Linux: VST3 → ~/.vst3/
if(WIN32)
    set(COPY_PLUGIN_AFTER_BUILD_VALUE FALSE)
else()
    set(COPY_PLUGIN_AFTER_BUILD_VALUE ${{COPY_TO_SYSTEM_FOLDERS}})
endif()

juce_add_plugin({projectName}
    COMPANY_NAME "{manufacturerName}"
    COMPANY_COPYRIGHT "{companyCopyright}"
    COMPANY_WEBSITE "{companyWebsite}"
    COMPANY_EMAIL "{companyEmail}"
    BUNDLE_ID "{bundleId}"
    PLUGIN_MANUFACTURER_CODE "{manufacturerCode}"
    PLUGIN_CODE "{pluginCode}"
    FORMATS ${{PLUGIN_FORMATS_LIST}}
    PRODUCT_NAME "{projectName}"
	PLUGIN_NAME "{projectDisplayName}"
    IS_SYNTH {isSynth}
    NEEDS_MIDI_INPUT {needsMidiInput}
    NEEDS_MIDI_OUTPUT {needsMidiOutput}
    IS_MIDI_EFFECT {isMidiEffect}
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD ${{COPY_PLUGIN_AFTER_BUILD_VALUE}}
    VST3_CATEGORIES "{vst3Categories}"
    AU_MAIN_TYPE "{auMainType}"
)

target_sources({projectName} PRIVATE ${{PLUGIN_SOURCES}})

target_link_libraries({projectName}
    PRIVATE
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)

target_compile_definitions({projectName}
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
        JUCE_DISPLAY_SPLASH_SCREEN=0
        JUCE_REPORT_APP_USAGE=0
){headerSearchPathsBlock}{extraDefinitionsBlock}

# =============================================================================
# COPY TO CENTRAL ARTEFACTS FOLDER
# When COPY_TO_ARTEFACTS_DIR is ON, copies build outputs to a central custom folder.
# Paths: ARTEFACTS_DIR_WINDOWS, ARTEFACTS_DIR_MACOS, ARTEFACTS_DIR_LINUX (injected at generation).
# Structure: {{ARTEFACTS_DIR}}/{{OS}}/{{arch}}/{{format}}/
# - macOS: ARM/, Intel/, Intel-Rosetta/, Universal/
# - Windows/Linux: no arch subfolder
# Formats: VST3/, AU/ (macOS only), Standalone/. CLAP/ (Linux, future).
# Intel = x86_64 native (Mac Intel). Intel-Rosetta = x86_64 cross-compiled on Apple Silicon.
# Only copies formats selected for the project.
# =============================================================================

if(COPY_TO_ARTEFACTS_DIR)
    # Determine base artefacts directory for current OS
    if(APPLE)
        set(ARTEFACTS_DIR_BASE "${{ARTEFACTS_DIR_MACOS}}")
    elseif(WIN32)
        set(ARTEFACTS_DIR_BASE "${{ARTEFACTS_DIR_WINDOWS}}")
    else()
        set(ARTEFACTS_DIR_BASE "${{ARTEFACTS_DIR_LINUX}}")
    endif()

    # Determine architecture subfolder (macOS only)
    if(APPLE)
        set(ARCH_LIST ${{CMAKE_OSX_ARCHITECTURES}})
        list(FIND ARCH_LIST "arm64" IDX_ARM64)
        list(FIND ARCH_LIST "x86_64" IDX_X86_64)
        if(NOT IDX_ARM64 EQUAL -1 AND NOT IDX_X86_64 EQUAL -1)
            set(PLUGIN_ARCH_SUBFOLDER "Universal")
        elseif(NOT IDX_ARM64 EQUAL -1)
            set(PLUGIN_ARCH_SUBFOLDER "ARM")
        elseif(NOT IDX_X86_64 EQUAL -1)
            if(HOST_ARCH STREQUAL "arm64")
                set(PLUGIN_ARCH_SUBFOLDER "Intel-Rosetta")
            else()
                set(PLUGIN_ARCH_SUBFOLDER "Intel")
            endif()
        else()
            set(PLUGIN_ARCH_SUBFOLDER "ARM")
        endif()
        set(ARTEFACTS_DEST "${{ARTEFACTS_DIR_BASE}}/macOS/${{PLUGIN_ARCH_SUBFOLDER}}")
    elseif(WIN32)
        set(ARTEFACTS_DEST "${{ARTEFACTS_DIR_BASE}}/Windows")
    else()
        set(ARTEFACTS_DEST "${{ARTEFACTS_DIR_BASE}}/Linux")
    endif()

    message(STATUS "Build artefacts will be copied to: ${{ARTEFACTS_DEST}}")
endif()

# Create custom target that copies all artefacts after build
if(COPY_TO_ARTEFACTS_DIR)
    set(ALL_PLUGIN_TARGETS)
    set(COPY_COMMANDS)
    
    # VST3
    if(PLUGIN_FORMATS_LIST MATCHES "VST3")
        list(APPEND ALL_PLUGIN_TARGETS "{projectName}_VST3")
        set(VST3_SOURCE_DIR "${{CMAKE_BINARY_DIR}}/{projectName}_artefacts/$<CONFIG>/VST3/{projectName}.vst3")
        set(VST3_DEST_DIR "${{ARTEFACTS_DEST}}/VST3/{projectName}.vst3")
        list(APPEND COPY_COMMANDS
            COMMAND ${{CMAKE_COMMAND}} -E echo "Copying VST3 to ${{ARTEFACTS_DEST}}/VST3/"
            COMMAND ${{CMAKE_COMMAND}} -E make_directory "${{ARTEFACTS_DEST}}/VST3"
            COMMAND ${{CMAKE_COMMAND}} -E remove_directory "${{VST3_DEST_DIR}}"
            COMMAND ${{CMAKE_COMMAND}} -E copy_directory "${{VST3_SOURCE_DIR}}" "${{VST3_DEST_DIR}}"
        )
    endif()
    
    # Standalone
    if(PLUGIN_FORMATS_LIST MATCHES "Standalone")
        list(APPEND ALL_PLUGIN_TARGETS "{projectName}_Standalone")
        if(APPLE)
            set(STANDALONE_SOURCE "${{CMAKE_BINARY_DIR}}/{projectName}_artefacts/$<CONFIG>/Standalone/{projectName}.app")
            set(STANDALONE_DEST_DIR "${{ARTEFACTS_DEST}}/Standalone/{projectName}.app")
            list(APPEND COPY_COMMANDS
                COMMAND ${{CMAKE_COMMAND}} -E echo "Copying Standalone to ${{ARTEFACTS_DEST}}/Standalone/"
                COMMAND ${{CMAKE_COMMAND}} -E make_directory "${{ARTEFACTS_DEST}}/Standalone"
                COMMAND ${{CMAKE_COMMAND}} -E remove_directory "${{STANDALONE_DEST_DIR}}"
                COMMAND ${{CMAKE_COMMAND}} -E copy_directory "${{STANDALONE_SOURCE}}" "${{STANDALONE_DEST_DIR}}"
            )
        elseif(WIN32)
            set(STANDALONE_SOURCE "${{CMAKE_BINARY_DIR}}/{projectName}_artefacts/$<CONFIG>/Standalone/{projectName}.exe")
            set(STANDALONE_DEST "${{ARTEFACTS_DEST}}/Standalone/{projectName}.exe")
            list(APPEND COPY_COMMANDS
                COMMAND ${{CMAKE_COMMAND}} -E echo "Copying Standalone to ${{ARTEFACTS_DEST}}/Standalone/"
                COMMAND ${{CMAKE_COMMAND}} -E make_directory "${{ARTEFACTS_DEST}}/Standalone"
                COMMAND ${{CMAKE_COMMAND}} -E copy "${{STANDALONE_SOURCE}}" "${{STANDALONE_DEST}}"
            )
        else()
            set(STANDALONE_SOURCE "${{CMAKE_BINARY_DIR}}/{projectName}_artefacts/$<CONFIG>/Standalone/{projectName}")
            set(STANDALONE_DEST "${{ARTEFACTS_DEST}}/Standalone/{projectName}")
            list(APPEND COPY_COMMANDS
                COMMAND ${{CMAKE_COMMAND}} -E echo "Copying Standalone to ${{ARTEFACTS_DEST}}/Standalone/"
                COMMAND ${{CMAKE_COMMAND}} -E make_directory "${{ARTEFACTS_DEST}}/Standalone"
                COMMAND ${{CMAKE_COMMAND}} -E copy "${{STANDALONE_SOURCE}}" "${{STANDALONE_DEST}}"
            )
        endif()
    endif()
    
    # AU (macOS only)
    if(APPLE AND PLUGIN_FORMATS_LIST MATCHES "AU")
        list(APPEND ALL_PLUGIN_TARGETS "{projectName}_AU")
        set(AU_SOURCE_DIR "${{CMAKE_BINARY_DIR}}/{projectName}_artefacts/$<CONFIG>/AU/{projectName}.component")
        set(AU_DEST_DIR "${{ARTEFACTS_DEST}}/AU/{projectName}.component")
        list(APPEND COPY_COMMANDS
            COMMAND ${{CMAKE_COMMAND}} -E echo "Copying AU to ${{ARTEFACTS_DEST}}/AU/"
            COMMAND ${{CMAKE_COMMAND}} -E make_directory "${{ARTEFACTS_DEST}}/AU"
            COMMAND ${{CMAKE_COMMAND}} -E remove_directory "${{AU_DEST_DIR}}"
            COMMAND ${{CMAKE_COMMAND}} -E copy_directory "${{AU_SOURCE_DIR}}" "${{AU_DEST_DIR}}"
        )
    endif()
    
    # Create the custom target with all copy commands
    add_custom_target(CopyToArtefactsDir ALL
        ${{COPY_COMMANDS}}
        DEPENDS ${{ALL_PLUGIN_TARGETS}}
        COMMENT "Copying all plugin artefacts to ${{ARTEFACTS_DEST}}"
        VERBATIM
    )
endif()

# =============================================================================
# COPY TO SYSTEM FOLDERS (Windows only - global folder, UAC elevation)
# On Windows, we copy to C:\Program Files\Common Files\VST3\ (Ableton/DAW standard).
# Copy runs elevated via PowerShell (UAC prompt); if user cancels, build still succeeds.
# macOS and Linux use JUCE's built-in copy.
# =============================================================================
if(WIN32 AND COPY_TO_SYSTEM_FOLDERS AND PLUGIN_FORMATS_LIST MATCHES "VST3")
    set(VST3_SYSTEM_DEST "C:/Program Files/Common Files/VST3")
    set(VST3_ELEVATED_SCRIPT "${{CMAKE_SOURCE_DIR}}/CMake/CopyVst3Elevated.ps1")
    set(VST3_SOURCE_PATH "${{CMAKE_BINARY_DIR}}/{projectName}_artefacts/$<CONFIG>/VST3/{projectName}.vst3")
    set(VST3_ARGS_FILE "${{CMAKE_BINARY_DIR}}/vst3_copy_args.txt")
    add_custom_target(CopyVST3ToSystemFolder ALL
        COMMAND ${{CMAKE_COMMAND}} -E echo "Copying VST3 to ${{VST3_SYSTEM_DEST}} (UAC may prompt for admin rights)..."
        COMMAND PowerShell -NoProfile -ExecutionPolicy Bypass -Command "Set-Content -LiteralPath '${{VST3_ARGS_FILE}}' -Value '${{VST3_SOURCE_PATH}}','${{VST3_SYSTEM_DEST}}' -Encoding UTF8"
        COMMAND PowerShell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process PowerShell -Verb RunAs -Wait -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','${{VST3_ELEVATED_SCRIPT}}','-ArgsFile','${{VST3_ARGS_FILE}}'; exit 0"
        DEPENDS {projectName}_VST3
        COMMENT "Copying VST3 to ${{VST3_SYSTEM_DEST}} (elevated)"
        VERBATIM
    )
endif()