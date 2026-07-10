# Sprint Change Proposal — Epic 10 Story 10.2: CD Release Pipeline

**Project:** Luthier  
**Date:** 2026-07-09  
**Author:** Correct Course workflow (Batch mode — PO context pre-supplied)  
**Change signal:** Post-v1.0.0; Epic 10 Story 10.1 done; need automated GitHub Release on semver tag push  
**Source registry:** Story 10.1 (done), `publish/prepare-release.py`, `publish/build-dist.py`, `sprint-change-proposal-2026-07-09-ci-multiplatform.md`  
**Scope classification:** **Moderate** — one new story, CI workflow, publish script CI mode, CONTRIBUTING; no rollback

---

## 1. Issue Summary

### 1.1 Problem Statement

Story **10.1** automated **pytest on three OS** for push/PR to `main`. **Distribution remains manual:** Guillaume builds PyInstaller bundles locally on each OS, runs `publish/prepare-release.py pack|import|finalize|publish`, and creates GitHub releases by hand.

For **v1.0.0 public release**, Guillaume wants a **complete CD pipeline** so an agent (or human) can publish with:

```bash
# bump app/version.py, commit, then:
git tag 1.0.0-rc1 && git push origin 1.0.0-rc1   # prerelease → smoke test
git tag 1.0.0 && git push origin 1.0.0             # final release
```

Each **semver tag push** (including `-rc*` prereleases) must trigger GitHub Actions to:

1. Build PyInstaller on **`macos-latest`**, **`windows-latest`**, **`ubuntu-latest`**
2. Produce **four zips**: `Luthier-X.Y.Z-{macos,windows,linux,docs}.zip`
3. Generate **`RELEASE_NOTES.md`** and **`SHA256SUMS.txt`**
4. Publish a **GitHub Release** with assets attached (`gh release create`)
5. Mark **`-rc*`** tags as **`--prerelease`** for manual smoke test before final `1.0.0`

**Trigger constraint:** `on: push: tags:` only — **not** `workflow_dispatch` — so tag push is the single agent-friendly entry point after version bump.

**Reuse constraint:** Extend `publish/prepare-release.py` and `publish/build-dist.py`; do **not** duplicate zip/checksum logic in the workflow YAML.

**CI adaptation:** On tag push the tag **already exists** on the remote; the publish step must **not** recreate or push the tag (new `publish-ci` subcommand or equivalent).

### 1.2 Trigger Type

- **Post-sprint enhancement** — natural extension of Epic 10 after 10.1; closes the release automation gap left explicit in 10.1 out-of-scope.
- **New requirement from stakeholder** — agent-driven release via `git tag` + `git push origin <tag>`.

### 1.3 Evidence

| Source | Finding |
|--------|---------|
| `sprint-change-proposal-2026-07-09-ci-multiplatform.md` | Story 10.1 out of scope: "PyInstaller build in CI" — now in scope for 10.2 |
| `publish/prepare-release.py` L314–380 | `publish_release()` creates tag + pushes + `gh release create` — blocks when tag exists |
| `publish/build-dist.py` | Cross-platform PyInstaller build with `--check` smoke |
| `publish/templates/README-macos.template.txt` L13–14 | Still says "create, reopen, and regenerate" — obsolete since Epic 9 scaffold-only |
| `docs/qa/smoke-test-three-os.md` | Manual smoke test checklist for RC artefacts from GitHub Release |
| Epic 10 `epics.md` | Explicit "No Story 10.2" — superseded by this proposal (Intel runner still out of scope) |

---

## 2. Impact Analysis

### 2.1 Checklist Summary

| Section | Status | Notes |
|---------|--------|-------|
| 1 — Trigger & context | [x] Done | Manual release gap; agent tag-push workflow |
| 2 — Epic impact | [x] Done | Epic 10 extended with Story 10.2; 10.1 unchanged |
| 3 — Artifact conflicts | [x] Done | 10.1 out-of-scope note; README-macos template; CONTRIBUTING |
| 4 — Path forward | [x] Done | **Direct Adjustment** — Story 10.2 within Epic 10 |
| 5 — Proposal components | [x] Done | This document + epics.md + sprint-status.yaml |
| 6 — Final review | [!] Action-needed | **Awaiting PO approval** |

### 2.2 Epic Impact

| Epic | Status | Impact |
|------|--------|--------|
| Epics 1–9 | **done** | No rollback |
| Epic 10 — Story 10.1 | **done** | Unchanged |
| **Epic 10 — Story 10.2** | **new — backlog** | CD release pipeline on tag push |
| ~~Epic 10.2 Intel macOS~~ | **still cancelled** | Investigation closed; not revived |

**Epic 10 status:** `done` → **`in-progress`** until 10.2 completes.

### 2.3 PRD / MVP Impact

**MVP features unchanged.** This adds **release automation** — a distribution/ops capability reinforcing **FR9** and **G5**.

| Requirement | Impact |
|-------------|--------|
| **FR9** | Reinforced — automated multi-OS bundle build + GitHub Release |
| **G5** | Reinforced — macOS ARM64 (`macos-latest`), Windows, Linux artefacts per release |
| **NF4** | CONTRIBUTING gains tag-based release procedure |
| **§9 Out of scope** | Signing/notarization, `.msi`/`.pkg`, Mac Intel app — **remain out of scope** |

### 2.4 Architecture Impact

