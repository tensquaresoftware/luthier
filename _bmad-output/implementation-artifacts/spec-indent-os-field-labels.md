---
title: 'Indent OS field labels in Workspace and Artefacts'
type: 'feature'
created: '2026-07-01'
status: 'done'
route: 'one-shot'
baseline_commit: 'fc433acd574b7b9f7ebb0fb11391475766247ea0'
---

# Indent OS field labels in Workspace and Artefacts

## Intent

**Problem:** On the Project and Preferences tabs, the Windows, macOS, and Linux path rows in the Workspace and Artefacts sections sit flush with section headings, making the hierarchy hard to scan.

**Approach:** Introduce a shared left margin constant and apply it to the per-OS path row containers in `WorkspaceSection` and `ArtefactsSection`, so OS rows read as nested under their parent headings without changing field widgets.

## Suggested Review Order

- Shared indent constant for all per-OS path rows
  [`path_specs.py:9`](../../app/pages/path_specs.py#L9)

- Workspace destination and JUCE groups both use the nested layout
  [`workspace.py:95`](../../app/pages/workspace.py#L95)

- Artefacts per-OS paths indented under copy-option checkboxes
  [`artefacts.py:101`](../../app/pages/artefacts.py#L101)
