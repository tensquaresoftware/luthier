# Sprint Change Proposal — Epic 10: Multi-Platform CI & macOS Distribution Scope

**Project:** Luthier  
**Date:** 2026-07-09  
**Author:** Correct Course workflow (Batch mode — PO context pre-supplied)  
**Change signal:** Post-v1.0.0 (Epics 1–9 done); extend CI beyond ubuntu-only; close Mac Intel distribution investigation  
**Source registry:** Story 7.1 (done), `deferred-work.md`, `investigations/macos-x86_64-intel-build-investigation.md`  
**Scope classification:** **Minor** — one new epic, one story, PRD/epics doc amendments; no rollback

---

## 1. Issue Summary

### 1.1 Problem Statement

Story **7.1** delivered GitHub Actions pytest CI on **`ubuntu-latest` only**. That catches most regressions but does **not** replace the manual cross-platform verification Guillaume ran after each change on **macOS**, **Windows**, and **Linux** — especially for:

- Path normalization and platform-specific logic in `core/` and tests
- PySide6 import/runtime behaviour per OS (Qt offscreen)
- Platform-gated integration tests in `test_cmake_cross_platform.py` (Windows/Linux configure tests run only on matching hosts)

Meanwhile, investigation **macos-x86_64-intel-build-investigation** (step 0) concluded that **Luthier.app on Mac Intel (x86_64) is out of scope**: existing bundle is ARM64-only; PySide6 6.11 requires macOS 13+; target Big Sur i7 hardware cannot host the current stack; dual-arch PyInstaller QA is not justified for v1.0+.

**Product decisions (closed):**

| Decision | Outcome |
|----------|---------|
| Mac Intel `Luthier.app` | **Abandoned** — not planned for v1.0+ |
| Story 10.2 / self-hosted Intel runner | **Not planned** |
| macOS distribution | **ARM64 (Apple Silicon) only** — Story 4.1 build validated |
| Generated JUCE projects | **Unchanged** — CMake presets still include `macos-*-x86_64` for plugin targets |
| CI macOS runner | **`macos-latest`** (GitHub **Apple Silicon** runners) — sufficient for retained scope |

### 1.2 Trigger Type

- **Post-sprint enhancement** — deliberate extension of Epic 7 CI deliverable, not a failed approach.
- **Scope clarification** — FR9/G5 narrowed for *Luthier application* distribution; generated-project portability (NFR3/FR3) unchanged.

### 1.3 Evidence

| Source | Finding |
|--------|---------|
| `.github/workflows/pytest.yml` | Single job on `ubuntu-latest`; Python 3.11, venv, Qt apt deps, `QT_QPA_PLATFORM=offscreen` |
| `7-1-github-actions-ci-for-pytest.md` | Status **done**; explicitly out of scope: cross-platform cmake in CI, PyInstaller in CI |
| `tests/integration/test_cmake_cross_platform.py` | Platform `@pytest.mark.skipif` — Windows/Linux configure tests need matching CI host |
| `tests/integration/test_frozen_bundle.py` | Skips when `dist/` bundle absent — CI-safe |
| `Dist/Luthier.app` | ARM64 Mach-O only (`investigations/macos-x86_64-intel-build-investigation.md`) |
| `publish/templates/README-macos.template.txt`, `RELEASE_NOTES.template.md` | Already state Apple Silicon only for app (2026-07-09) |
| `deferred-work.md` | pip/apt cache, retry apt — post-MVP triggers only; not blocking 10.1 |
| Manual QA habit | Guillaume re-ran pytest logic on three OS families after changes pre-CI |

---

## 2. Impact Analysis

### 2.1 Checklist Summary

| Section | Status | Notes |
|---------|--------|-------|
| 1 — Trigger & context | [x] Done | 7.1 ubuntu-only gap; Intel investigation closed |
| 2 — Epic impact | [x] Done | New **Epic 10**; Epics 1–9 remain **done**; no 10.2 |
| 3 — Artifact conflicts | [x] Done | PRD FR9/G5 vs actual release; epics.md FR9 + Story 4.1 AC3; CONTRIBUTING CI section |
| 4 — Path forward | [x] Done | **Direct Adjustment** — Epic 10 / Story 10.1; Rollback rejected; MVP Review rejected |
| 5 — Proposal components | [x] Done | This document + story `10-1-ci-multi-platform-pytest-matrix.md` |
| 6 — Final review | [!] Action-needed | **Awaiting PO approval** |

### 2.2 Epic Impact

| Epic | Status | Impact |
|------|--------|--------|
| Epics 1–9 | **done** | No code rollback; 10.1 extends 7.1 workflow only |
| **Epic 10 — CI & Release Scope** | **new — backlog** | Story 10.1: multi-OS pytest matrix |
| ~~Epic 10.2 Intel macOS~~ | **cancelled** | Investigation closed; not in backlog |

### 2.3 PRD / MVP Impact