| Area | Impact |
|------|--------|
| **CI/CD** | New `.github/workflows/release.yml` — tag-triggered build matrix + publish job |
| **publish/** | `publish-ci` mode: skip tag create/push; `gh release create` only |
| **AD-6 / tests** | Optional: workflow validation tests or documented dry-run; no core invariant change |
| **architecture-spine** | No change required |

### 2.5 UI/UX Impact

**[N/A]** — infrastructure and release docs only. **README-macos.template.txt** copy fix aligns with Epic 9 scaffold-only positioning (user-facing release readme, not app UI).

### 2.6 Technical Impact

| Artifact | Story | Change |
|----------|-------|--------|
| `.github/workflows/release.yml` | 10.2 | Tag push → build matrix → artifact upload → finalize → `gh release create` |
| `publish/prepare-release.py` | 10.2 | `publish-ci` subcommand (no tag create/push; prerelease auto from `-rc` in tag) |
| `publish/templates/README-macos.template.txt` | 10.2 | Remove reopen/regenerate; scaffold-only wording |
| `CONTRIBUTING.md` | 10.2 | RC tag + final release procedure |
| `epics.md` | CC | Story 10.2; remove "No Story 10.2" |
| `sprint-status.yaml` | CC | `epic-10: in-progress`; `10-2-cd-release-pipeline: backlog` |

**Risk:** Medium — PyInstaller in CI is slower and env-sensitive; mitigated by reusing `build-dist.py` and existing pack/finalize paths.  
**Effort:** Medium — ~1–2 dev sessions (workflow + publish-ci + docs + validation).  
**Timeline:** Blocks agent-driven `1.0.0-rc1` publish; recommended before public announcement.

---

## 3. Recommended Approach

**Selected: Option 1 — Direct Adjustment**

Add **Story 10.2** to existing **Epic 10**. Reuse `publish/` scripts; add CI-specific publish path. No rollback of 10.1.

**Rejected:**

| Option | Reason |
|--------|--------|
| Rollback 10.1 | Unrelated; pytest matrix stays |
| New Epic 11 | CD is natural Epic 10 continuation |
| MVP Review | No feature scope reduction — automation only |
| Duplicate zip logic in YAML | Violates reuse constraint; maintenance burden |

---

## 4. Detailed Change Proposals

### 4.1 Epic 10 header — `epics.md`

**OLD (Epic List note):**
> **Note:** Mac Intel `Luthier.app` explicitly out of scope per `investigations/macos-x86_64-intel-build-investigation.md`. No Story 10.2.

**NEW:**
> **Note:** Mac Intel `Luthier.app` explicitly out of scope per `investigations/macos-x86_64-intel-build-investigation.md`. Story 10.2 = CD release pipeline (not Intel runner).

---

### 4.2 Story 10.2 — Acceptance Criteria (authoritative)

See `epics.md` § Epic 10 and story file `10-2-cd-release-pipeline.md` (to be created via `[CS] Create Story`).

Summary:

1. **Trigger:** `on: push: tags:` matching semver (`*.*.*`, including `-rc*`). **No** `workflow_dispatch`.
2. **Permissions:** `contents: write` for `GITHUB_TOKEN` (release + assets).
3. **Build matrix:** `macos-latest`, `windows-latest`, `ubuntu-latest` — each runs `publish/build-dist.py` then `publish/prepare-release.py pack`.
4. **Publish job:** downloads three platform zips → `finalize` (docs zip, `RELEASE_NOTES.md`, `SHA256SUMS.txt`) → `publish-ci` (`gh release create` with assets; **no** tag create/push).
5. **Prerelease:** tag matching `*-rc*` → `gh release create --prerelease`.
6. **Version:** tag name = version (no `v` prefix); must match `app/version.py` at tagged commit.
7. **Reuse:** no duplicated archive/checksum logic in workflow YAML.
8. **Template fix:** `README-macos.template.txt` — scaffold-only copy (no reopen).
9. **CONTRIBUTING.md:** document RC smoke test (`docs/qa/smoke-test-three-os.md`) then final tag.
10. **Out of scope:** Mac Intel app, code signing/notarization, `.msi`/`.pkg` installers.

---

### 4.3 `sprint-status.yaml`

**CHANGE:**

```yaml
  epic-10: in-progress   # was: done
  10-1-ci-multi-platform-pytest-matrix: done
  10-2-cd-release-pipeline: backlog   # NEW
```

---

## 5. Implementation Handoff

### 5.1 Scope classification

**Moderate** — Developer agent implements 10.2; PO validates first RC release manually.

### 5.2 Handoff recipients

| Role | Responsibility |
|------|----------------|
| **`bmad-create-story`** | Create `10-2-cd-release-pipeline.md` from epics ACs |
| **Developer (`bmad-dev-story`)** | Workflow, publish-ci, template fix, CONTRIBUTING, validation |
| **PO (Guillaume)** | Approve proposal; run smoke test on `1.0.0-rc1` GitHub Release |

### 5.3 Success criteria

- [ ] Push tag `X.Y.Z-rcN` creates prerelease with 4 zips + checksums + notes
- [ ] Push tag `X.Y.Z` creates final release with same asset set
- [ ] Agent can release via version bump + `git tag` + `git push origin <tag>` only
- [ ] `README-macos` archive text matches scaffold-only Epic 9
- [ ] CONTRIBUTING documents RC → smoke → final flow

### 5.4 Recommended sequence

```
PO approve proposal → bmad-create-story 10.2 → bmad-dev-story 10.2 → tag 1.0.0-rc1 → manual smoke → tag 1.0.0
```

---

## 6. Approval

**Status:** **Approved** by Guillaume — 2026-07-09

**Conditions:** None. Implementation via Story 10.2; `[CS] Create Story` → `[DS] Dev Story`.

---

*Correct Course workflow — Luthier — 2026-07-09 — **FINALIZED***
