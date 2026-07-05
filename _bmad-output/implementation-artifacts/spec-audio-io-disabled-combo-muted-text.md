---
title: 'Muted disabled Audio I/O combo text'
type: 'feature'
created: '2026-07-05'
status: 'done'
route: 'one-shot'
---

# Muted disabled Audio I/O combo text

## Intent

**Problem:** When the Audio I/O `ComboField` is disabled (MIDI Effect preset or `is_midi_effect` toggle), its text stayed at the default bright colour instead of matching the muted grey used for locked Plugin Type checkbox labels.

**Approach:** Style `QComboBox:disabled` in the global theme with `TEXT_MUTED` (same token as disabled checkboxes/radios), muted caret, and disabled input background. Bump `REVISION_DATE` to `2026-07-05`; keep `VERSION` at `1.0.0`.

## Suggested Review Order

- Disabled combo uses `TEXT_MUTED` and muted caret
  [`theme.py:144`](../../app/theme.py#L144)

- About revision date bumped for this release touch-up
  [`version.py:4`](../../app/version.py#L4)

- Test mirrors new revision date
  [`test_about.py:8`](../../tests/unit/test_about.py#L8)
