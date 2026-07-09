# Investigation: macOS x86_64 Intel PyInstaller Build Feasibility

## Hand-off Brief

1. **What happened.** Luthier v1.0.0 ships an **arm64-only** `Dist/Luthier.app`; Intel Macs cannot run it (`Bad CPU type in executable`). Generated JUCE projects already support **Mac Intel via CMake presets** — the gap was only **Luthier.app distribution** on x86_64.
2. **Where the case stands.** **Concluded — out of scope.** Maintainer decision (2026-07-09): do **not** pursue Intel `Luthier.app`; audience marginal, Big Sur 2014 Mac cannot host current stack, dual-bundle QA not justified.
3. **What's needed next.** Document release requirement: **macOS Apple Silicon only** for `Luthier.app`; clarify that **generated projects remain Intel-capable**. Optional PRD/epic note amendment — no Story 10.2.

## Case Info

| Field            | Value                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------ |
| Ticket           | N/A (pre-release gap analysis for Story 10.2)                                              |
| Date opened      | 2026-07-09                                                                                 |
| Date closed      | 2026-07-09                                                                                 |
| Status           | **Concluded** — Intel `Luthier.app` explicitly out of scope for v1.0+                      |
| System           | Target: **MacBook Pro 15" mid-2014 i7**, macOS Big Sur 11.x (max official OS — **no Ventura upgrade path**). Investigation host: Apple M5 arm64, macOS 26.5.1 |
| Evidence sources | Story 4.1 artifact, PRD FR9/G5, `Build/luthier.spec`, PyPI wheel metadata, pip platform simulation, existing `Dist/Luthier.app` |

## Problem Statement

Luthier v1.0.0 is release-ready on Apple Silicon but macOS x86_64 distribution (FR9/G5) was never validated. The hypothesis is that the gap is **not** a design omission (generated projects include `macos-debug-x86_64` presets) but the **absence of an x86_64 PyInstaller build/test pipeline**, possibly compounded by **Python 3.14 + PySide6 6.11 being unavailable on Big Sur**.

## Evidence Inventory

| Source                                      | Status    | Notes                                                                 |
| ------------------------------------------- | --------- | --------------------------------------------------------------------- |
| `_bmad-output/implementation-artifacts/4-1-pyinstaller-bundle-macos.md` | Available | AC3 SKIP documented; arm64-only validation                            |
| `Dist/Luthier.app`                          | Available | Confirmed **arm64** Mach-O (`file`, `lipo -info`)                     |
| `Build/luthier.spec`                        | Available | Architecture-agnostic; no cross-compile                               |
| `templates/CMakeUserPresets.json`           | Available | `macos-debug-x86_64` / `macos-release-x86_64` presets present         |
| `.github/workflows/pytest.yml`              | Available | Ubuntu-only; no macOS build job                                       |
| PyPI PySide6 wheel metadata                 | Available | Platform tags queried via PyPI JSON API                               |
| pip platform simulation (Big Sur x86_64)    | Available | `--platform macosx_11_0_x86_64` dry-runs                              |
| Intel Mac hands-on logs                     | Missing   | Investigation ran on ARM64 host, not the Big Sur i7                   |
| Intel Mac `python main.py` / PyInstaller    | Missing   | Requires execution on target hardware                                 |

## Investigation Backlog

| # | Path to Explore                              | Priority | Status      | Notes                                           |
| - | -------------------------------------------- | -------- | ----------- | ----------------------------------------------- |
| 1 | Intel Mac: `pip install -r requirements-dev.txt` | High     | **Cancelled** | Case closed — Intel app out of scope            |
| 2 | Intel Mac: build with Python 3.12 + PySide6 6.7.3 | High     | **Cancelled** | Not pursuing legacy Intel bundle                |
| 3 | Intel Mac: upgrade path to macOS 13+         | Medium   | **Cancelled** | Hardware cannot upgrade (2014 MBP, Big Sur max) |
| 4 | Intel Mac: `publish/build-dist.py` full run  | High     | **Cancelled** | Story 10.2 abandoned                            |
| 5 | Self-hosted runner registration smoke        | Medium   | **Cancelled** | No Intel CI planned                             |
| 6 | Release matrix doc (dual-arch naming)        | Low      | **Cancelled** | Single-arch macOS release only                  |
| 7 | Release notes: macOS Apple Silicon only      | Medium   | **Done**      | Templates + user manuals updated (2026-07-09)   |

## Timeline of Events

