---
baseline_commit: c497802d5fee4ae8a23e65079655cf05574e95d9
---

# Story 7.1: GitHub Actions CI for pytest

Status: in-progress

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

- [ ] Add `.github/workflows/pytest.yml` (AC: 1–4)
  - [ ] Trigger on `push` and `pull_request` to default branch
  - [ ] Setup Python 3.11+ (match CONTRIBUTING minimum)
  - [ ] `pip install -r requirements-dev.txt` then `pytest`
  - [ ] No CMake/JUCE/PyInstaller build steps required

- [ ] Verify skip behaviour in CI (AC: 3)
  - [ ] Confirm `tests/integration/test_cmake_cross_platform.py` skips without cmake/JUCE
  - [ ] Confirm `tests/integration/test_frozen_bundle.py` skips without dist bundle

- [ ] Update `CONTRIBUTING.md` (AC: 5)
  - [ ] Note CI runs on PRs; optional status badge

- [ ] Regression
  - [ ] Local `.venv/bin/pytest` still green
  - [ ] Push branch and confirm workflow green

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
