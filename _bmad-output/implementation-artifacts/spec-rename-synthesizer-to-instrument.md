---
title: 'Rename Synthesizer to Instrument in Plugin Type'
type: 'chore'
created: '2026-06-27'
status: 'done'
route: 'one-shot'
---

# Rename Synthesizer to Instrument in Plugin Type

## Intent

**Problem:** The Plugin Type UI labels the synth option "Synthesizer" and its hint repeats "Instrument." before the description, which is redundant and inconsistent with JUCE terminology and existing user docs that already use "Instrument".

**Approach:** Change the display label in `PLUGIN_TYPES` to "Instrument", shorten the synth hint to "Receives MIDI, produces audio.", and align README / USER-MANUAL references. Internal JSON key `synth` is unchanged.

## Suggested Review Order

- Canonical display label for the synth plugin type
  [`plugin_settings.py:9`](../../core/plugin_settings.py#L9)

- Hint text shown after the em dash on the Plugin Type row
  [`plugin_type.py:16`](../../app/pages/plugin_type.py#L16)

- Project README plugin-type bullet
  [`README.md:13`](../../README.md#L13)

- Preferences section table in the user manual
  [`USER-MANUAL.md:409`](../../docs/USER-MANUAL.md#L409)
