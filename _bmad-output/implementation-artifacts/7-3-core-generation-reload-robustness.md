# Story 7.3: Core Generation & Reload Robustness

Status: backlog

<!-- Epic 7 — Release Hardening. Priority: SHOULD. Order: third. -->

## Story

As a JUCE developer,
I want generation and project reload to handle edge-case inputs and legacy projects gracefully,
So that unusual paths, hand-edited sidecars, and legacy CMake projects fail with clear, actionable messages instead of silent corruption or raw exceptions.

## Acceptance Criteria

1. **Given** a `juce_dir` containing quotes, `$`, or spaces, **when** `CMakeLists.txt` is generated, **then** the `set(JUCE_DIR ...)` line is correctly quoted/escaped for CMake.
2. **Given** artefact JSON path fields with quotes or control characters, **when** presets are rendered, **then** output remains valid JSON.
3. **Given** string booleans in sidecar/dict (`"ON"`, `"false"`, etc.), **when** `ProjectSpec.from_dict()` runs, **then** bool fields coerce correctly.
4. **Given** hand-edited `.luthier.json` with wrong types or `null` for required fields, **when** `read_project()` runs, **then** validation fails explicitly.
5. **Given** empty valid sidecar `{}`, **when** `read_project()` runs, **then** load fails with message distinguishing empty sidecar from parse failure.
6. **Given** bool CMake cache options in template, **when** project regenerates, **then** `CACHE BOOL` uses `FORCE`.
7. **Given** unknown `pluginType`, **when** generation/context build runs, **then** clear validation error — not raw `KeyError`.
8. **Given** rare `ProjectWriter` rename failure after old dir removal, **when** failure path runs, **then** behaviour documented and tested.
9. **Given** legacy CMake fallback failure, **when** error shown, **then** message distinguishes sidecar vs CMake failures and lists missing fields.
10. **Given** escaped quotes in CMake values, **when** regex fallback runs, **then** correct parse or clear failure.
11. **Given** pytest, **when** edge-case tests run, **then** no Qt imports.

## Tasks / Subtasks

- [ ] `core/render_context.py` / CMake template — JUCE_DIR quoting (AC: 1)
- [ ] Preset JSON rendering — special chars in artefact paths (AC: 2)
- [ ] `core/project_spec.py` — `from_dict` bool coercion helper (AC: 3)
- [ ] `core/project_reader.py` — sidecar validation, empty `{}`, error taxonomy (AC: 4, 5, 9, 10)
- [ ] `Templates/CMakeLists.txt` — `CACHE BOOL` + `FORCE` (AC: 6)
- [ ] `core/plugin_settings.py` or validation — unknown plugin type (AC: 7)
- [ ] `core/project_writer.py` — rename failure edge case (AC: 8)
- [ ] App layer — propagate discriminated reader errors to status bar/dialog (AC: 9)
- [ ] Unit/integration tests in `tests/unit/` and `tests/integration/` (AC: 11)
- [ ] Update `deferred-work.md` — strike generation/reload items when done

## Dev Notes

### Modules to inspect

| Module | Deferred-work items |
|--------|---------------------|
| `core/render_context.py` | `_juce_dir_line`, special paths |
| `core/project_spec.py` | `from_dict` bool coercion |
| `core/project_reader.py` | Legacy messages, empty sidecar, regex quotes |
| `core/project_writer.py` | Rename after delete edge case |
| `core/project_generator.py` | Unknown plugin type |
| `Templates/CMakeLists.txt` | CACHE BOOL FORCE |

### Error message taxonomy (extend Story 2.2)

Distinguish at minimum:

- Malformed JSON sidecar
- Valid JSON but empty/invalid spec
- No sidecar — CMake parse failure (list missing fields)

App layer already has status bar (Epic 6) — use for open failures.

### Out of scope

- Qt widget tests
- Full JSON schema validation framework

### References

- Story 2.2 AC — CMake fallback error discrimination
- `tests/test_story_2_2.py` — legacy cases to migrate in 7.4
