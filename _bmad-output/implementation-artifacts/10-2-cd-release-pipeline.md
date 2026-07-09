---
epic: 10
story: 2
story_key: 10-2-cd-release-pipeline
depends_on: [10-1, 4-1, 4-2, 4-4]
blocks: []
implementation_order: 2
correct_course_date: 2026-07-09
baseline_commit: 03cf06bdf8f89dc18db40218a9d70dd7478d2d72
baseline_workflow: .github/workflows/release.yml
---

# Story 10.2: CD Release Pipeline (GitHub Actions)

Status: done

<!-- Epic 10 — CI & Release Scope. Automated GitHub Release on semver tag push. Priority: MUST (pre-public v1.0.0). -->

## Story

As a maintainer,
I want pushing a semver git tag to trigger a full multi-OS build and GitHub Release,
So that I (or an agent) can publish `1.0.0-rc1` for smoke testing and `1.0.0` for the final release without manual per-OS builds or duplicate packaging logic.

## Context

**Correct Course 2026-07-09 (approved):** Story **10.1** delivers pytest on three OS for push/PR. Distribution is still manual via `publish/build-dist.py` + `publish/prepare-release.py` on each machine.

**Target workflow:** bump `app/version.py` → commit → `git tag <version>` → `git push origin <tag>` → CI builds, packages, and publishes GitHub Release.

**Reuse:** `publish/build-dist.py` (PyInstaller + `--check`), `prepare-release.py` subcommands `pack`, `finalize`, `verify`. **Do not** duplicate zip/checksum logic in YAML.

**CI adaptation:** Tag already exists when workflow runs — add **`publish-ci`** subcommand: `gh release create` only (no tag create/push, no clean-tree check).

**Prerelease:** version with prerelease suffix (`1.0.0-rc1`, `1.0.1-beta2`) → `--prerelease`. Stable `1.0.0` → normal release.

