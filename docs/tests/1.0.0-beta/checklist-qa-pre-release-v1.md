# Luthier — Essential pre-release QA for v1.0.0

**Target version:** 1.0.0  
**Build to install:** commit **`c893cec`** — **About** tab: version **1.0.0**, revision date **2026-07-02**  
**Audience:** tester without technical background  
**App language:** English (labels quoted as shown on screen)  
**Estimated duration:**

| Scenario | Duration |
| --- | --- |
| One machine, regressions + new features | ~45 min |
| Workspace smoke on all 3 OS | ~30 min (10 min/OS) |
| Complete `VoyageLuthier` Git workflow | ~30 min |

> **Goal:** do not rerun the full [detailed checklist](checklist-qa-manuelle.md) or [single pass](checklist-qa-passe-unique.md). This sheet covers **only** what changed since 30/06 and what remained **unchecked** or **failed** when testing stopped.

---

## Already validated — do not repeat

Check mentally; skip directly to the sections below if you use the **same build** or a **newer** build than the one tested on 30/06.

| Area | Status | Reference |
| --- | --- | --- |
| Full Part 1 workflow (A/B/C, steps 1–9) | ✅ | [checklist-qa-manuelle.md](checklist-qa-manuelle.md) — 2026-06-29 |
| Regressions R1, R4, R5, R6 (accents, `/` messages, dirty form, red error, corrupt prefs) | ✅ | [checklist-qa-passe-unique.md](checklist-qa-passe-unique.md) |
| `VoyageLuthier` Git workflow 2.2 → 2.4 (Mac → Win → Linux) | ✅ | manual checklist + single pass |
| WinError 5 on `.git` (Windows) | ✅ fixed | commits `60dc52e`, **`c893cec`** |
| Export Preferences with full path | ✅ | R2 single pass |
| Import / export profile, Templates, basic validation | ✅ | manual Part 1 |

**Do not retest** unless a point below fails: manufacturer codes, Audio Effect / VST3-only variants, preprocessor defs, optional CMake builds already OK.

---

## Fixes and features to validate (since 30/06)

Related commits: `78dcf03` (QA fixes), `e78bce6` (Workspace per-OS), `fc433ac` (mandatory sidecar), `3213eb0` / `6888e19` (UI indentation), **`26dcd0d`** (project color + sidecar message), **`c893cec`** (Windows WinError `.git`).

### Common prerequisites (each OS)

- [x] **1.0.0** build from **2026-07-02** installed.
- [x] **About**: version **1.0.0**, revision **2026-07-02**.
- [x] Local JUCE available; effective paths are:

| OS | JUCE (example) |
| --- | --- |
| macOS | `/Volumes/Guillaume/Dev/SDKs/JUCE` |
| Windows | `C:/Users/Guillaume/Dev/SDKs/JUCE` |
| Linux | `/home/guillaume/Dev/SDKs/JUCE` |

---

## Part 1 — Workspace per-OS (Epic 8.1)

> **Major change:** the **Paths** section becomes **Workspace** with **six fields** (destination + JUCE × Windows / macOS / Linux). Only the **host OS** row has a **Choose…** button.

### W1 — Preferences → Workspace (~5 min/OS)

- [x] **Preferences** tab → **Workspace** section visible (no single **Paths** section).
- [x] Under **Destination folder**: three **Windows**, **macOS**, **Linux** rows — slightly **indented** under the title.
- [x] Under **JUCE directory**: same three-line indented layout.
- [x] On **your host OS** only: **Choose…** button next to destination and JUCE; the other two OS = manual entry.
- [x] **Choose…** destination → folder with **accents** (e.g. `Téléchargements`, `été 2026`) → **no** red error; **Saved** badge possible.
- [x] Enter the **host** JUCE path; enter plausible paths for the **other two OS** (used later cross-platform).
- [x] Close / reopen Luthier: all **six** values are preserved.
- [x] **Export Preferences…** → **Import Preferences…**: all six fields return.

### W2 — Project → Workspace (~5 min/OS)

- [x] **Create New Project** → **Workspace** fields match your **Preferences** (six paths).
- [x] **Project name** `TestLuthier` → **Generate Project** → success **without** an unexpected folder dialog (host destination already valid).
- [x] Open `.luthier.json` in the generated folder: all six Workspace paths are present (metadata reference).
- [x] **Choose…** on a host row → **Saved** badge visible (as in **Preferences**).

### W3 — Legacy settings migration (one machine is enough)

> If your `preferences.json` was already migrated on a previous launch, check and skip.

- [x] *(Optional)* Before first launch of the new build: back up `preferences.json` (locations below).
- [x] First launch: no crash; **Workspace** section filled (legacy `destinationDir` / `juceDir` keys spread to host OS if migration needed).
- [x] Identity (**Manufacturer**, color, etc.) **unchanged** after migration.

### W3b — Cross-platform import (Dropbox / USB) (~5 min)

> **Key scenario:** export prefs on one machine, import on another, complete **host** paths with **Choose…**.