| Time        | Event                                          | Source                          | Confidence |
| ----------- | ---------------------------------------------- | ------------------------------- | ---------- |
| 2026-06-25  | Story 4.1 done; AC3 x86_64 SKIP                | `4-1-pyinstaller-bundle-macos.md:267` | Confirmed  |
| 2026-06-25  | ARM64 bundle built: PyInstaller 6.20, PySide6 6.11.1, Python 3.14 | Story 4.1 completion notes | Confirmed  |
| 2026-07-09  | Existing `Dist/Luthier.app` is arm64-only      | `file` / `lipo` on investigation host | Confirmed  |
| 2026-07-09  | arm64 binary rejected under x86_64 execution   | `arch -x86_64 … Luthier --check` | Confirmed  |
| 2026-07-09  | PySide6 6.11.1 wheel tag: `macosx_13_0`        | PyPI JSON                       | Confirmed  |
| 2026-07-09  | `pip install` on Big Sur+Py3.14: no PySide6 wheel | pip simulation                  | Confirmed  |
| 2026-07-09  | Maintainer decision: Intel `Luthier.app` out of scope | User confirmation | Confirmed  |

## Confirmed Findings

### Finding 1: Existing bundle is ARM64-only; Intel cannot launch it

**Evidence:** `Dist/Luthier.app/Contents/MacOS/Luthier` → `Mach-O 64-bit executable arm64`; `lipo -info` → `architecture: arm64`.

**Detail:** Running the binary under x86_64 execution context yields:
```
arch: posix_spawnp: …/Luthier: Bad CPU type in executable
```
This is the expected macOS error when an arm64 binary is launched on x86_64 without Rosetta-translated arm64 execution (and Rosetta does not make an arm64 `.app` usable as an x86_64 distribution artefact).

### Finding 2: Story 4.1 explicitly SKIPped AC3 (x86_64)

**Evidence:** `_bmad-output/implementation-artifacts/4-1-pyinstaller-bundle-macos.md:267`

**Detail:** Completion notes state: "Dev machine is ARM64-only … PyInstaller cannot cross-compile; Rosetta running ARM64 `.app` is not a substitute."

### Finding 3: PyInstaller does not cross-compile (spec is arch-neutral)

**Evidence:** `Build/luthier.spec:71` comment; story 4.1 dev notes lines 167–172.

**Detail:** Same spec file works on any macOS arch; output arch matches the Python interpreter used to invoke PyInstaller.

### Finding 4: Generated JUCE projects support Intel presets (not Luthier itself)

**Evidence:** `templates/CMakeUserPresets.json` — `macos-debug-x86_64`, `macos-release-x86_64` with `CMAKE_OSX_ARCHITECTURES: x86_64`.

**Detail:** The gap is **Luthier app distribution**, not generated-project CMake presets.

### Finding 5: PySide6 wheel macOS minimum version escalates with release line

**Evidence:** PyPI wheel filenames (queried 2026-07-09):

| PySide6  | macOS wheel tag   | Requires-Python |
| -------- | ----------------- | --------------- |
| 6.7.3    | `macosx_11_0`     | `>=3.9,<3.13`   |
| 6.8.3    | `macosx_12_0`     | `>=3.9,<3.14`   |
| 6.9.2    | `macosx_12_0`     | `>=3.9,<3.14`   |
| 6.10.1   | `macosx_13_0`     | `>=3.9,<3.15`   |
| 6.11.1   | `macosx_13_0`     | `>=3.10,<3.15`  |

**Detail:** Big Sur = macOS **11.x**. Only PySide6 **≤6.7.x** ships wheels tagged `macosx_11_0`. Current `requirements.txt` (`PySide6>=6.7`) resolves to **6.11.1**, which requires **macOS 13.0+**.

### Finding 6: `pip install -r requirements-dev.txt` fails on Big Sur + Python 3.14

**Evidence:** pip simulation `--platform macosx_11_0_x86_64 --python-version 3.14 --ignore-installed`:
```
ERROR: Could not find a version that satisfies the requirement PySide6>=6.7 (from versions: none)
```

### Finding 7: Big Sur + Python 3.12 can install deps (but pins PySide6 6.7.3, not 6.11)

**Evidence:** Same pip simulation with `--python-version 3.12` → `Would install PySide6-6.7.3 … pyinstaller-6.21.0 …`.

### Finding 8: CI has no macOS build job

**Evidence:** `.github/workflows/pytest.yml` — `runs-on: ubuntu-latest` only; pytest on Python 3.11.

## Deduced Conclusions

### Deduction 1: User hypothesis is largely confirmed

**Based on:** Findings 2, 5, 6