**MVP (v1.0.0) already shipped** with Epics 1–9. This change **clarifies release scope** and **automates post-release regression checks** — it does not reopen scaffold-only or generation features.

| Requirement | Current PRD text | Proposed change |
|-------------|------------------|-----------------|
| **FR9** (F9) | macOS ARM64 **and** x86_64 for Luthier app | **Luthier app:** macOS ARM64, Windows x64, Linux x86_64 only. **Generated projects:** all 10 CMake presets unchanged (including macOS x86_64 for JUCE targets). |
| **G5** | macOS (Intel & ARM) | **G5:** macOS Apple Silicon, Windows, Linux — *Luthier application* distribution |
| **NF2** | Integration tests on all 3 platforms or OS-mocked CI | **NF2 addendum:** CI matrix runs pytest on `ubuntu-latest`, `windows-latest`, `macos-latest`; optional-env tests skip per AD-6 |
| **§9 Out of scope** | CI/CD listed post-MVP | **Addendum:** multi-OS pytest matrix in scope (Story 10.1); PyInstaller/CMake-in-CI remain out of scope |

**No MVP scope reduction** for user-facing generation features. **Distribution matrix narrowed** to match shipped artefacts and investigation conclusion.

### 2.4 Architecture Impact

| Area | Impact |
|------|--------|
| **AD-6** | Unchanged — no Qt widget tests; CI runs existing unit + integration tiers |
| **NFR3 / FR3** | Unchanged — generated project portability; preset JSON tests run on all matrix legs |
| **CI/CD** | `.github/workflows/pytest.yml` gains `strategy.matrix` — primary technical change in 10.1 |
| **Release docs** | PRD/epics alignment; publish templates already correct |

No architecture-spine invariant changes required.

### 2.5 UI/UX Impact

**[N/A]** — infrastructure-only story.

### 2.6 Technical Impact

| Artifact | Story | Change |
|----------|-------|--------|
| `.github/workflows/pytest.yml` | 10.1 | Matrix: `ubuntu-latest`, `windows-latest`, `macos-latest` |
| `CONTRIBUTING.md` | 10.1 | Document multi-OS CI, per-OS Qt notes, Apple Silicon runner note |
| `epics.md` | CC | Epic 10 + FR9 scope note; Story 4.1 AC3 marked out of scope |
| `sprint-status.yaml` | CC | Epic 10 backlog + story 10.1 |
| `prd.md` | CC (proposed) | FR9, G5, NF2 addendum |
| `deferred-work.md` | Optional | Move “multi-OS CI” from implicit gap to resolved when 10.1 done |

**Risk:** Low — pytest suite already green on three OS families locally; matrix exposes platform-specific env setup only.  
**Effort:** Low — ~1 dev session.  
**Timeline:** No release blocker; recommended before next feature epic.

---

## 3. Recommended Approach

**Selected: Option 1 — Direct Adjustment**

Add **Epic 10** with a single story **10.1** extending the existing pytest workflow to a three-OS matrix. No rollback of 7.1. No PRD MVP reduction beyond **documenting** the already-shipped ARM64-only macOS app.

**Rejected:**

| Option | Reason |
|--------|--------|
| Rollback 7.1 | Workflow is sound; only runner scope is insufficient |
| MVP Review / defer CI | PO wants automation now; manual tri-OS runs are the pain point |
| Story 10.2 Intel build | Investigation closed — audience and stack constraints |

---

## 4. Detailed Change Proposals

### 4.1 Epic 10 (new) — `epics.md`

**Section:** Epic List (after Epic 9)

**NEW:**

```markdown
### Epic 10: CI & Release Scope
Automated pytest on Linux, Windows, and macOS (GitHub-hosted runners); PRD/release alignment for ARM64-only macOS app distribution.

**FRs covered:** — (reinforces NFR2; clarifies FR9 release scope)
**Priority:** Post-v1.0.0 (2026-07-09 correct-course)
**Note:** Mac Intel Luthier.app explicitly out of scope per investigation 2026-07-09. No Story 10.2.
```

**Story 10.1** — full text in §4.3 and story file `10-1-ci-multi-platform-pytest-matrix.md`.

---

### 4.2 PRD — `prd-Luthier-2026-06-22/prd.md`

**Section: G5 (§2 Goals)**

**OLD:**
> **G5** — Luthier itself is distributed as a native desktop application on macOS (Intel & ARM), Windows, and Linux.

**NEW:**
> **G5** — Luthier itself is distributed as a native desktop application on macOS (Apple Silicon), Windows, and Linux. Generated JUCE projects remain buildable for Mac Intel via CMake presets; the standalone Luthier app does not run on Intel Macs.

---

**Section: F9 — Luthier Application Portability (§5)**

**OLD:**
> - macOS ARM64 (Apple Silicon)
> - macOS x86_64 (Intel)
> - Windows x64
> - Linux x86_64
> - Full feature parity across all supported platforms.