- [x] Machine A (e.g. Linux): customize **Preferences** → **Export Preferences…** to Dropbox.
- [x] Machine B (e.g. macOS): **Import Preferences…** → **success** even if the **macOS destination** row is still empty.
- [x] Machine A paths (e.g. Linux) are present; host rows on B are empty or to be completed.
- [x] **Choose…** on destination and **host** JUCE → **Saved** badge → close / reopen Luthier: host paths preserved.
- [x] **Create New Project**: all six Workspace paths are re-seeded from the imported profile.

| OS | Config folder |
| --- | --- |
| macOS | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\` |
| Linux | `~/.config/Luthier/` |

### W4 — Workspace + Artefacts indentation (cosmetic, ~1 min/OS)

- [x] **Preferences** → **Workspace** and **Artefacts** sections: **Windows / macOS / Linux** labels visually aligned with **checkbox** text (same left margin).
- [x] **Project** → **Workspace** and **Artefacts** sections: same alignment.

---

## Part 2 — Write-only sidecar (Epic 9 — replaces « mandatory sidecar for Open »)

> **v1.0.0 scaffold-only:** `.luthier.json` is **written** on **Generate Project**; Luthier **does not read it back**. No **Open Project…** button.

### S1 — Sidecar present after generate (~3 min)

- [x] **Generate Project** → `.luthier.json` present in the project folder.
- [x] Open `.luthier.json`: Workspace paths use **`/`**; **no** `accentColor` key.
- [x] Luthier offers **no** way to reload the sidecar into the form.

### S2 — Cross-platform `.luthier.json` (Git reference)

- [x] Keys `destinationDirWindows`, `juceDirMacos`, etc. present after generate.
- [x] On another machine: manually edit the **host** JUCE path in `.luthier.json` or **Preferences**, then CMake build — **without** Open in Luthier.

---

## Part 3 — Open items from the single pass

> Boxes left empty or marked ❌ in [checklist-qa-passe-unique.md](checklist-qa-passe-unique.md).

### P1 — Windows modals (R3) — Windows only

- [x] **Create New Project** after edit without generate → **No** default (No/Yes order cosmetic — accepted minor).
- [x] **Generate Project** on existing folder → same behavior.

*(Button order: minor Qt Windows issue — not blocking for release.)*

### P2 — Linux: icon and window geometry (R7) — Linux only

- [x] Launcher / taskbar: Luthier icon visible.
- [x] Resize and move the window → close → reopen: size **roughly** restored; **position not guaranteed** (accepted v1 limitation, especially Wayland).

### P3 — Quick post-Workspace smoke

> Not applicable — W1 + W2 already validated on all **three** OS.

| OS | Status |
| --- | --- |
| macOS | [x] W1 + W2 validated |
| Windows | [x] W1 + W2 + **Generate** on Git clone without WinError (`c893cec`) |
| Linux | [x] W1 + W2 validated |

---

## Part 4 — Complete `VoyageLuthier` Git workflow

**Repo:** https://github.com/tensquaresoftware/voyage-luthier

### 4.1 — Return to macOS (finalization)

- [x] `git pull` — latest Linux revision (`1.2.0`, `LINUX_QA=1`).
- [x] Open `.luthier.json` in the editor: **Version** `1.2.0`; **Preprocessor defs** contains `LINUX_QA=1`.
- [x] Adjust **JUCE directory** **macOS** row in `.luthier.json` or **Preferences** if needed → CMake build (no Luthier Open).
- [x] **Create New Project** in Luthier for a **new** generation if you need to regenerate the starter project (empty folder or session regenerate).

### 4.2 — Final checks (3 OS, ~10 min/OS or 1 OS + spot-check)

- [x] Git clone → edit host paths in `.luthier.json` if needed → **consistent CMake build** on each OS (no **Open Project…**).
- [x] **Import Preferences…** from JSON from another machine → **Preferences** updated; **Project** form unchanged until **Create New Project**.
- [x] **No Luthier crash** during 4.1–4.2.

### VoyageLuthier summary

| Step | Machine | Version | Display name |
| --- | --- | --- | --- |
| Creation | macOS | 1.0.0 | Voyage Cross QA macOS |
| Windows | Windows | 1.1.0 | … Windows |
| Linux | Linux | 1.2.0 | (unchanged or …) |
| **Final Mac** | **macOS** | **1.2.0** | **… Final** |

---

## Success criteria (go for release)

Pre-release QA is **successful** when:

- [x] **Part 1 (W1–W4)** OK on **macOS, Windows, and Linux**.
- [x] **Part 2 (S1–S2)** OK — mandatory sidecar confirmed.
- [x] **Part 4** complete (final Mac + Git consistency on all 3 OS).
- [x] **No blocking** issues open.
- [x] Known **minor** issues accepted for v1.0.0:
  - modal button order on Windows (P1);
  - Linux window position not guaranteed (P2).

**Decision: go for v1.0.0 release** — build **`c893cec`**, revision **2026-07-02**.

---

## Tracking grid

| # | OS | Section | What were you doing? | Expected | Actual | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| — | — | — | *(no open items)* | — | — | — |

**Severity:** **blocking** = cannot continue or data loss risk; **annoying** = painful workaround; **minor** = cosmetic or rare case.

---

## References

- [Detailed QA checklist (archive)](checklist-qa-manuelle.md)
- [Single-pass Workspace QA (archive)](checklist-qa-passe-unique.md)
- [User manual (EN)](../user/user-manual.md)
