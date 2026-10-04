---
id: L-20261004T151000Z-parameter-range-set-without-attainable-range-check
title: "A UI parameter's range was set to a model's full regression range instead of what the actual configuration can attain"
status: active
supersedes: []
recurrence_of: L-20261004T102005Z-calibration-targets-before-attainable-range
occurrences: 1
severity: Low
tags: [domain:music-perception, tech:cpp, phase:specification, kind:wrong-assumption]
recorded_by: planner
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:10:00Z
---
## Trigger
Choosing the min/max range for a user-facing control (a target value fed to a directed sampler) from a model's published or fitted range, without first checking what the sampler's actual configuration (sonority size, window, candidate set) can reach.
## What went wrong
A-004 set the plugin's Consonance parameter to the composite model's full published regression range (-0.7 to 3.1). That range spans chords of every size; the plugin's 4-note window cannot reach anywhere near its top end (per K-20261004T102022Z-composite-score-attainable-range, loaded from the knowledge store: 4-note random chords have p95=1.29, max=2.02, and a target of 2.4 collapses). This is the exact mistake L-20261004T102005Z already recorded, from the same codebase's own earlier calibration work -- it recurred here because this run's intake happened before R0 would have loaded that lesson, and the correction below was only made retroactively while adopting the addendum.
## Correction
Narrowed the range to -0.7 to 2.2 (D-009), citing the specific attainable-range numbers rather than the model's nominal fitted range, and flagged in D-009 that S-016's soak test should verify this empirically once the real instrument exists.
## Prevention rule
Before setting a user-facing range for any target fed to a directed/weighted sampler, check the knowledge store (or run a quick attainable-range measurement) for the specific configuration being used, not the model's nominal or published range; this is now the second occurrence of this exact mistake in this codebase's history -- treat 'range = model's published range' as a default to actively distrust, not a safe shortcut.
## Detection check
Any UI/parameter range table entry sourced from a model's 'published' or 'fitted' range, without a cited attainable-range measurement for the actual configuration in use, should be treated as unverified.
## Evidence
plan/DECISIONS.md D-009; plan/ASSUMPTIONS.md A-004 (diff changing 3.1 to 2.2); research/PRIOR_KNOWLEDGE.md row 10. Recorded during S-RETRO, as a recurrence.