**Reasoning:** The x86_64 gap is operational (no Intel build machine in the ARM64 workflow), not a template/design omission. On Big Sur specifically, the **current release stack is blocked at dependency install** before any PyInstaller step.

### Deduction 2: Two viable paths for Intel builds

**Based on:** Findings 5, 6, 7

**Reasoning:**

| Path | macOS floor | Python | PySide6 | Parity with ARM64 release |
| ---- | ----------- | ------ | ------- | ------------------------- |
| **A — Upgrade Intel Mac** | Ventura 13+ | 3.14 | 6.11.x | Full stack parity |
| **B — Stay on Big Sur** | Big Sur 11 | 3.12 (max for 6.7) | 6.7.3 (pin) | Divergent stack; regression risk |

Path A is strongly preferred for v1.0.0 release parity. Path B is a fallback if hardware cannot be upgraded.

### Deduction 3: `python main.py` on Intel with current docs would fail on Big Sur

**Based on:** Findings 5, 6, `CONTRIBUTING.md` quick-start

**Reasoning:** Following documented `pip install -r requirements-dev.txt` on Big Sur fails at PySide6 resolution. Error is dependency/platform, not application code.

## Hypothesized Paths

### Hypothesis 1: Blocker is missing x86_64 build, not missing CMake presets

**Status:** Confirmed

**Theory:** FR9 gap is PyInstaller validation on Intel hardware only.

**Supporting indicators:** AC3 SKIP; arm64-only `Dist/`; presets exist in templates.

**Would confirm:** Successful `publish/build-dist.py` on Intel → x86_64 `Luthier.app`.

**Would refute:** Build succeeds on Intel without separate hardware (impossible per PyInstaller design).

**Resolution:** Confirmed by Story 4.1 documentation and `Build/luthier.spec` comments.

### Hypothesis 2: Python 3.14 + PySide6 6.11 unavailable on Big Sur

**Status:** Confirmed (via PyPI + pip simulation; Intel hands-on pending)

**Theory:** Big Sur cannot install current dependency stack.

**Supporting indicators:** `macosx_13_0` wheel tag on 6.11.1; pip simulation failure.

**Would confirm:** Identical `pip install` error on real Big Sur Intel Mac.

**Would refute:** PyPI publishes `macosx_11_0` wheel for 6.11 (none observed).

**Resolution:** PyPI metadata + pip platform simulation. Pending on-iron confirmation.

### Hypothesis 3: Self-hosted GitHub runner on Big Sur Intel is viable

**Status:** Refuted (moot — case closed)

**Theory:** MacBook Pro i7 Big Sur can host `actions-runner-osx-x64` for future Intel builds.

**Resolution:** Case closed before trial. Intel distribution abandoned; runner not planned.

### Hypothesis 4: Intel Luthier.app is required for product value

**Status:** Refuted

**Theory:** FR9/G5 gap blocks release or materially harms users.

**Resolution:** Maintainer decision (2026-07-09): marginal audience; **generated JUCE projects already support Mac Intel** via CMake presets. Intel `Luthier.app` is a nice-to-have, not a v1.0 requirement.

## Missing Evidence

| Gap                              | Impact                                      | Status at close                        |
| -------------------------------- | ------------------------------------------- | -------------------------------------- |
| Real Big Sur `pip install` log   | Confirm simulated error verbatim            | **Waived** — decision does not require |
| x86_64 `publish/build-dist.py`   | End-to-end Intel bundle proof               | **Waived** — out of scope              |
| Self-hosted runner trial         | CI viability                                | **Waived** — not planned               |

## Source Code Trace

| Element       | Detail                                                                 |
| ------------- | ---------------------------------------------------------------------- |
| Error origin  | N/A (distribution/infra); launch failure at Mach-O loader (wrong arch) |
| Trigger       | Double-click / `open Dist/Luthier.app` on x86_64 Mac without arm64 build |
| Condition     | Binary built with arm64 Python/PyInstaller on Apple Silicon            |
| Related files | `Build/luthier.spec`, `publish/build-dist.py`, `requirements.txt`, `requirements-dev.txt` |

## Conclusion

**Confidence:** **High** on the closure decision.

**Final decision (2026-07-09):** **Do not ship `Luthier.app` on macOS Intel.** Story 10.2 and Intel PyInstaller work are **cancelled**. v1.0 macOS distribution = **Apple Silicon (`arm64`) only**.

**Rationale (Confirmed + strategic):**

