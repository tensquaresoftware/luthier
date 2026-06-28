# Story 7.2: Atomic JSON Persistence & Corrupt-File Feedback

Status: backlog

<!-- Epic 7 — Release Hardening. Priority: SHOULD. Order: second. Depends on 7.1 recommended. -->

## Story

As a JUCE developer,
I want my preferences and app state saved safely and reported clearly when a config file is corrupt,
So that a crash during save never leaves me with a broken profile and I know when defaults were restored.

## Acceptance Criteria

1. **Given** `Preferences.save()` or `AppState.save()` is called, **when** the file is written, **then** content is written to a sibling temp file and atomically replaced (same pattern as `ProjectWriter` AD-4).
2. **Given** a corrupt or truncated `preferences.json` on startup, **when** Luthier loads preferences, **then** in-memory state falls back to factory defaults **and** a user-visible message explains that the file was reset.
3. **Given** a corrupt `app_state.json`, **when** Luthier loads app state, **then** defaults apply and the user is notified similarly.
4. **Given** unit tests with `tmp_path`, **when** a simulated crash occurs after temp write but before rename, **then** the original JSON file content is unchanged.
5. **Given** Epic 7.2 completion, **when** architecture docs are inspected, **then** AD-10 documents atomic JSON persistence.

**Deferred:** schema `version` field for migrations.

## Tasks / Subtasks

- [ ] Extract or reuse atomic write helper (AC: 1, 4)
  - [ ] Pattern from `core/project_writer.py` — temp sibling + `replace()`
  - [ ] Apply in `core/preferences.py` `save()`
  - [ ] Apply in `core/app_state.py` `save()`

- [ ] Corrupt-load detection + feedback (AC: 2, 3)
  - [ ] On `JSONDecodeError` or invalid structure: reset to defaults
  - [ ] Return or signal load failure to app layer
  - [ ] `MainWindow` (or bootstrap) shows status bar / dialog message (Epic 6 pattern)

- [ ] Unit tests (AC: 4)
  - [ ] `tests/unit/test_preferences.py` and/or `test_app_state.py` with `tmp_path`
  - [ ] Atomic write + corrupt read scenarios
  - [ ] No Qt imports

- [ ] Docs (AC: 5)
  - [ ] AD-10 already in `architecture-spine.md` — verify `docs/architecture.md` if it mirrors ADs

- [ ] Update `deferred-work.md` — strike JSON persistence items when done

## Dev Notes

### Current implementation (non-atomic)

```python
# core/preferences.py ~185
self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

# core/app_state.py ~68
self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
```

Contrast: `ProjectWriter.write()` uses `<dest>.tmp/` then rename (AD-4).

### App-layer notification

Use existing `_set_status()` / error colour for corrupt prefs on cold start. Avoid importing Qt from `core/`.

### Out of scope

- JSON schema versioning / migrations
- Encrypting preferences

### References

- AD-4, AD-10 — `architecture-spine.md`
- AD-5 — prefs write triggers unchanged (auto-save, import, factory only)
