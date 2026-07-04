---
title: 'OS tree connector alignment tuning'
type: 'feature'
created: '2026-07-04'
status: 'done'
route: 'one-shot'
baseline_commit: ''
---

# OS tree connector alignment tuning

## Intent

**Problem:** Tree connector lines in Workspace and Artefacts sections (Project and Preferences tabs) were misaligned: the trunk sat too far right, branches hugged anchor labels too tightly, OS row labels needed more indent, and horizontal branches sat 2 px too high relative to OS labels.

**Approach:** Centralise the geometry tweaks in `path_specs.py` constants consumed by the shared `OsPathTreeGroup` widget — trunk X −3 px, anchor gap +5 px, field left margin +20 px (auto-extending branch length), branch Y +2 px.

## Suggested Review Order

- Trunk, anchor gap, and branch offset constants drive all four user tweaks
  [`path_specs.py:12`](../../app/pages/path_specs.py#L12)

- Anchor gap applied where vertical trunk starts below section labels
  [`os_path_tree_group.py:56`](../../app/widgets/os_path_tree_group.py#L56)

- Branch Y offset lowers horizontal connectors to OS label midline
  [`os_path_tree_group.py:86`](../../app/widgets/os_path_tree_group.py#L86)

- Left margin on OS row host extends labels and branch endpoints together
  [`os_path_tree_group.py:70`](../../app/widgets/os_path_tree_group.py#L70)