1. **Technical:** Intel launch of existing bundle fails (`Bad CPU type in executable`). Current release stack (Python 3.14 + PySide6 6.11) requires macOS 13+; maintainer Intel host is Big Sur 11 on 2014 hardware with no upgrade path.
2. **Product:** Generated projects already include `macos-debug-x86_64` / `macos-release-x86_64` presets — **JUCE Mac Intel workflow is unaffected**.
3. **Economics:** Addressable Intel-`Luthier.app` audience estimated marginal and declining; dual-bundle QA and legacy stack maintenance not justified.

**What remains in scope for macOS:**

| Artefact | Intel support |
| -------- | ------------- |
| `Luthier.app` (PyInstaller) | ❌ Apple Silicon only |
| Generated JUCE projects (CMake) | ✅ Intel presets + artefacts |
| Windows / Linux `Luthier` bundles | ✅ Unchanged (Story 4.2) |

## Recommended Next Steps

### Fix direction

**None (implementation).** No code or CI changes required for this decision.

### Documentation (optional, low effort)

1. **Release notes / README:** State `Luthier.app` requires **macOS on Apple Silicon**; generated plugin projects support Intel via CMake presets.
2. **PRD alignment (optional):** Amend FR9/G5 wording to distinguish **app distribution** (ARM macOS + Win + Linux) from **generated-project platform coverage** (includes Mac Intel).

### Diagnostic

Not applicable — investigation closed.

### Story 10.2

**Cancelled.** Revisit only on explicit user demand with measurable uptake.

## Reproduction Plan

**Setup:** MacBook Pro i7, macOS Big Sur 11.x (or upgraded 13+), clone Luthier repo.

**Trigger A — existing release artefact:**
```bash
open Dist/Luthier.app   # or CLI launch
# Expected on Intel: Bad CPU type in executable
```

**Trigger B — current stack install:**
```bash
python3.14 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
# Expected on Big Sur: PySide6 resolution failure
```

**Trigger C — successful build (Ventura+ or pinned fallback):**
```bash
source .venv/bin/activate
python publish/build-dist.py
file dist/Luthier.app/Contents/MacOS/Luthier
# Expected: x86_64, --check exit 0
```

## Side Findings

- Investigation executed on **Apple M5 arm64** (macOS 26.5.1), not the target Intel Mac — hands-on Intel evidence still required.
- `CONTRIBUTING.md` states Python 3.11+ tested on 3.14; does not document macOS minimum for PySide6 wheels.
- GitHub-hosted `macos-latest` is arm64-oriented in 2026; Intel CI on GitHub-hosted runners is being retired — self-hosted x64 is the durable Intel path.
- PyInstaller 6.21 `macosx_10_13_universal2` wheel has no macOS floor issue for Big Sur.

## Follow-up: 2026-07-09 #2

### New Evidence

- User constraint: Intel machine is **MacBook Pro mid-2014**; **Big Sur is the maximum official macOS** — Ventura+ upgrade is not available.
- Strategic question: should Luthier ship on Mac Intel at all, given Big Sur-only build host and stack divergence risk?

### Additional Findings

- **Distinction (critical):** Generated JUCE projects already ship `macos-debug-x86_64` presets — **Intel plugin development does not require an Intel Luthier.app**. FR9/G5 gap is only about **running Luthier itself** without Python on Intel Macs.
- **Codebase:** No Python 3.14-only syntax observed; CI already runs **Python 3.11**. Application logic is unlikely to require 3.14.
- **PySide6 usage:** Standard widgets, QSS, SVG, file dialogs — no APIs that obviously require 6.10+.
- **Market (indicative):** ~70–80%+ of active Mac developers on Apple Silicon in 2026; Intel Mac fleet is legacy and shrinking.

### Updated Conclusion (strategic)

For v1.0, **Intel Luthier.app is optional, not blocking**. Do not downgrade ARM64 stack. One-time Big Sur build with Python 3.12 + PySide6 6.7.3 is plausible; recurring dual-bundle QA is the real cost. Addressable Intel audience likely **small and declining** (unmeasured).

## Follow-up: 2026-07-09 #3 — Case closed

### Decision

**Intel `Luthier.app` is out of scope.** Story 10.2 cancelled. No PyInstaller x86_64 work, no self-hosted Intel runner.

### Rationale (user-confirmed)

- Marginal audience for running Luthier itself on Mac Intel
- Generated JUCE starter projects already compile for Mac Intel — sufficient value
- Avoid unnecessary complexity (dual stack, legacy PySide6 on Big Sur 2014 Mac)

### Carry-forward (backlog item #7 only)

Document in release materials: **macOS = Apple Silicon only** for the Luthier application bundle; Intel support applies to **generated projects**, not the Luthier host app.
