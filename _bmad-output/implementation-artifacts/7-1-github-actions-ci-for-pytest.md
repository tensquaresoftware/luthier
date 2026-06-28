---
baseline_commit: cbc07a401495c47b9b4eeff430b8da114daaaed7
---

# Story 7.1: GitHub Actions CI for pytest

Status: done

<!-- Epic 7 — Release Hardening. Priority: MUST. Order: first. -->

## Story

As a contributor,
I want pytest to run automatically on every push and pull request,
So that regressions in unit and integration tests are caught before merge without relying on local runs only.

## Acceptance Criteria

1. **Given** a push or pull request to the default branch, **when** GitHub Actions runs, **then** a workflow installs Python, creates a venv, installs `requirements-dev.txt`, and runs `pytest`.
2. **Given** the CI runner (`ubuntu-latest`), **when** pytest executes, **then** all tests under `tests/unit/` and `tests/integration/` are collected and run.
3. **Given** tests requiring unavailable tooling, **when** CI runs without CMake, JUCE, or a built PyInstaller bundle, **then** those tests skip cleanly — CI does **not** fail.
4. **Given** a failing test, **when** CI completes, **then** the workflow exits non-zero and the PR check shows failure.
5. **Given** `CONTRIBUTING.md`, **when** Epic 7.1 is complete, **then** it documents that CI runs on PRs.

## Tasks / Subtasks

- [x] Add `.github/workflows/pytest.yml` (AC: 1–4)
  - [x] Trigger on `push` and `pull_request` to default branch
  - [x] Setup Python 3.11+ (match CONTRIBUTING minimum)
  - [x] `pip install -r requirements-dev.txt` then `pytest`
  - [x] No CMake/JUCE/PyInstaller build steps required

- [x] Verify skip behaviour in CI (AC: 3)
  - [x] Confirm `tests/integration/test_cmake_cross_platform.py` skips without cmake/JUCE
  - [x] Confirm `tests/integration/test_frozen_bundle.py` skips without dist bundle

- [x] Update `CONTRIBUTING.md` (AC: 5)
  - [x] Note CI runs on PRs; optional status badge

- [x] Regression
  - [x] Local `.venv/bin/pytest` still green
  - [x] Push branch and confirm workflow green

## Dev Notes

### Source

- `_bmad-output/implementation-artifacts/deferred-work.md` — Infrastructure / CI
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-06-28.md` § Story 7.1

### Existing test layout

| Path | CI expectation |
|------|----------------|
| `tests/unit/` | Always run |
| `tests/integration/` | Run; cmake/bundle tests self-skip |
| `tests/test_story_*.py` | Still collected until Story 7.4 |

### Out of scope

- Cross-platform cmake configure in CI (requires JUCE install)
- PyInstaller build in CI
- Qt widget tests (AD-6)

### References

- `pytest.ini` — testpaths, pythonpath
- `CONTRIBUTING.md` — quick start, ~156+ tests, ~18s local run

## Dev Agent Record

### Implementation Plan

- Added `.github/workflows/pytest.yml` on `ubuntu-latest`: Python 3.11, venv, `requirements-dev.txt`, `pytest`.
- Installed Qt runtime libs (`libegl1`, `libgl1`, …) and `QT_QPA_PLATFORM=offscreen` so headless Linux CI can import PySide6-backed `app/` tests.
- Updated `CONTRIBUTING.md` CI section with workflow description and status badge.
- Aligned integration test fixtures with `normalize_portable_path` canonical forward-slash Windows paths so round-trip assertions stay green (202 passed, 2 skipped locally).

### Debug Log

- Initial HEAD commit had workflow without venv; AC1 requires venv — consolidated into single step with `.venv/bin/pip` and `.venv/bin/pytest`.
- 12 round-trip failures traced to `C:\` vs `C:/` mismatch after path normalization; fixed test expectations in conftest and legacy story tests.

### Completion Notes

- ✅ AC1–5 satisfied: workflow triggers on push/PR to `main`, runs full pytest suite, optional-env tests skip, CONTRIBUTING documents CI.
- Local regression: `python3 -m pytest` → 202 passed, 2 skipped (~21s).
- CMake cross-platform: platform-specific configure tests skip on non-matching OS; JSON/preset tests run without cmake/JUCE.
- Frozen bundle tests skip when `dist/` absent (verified skip markers).
- Branch `story/7-1-github-actions-ci` pushed; PR #1 workflow run [28324004094](https://github.com/tensquaresoftware/luthier/actions/runs/28324004094) green on `ubuntu-latest`.

## File List

- `.github/workflows/pytest.yml` (modified)
- `CONTRIBUTING.md` (modified)
- `tests/conftest.py` (modified)
- `tests/integration/test_round_trip.py` (modified)
- `tests/test_story_2_1.py` (modified)
- `tests/test_story_2_2.py` (modified)
- `_bmad-output/implementation-artifacts/7-1-github-actions-ci-for-pytest.md` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

## Change Log

- 2026-06-28: Story 7.1 — GitHub Actions pytest CI on ubuntu-latest (Qt headless deps); CONTRIBUTING CI section; test fixture path normalization alignment.

### Review Findings

- [x] [Review][Patch] CONTRIBUTING omits Linux Qt system deps and offscreen env [`CONTRIBUTING.md:175`]
- [x] [Review][Patch] apt-get step lacks noninteractive and no-recommends flags [`.github/workflows/pytest.yml:22`]
- [x] [Review][Defer] No pip or apt caching in CI workflow [`.github/workflows/pytest.yml`] — deferred, pre-existing optimization gap
- [x] [Review][Defer] apt-get update has no retry on transient network failures [`.github/workflows/pytest.yml:22`] — deferred, flaky-CI hardening
- [x] [Review][Defer] Test helpers still allow backslash Windows path overrides via kwargs [`tests/conftest.py:42`] — deferred, pre-existing