**NEW:**
> - macOS ARM64 (Apple Silicon) — **Luthier.app distribution target**
> - Windows x64
> - Linux x86_64
> - Full feature parity across these three **application** platforms.
> - **Out of scope for Luthier.app:** macOS x86_64 (Intel). Users on Intel Macs build generated projects with CMake/Xcode; they do not run the PyInstaller bundle.

---

**Section: NF2 — Tests (§6)**

**ADD** after integration-tests bullet:
> - **CI matrix (Story 10.1):** pytest runs on GitHub Actions for `ubuntu-latest`, `windows-latest`, and `macos-latest`. The macOS runner is Apple Silicon (`macos-latest` as of 2026), which matches the Luthier.app distribution target. Tests requiring CMake, JUCE, or a built PyInstaller bundle skip cleanly.

---

### 4.3 Epics — FR9 inventory line

**OLD (Requirements Inventory):**
> FR9: Luthier is distributable as a self-contained bundle (PyInstaller, no system Python) on macOS ARM64, macOS x86_64, Windows x64, and Linux x86_64, with full feature parity across platforms.

**NEW:**
> FR9: Luthier is distributable as a self-contained bundle (PyInstaller, no system Python) on **macOS ARM64 (Apple Silicon)**, Windows x64, and Linux x86_64, with full feature parity across those platforms. **Mac Intel is not a Luthier.app target** (investigation 2026-07-09); generated projects retain x86_64 CMake presets.

---

### 4.4 Epics — Story 4.1 AC3

**OLD:**
> **Given** `Luthier.app` on macOS x86_64 (Intel or Rosetta), **When** it is launched, **Then** all features work identically to the ARM64 build.

**NEW:**
> ~~AC3 macOS x86_64~~ — **OUT OF SCOPE (2026-07-09).** Luthier.app ships ARM64 only. Rosetta execution of the ARM64 bundle is not a distribution substitute. See `investigations/macos-x86_64-intel-build-investigation.md`.

---

### 4.5 Story 10.1 — Acceptance Criteria (authoritative)

See `_bmad-output/implementation-artifacts/10-1-ci-multi-platform-pytest-matrix.md` for full dev context.

Summary:

1. Workflow triggers on **push** and **pull_request** to **`main`**.
2. **Matrix** over `ubuntu-latest`, `windows-latest`, `macos-latest` (Python 3.11, venv, `requirements-dev.txt`, `pytest`).
3. **Qt runtime** installed or configured per OS (`QT_QPA_PLATFORM=offscreen` on all legs; Linux retains apt Qt libs from 7.1).
4. **`macos-latest` = GitHub Apple Silicon** — documented in workflow comment, CONTRIBUTING, and story Dev Notes; sufficient for ARM64 app scope.
5. Tests needing **CMake/JUCE** or **PyInstaller `dist/`** skip cleanly — matrix job still passes.
6. Any failing test → workflow **exit non-zero**; PR check red.
7. **`CONTRIBUTING.md`** updated for multi-OS CI; status badge remains valid (same workflow file).
8. **Out of scope:** PyInstaller build in CI, macOS x86_64 runner, Intel/Big Sur, self-hosted runner.

---

### 4.6 `sprint-status.yaml`

**ADD:**

```yaml
  # Epic 10: CI & Release Scope
  # (Correct Course 2026-07-09 — multi-OS pytest matrix; ARM64-only macOS app scope)
  epic-10: backlog
  10-1-ci-multi-platform-pytest-matrix: backlog
  epic-10-retrospective: optional
```

---

## 5. Implementation Handoff

### 5.1 Scope classification

**Minor** — Developer agent can implement Story 10.1 directly after PO approval.

### 5.2 Handoff recipients

| Role | Responsibility |
|------|----------------|
| **Developer (`bmad-dev-story`)** | Implement 10.1: workflow matrix, CONTRIBUTING, verify green on all three OS legs |
| **PO (Guillaume)** | Approve this proposal; optional PRD edit merge |
| **Tech writer** | Optional — PRD § amendments if not applied in same PR as 10.1 |

### 5.3 Success criteria

- [ ] PR to `main` shows pytest workflow green on **ubuntu**, **windows**, **macos** legs
- [ ] Same test count semantics as 7.1 (optional-env tests skipped, not failed)
- [ ] CONTRIBUTING documents multi-OS CI and Apple Silicon runner note
- [ ] `epics.md` and `sprint-status.yaml` reflect Epic 10
- [ ] No references to Story 10.2 or Intel CI in backlog

### 5.4 Recommended sequence

```
PO approve proposal → bmad-dev-story 10.1 → merge → mark 10.1 done in sprint-status
```

Optional follow-up (separate quick-dev): apply PRD FR9/G5 edits if not bundled in 10.1 PR.

---

## 6. Approval

**Status:** **Approved** by Guillaume — 2026-07-09

**Conditions:** None. Implementation via Story 10.1 only; no Story 10.2; YAML not in Correct Course session.

---

*Correct Course workflow — Luthier — 2026-07-09 — **FINALIZED***