**Planning references:**
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-09-cd-release.md`
- `publish/prepare-release.py` — `publish_release()` L314–380 (local flow; CI differs)
- `docs/tests/1.0.0-pre-release/smoke-test-v1-trois-os.md` — manual RC validation

## Acceptance Criteria

### AC1 — Tag trigger only

**Given** a semver tag push (e.g. `1.0.0`, `1.0.0-rc1`)  
**When** GitHub Actions runs  
**Then** `.github/workflows/release.yml` triggers on `push: tags:` only — **not** `workflow_dispatch`

### AC2 — Build matrix

**Given** the release workflow  
**When** build jobs run  
**Then** PyInstaller executes on `macos-latest`, `windows-latest`, `ubuntu-latest` via `publish/build-dist.py`  
**And** each leg runs `publish/prepare-release.py pack --version <tag>`

### AC3 — Publish job

**Given** all three build jobs succeed  
**When** the publish job runs  
**Then** it runs `finalize` (docs zip, `RELEASE_NOTES.md`, `SHA256SUMS.txt`) and `publish-ci` with four zips + checksums attached to GitHub Release

### AC4 — publish-ci (no tag recreation)

**Given** the tag already exists on the remote  
**When** `publish-ci` runs  
**Then** it does **not** create or push a git tag  
**And** it invokes `gh release create` with assets

### AC5 — Prerelease detection

**Given** tag `1.0.0-rc1` (or any `X.Y.Z-<suffix>`)  
**When** GitHub Release is created  
**Then** it is marked `--prerelease`  
**Given** tag `1.0.0`  
**Then** stable (non-prerelease) release

### AC6 — Permissions and version

**Given** the workflow  
**Then** `permissions: contents: write` for `GITHUB_TOKEN`  
**And** tag name (no `v` prefix) matches `app/version.py` `VERSION` at tagged commit

### AC7 — README-macos template

**Given** `publish/templates/README-macos.template.txt`  
**Then** text reflects scaffold-only positioning — no "reopen" wording (Epic 9)

### AC8 — CONTRIBUTING.md

**Given** `CONTRIBUTING.md`  
**Then** documents RC tag → smoke test → final tag release procedure

### AC9 — Tests / validation

**Given** story completion  
**Then** unit tests cover prerelease detection and `publish-ci` behaviour (no tag creation)  
**And** release workflow YAML is validated in tests

## Tasks / Subtasks

- [x] Add `publish-ci` to `publish/prepare-release.py` (AC: 3, 4, 5)
  - [x] Extract shared `gh release create` helper from `publish_release`
  - [x] Add `is_prerelease_version()` — `X.Y.Z-<suffix>` → prerelease
  - [x] `publish-ci`: verify + `gh release create`; skip git clean/tag checks
  - [x] Wire subcommand with `--yes` and optional `--prerelease` override

- [x] Create `.github/workflows/release.yml` (AC: 1, 2, 3, 6)
  - [x] `on.push.tags` semver pattern; `permissions: contents: write`
  - [x] `validate-tag` job: semver regex + match `app/version.py`
  - [x] Matrix build: venv, Qt deps (Linux), `build-dist.py`, `pack --version`
  - [x] Upload per-platform zip artifact
  - [x] Publish job: download artifacts → `finalize` → `publish-ci --yes`
  - [x] `timeout-minutes` generous for PyInstaller legs

- [x] Fix `publish/templates/README-macos.template.txt` (AC: 7)
  - [x] EN + FR: scaffold-only copy (create new projects; no reopen/regenerate)

- [x] Update `CONTRIBUTING.md` (AC: 8)
  - [x] Section: version bump, tag RC, smoke test doc link, final tag

- [x] Tests (AC: 9)
  - [x] `tests/unit/test_prepare_release.py` — prerelease detection, publish-ci command assembly
  - [x] Workflow structure test (yaml parse, required jobs/steps)

- [x] Regression
  - [x] `pytest` green locally (320 passed, 3 skipped)

### Review Findings

- [x] [Review][Decision] Prerelease detection scope — resolved: keep `X.Y.Z-<suffix>` (AC5); `epics.md` aligned
- [x] [Review][Decision] `cancel-in-progress: true` — resolved: set `false` in `release.yml`
- [x] [Review][Decision] Smoke test doc vs RC release flow — resolved: Option R (GitHub Release) added; version = tag testé
- [x] [Review][Patch] `gh release create` not idempotent on workflow re-run [publish/prepare-release.py:319-345]
- [x] [Review][Patch] VERSION extraction has no empty-guard when grep misses [release.yml:30-33]
- [x] [Review][Patch] Publish job copies artifacts without preflight existence check [release.yml:94-99]
- [x] [Review][Patch] Workflow tests are substring-only; no YAML parse [tests/unit/test_prepare_release.py]
- [ ] [Review][Patch] Tag filter `*.*.*` is broader than semver; workflow starts before validate-tag [release.yml:12] — left open per review triage
- [x] [Review][Defer] No end-to-end workflow run in change set [release.yml] — deferred, expected: AC1 forbids `workflow_dispatch`; first validation is real tag push
- [x] [Review][Defer] Artifact retention 7 days [release.yml:71] — deferred, post-MVP: extend if publish failures need manual recovery

## Dev Notes

### Artifact flow in CI

1. Each matrix leg: `_local/releases/<version>/Luthier-<version>-<platform>.zip`
2. `actions/upload-artifact` per platform
3. Publish job: `download-artifact` → copy into `_local/releases/<version>/`
4. `finalize` adds docs + notes + checksums
5. `publish-ci` uploads to GitHub

### Out of scope

- Mac Intel app; signing/notarization; `.msi`/`.pkg`
- `workflow_dispatch`
- Duplicating zip/checksum logic in YAML

## Dev Agent Record

### Agent Model Used

Composer (Cursor)

### Debug Log References

- `importlib` dynamic load of `prepare-release.py` required `sys.modules` registration for dataclasses on Python 3.14.

### Completion Notes List

- ✅ AC1–9: `release.yml` on tag push only; 3-OS build + pack; publish job finalize + `publish-ci`; `contents: write`; version/tag validation; README-macos scaffold-only; CONTRIBUTING release section; unit + workflow structure tests.
- ✅ `publish-ci` auto-detects prerelease from `X.Y.Z-<suffix>`; `--prerelease` / `--stable` overrides available.
- ✅ Local regression: 320 passed, 3 skipped.

### File List

- `.github/workflows/release.yml` (added)
- `publish/prepare-release.py` (modified)
- `publish/templates/README-macos.template.txt` (modified)
- `CONTRIBUTING.md` (modified)
- `tests/unit/test_prepare_release.py` (added)
- `_bmad-output/implementation-artifacts/10-2-cd-release-pipeline.md` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

## Change Log

- 2026-07-09: Story created via Correct Course — CD release pipeline on semver tag push.
- 2026-07-09: Story 10.2 implemented — release workflow, publish-ci, docs, tests.
