---
id: L-20261004T150200Z-frozen-header-default-contradicted-fixture
title: "A frozen C++ header's default MPE bend range (48 semitones) contradicted the frozen fixture's value (2)"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: High
tags: [tech:cpp, phase:specification, kind:integrity]
recorded_by: planner
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:02:00Z
---
## Trigger
Writing default parameter values into a C++ interface header (soc_core.h) from a design decision (D-006) while a fixture generated independently (tests/make_fixtures.py) encodes the same constant.
## What went wrong
soc_core.h defaulted encodeMpe's bendRangeSemitones to 48.0, matching a generic MPE convention, while tests/fixtures/mpe.json (generated separately, from the actual D-006 decision of +/-2 semitones for precision) recorded 2.0. The two were never cross-checked against each other before the freeze.
## Correction
Corrected the header's default to 2.0, matching the fixture and D-006's stated rationale (24x the bend resolution needed for the plugin's narrow intra-semitone use).
## Prevention rule
When a numeric constant appears in both a frozen header and a frozen fixture, grep both for that constant's name/role and diff the values before freezing either.
## Detection check
grep -n bendRangeSemitones src/soc_core.h tests/fixtures/mpe.json -- the default in the header and the value recorded in the fixture must match.
## Evidence
premortem/round-1.md: "A contradiction was found between two frozen artifacts..."; soc_core.h diff changing 48.0 to 2.0. Recorded retroactively when the addendum was adopted mid-run.
