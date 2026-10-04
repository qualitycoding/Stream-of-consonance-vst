---
id: L-20261004T150300Z-fixture-cents-reference-undeclared
title: "Golden fixtures gave cents values with no stated reference pitch, risking a silent, undetectable scoring error"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Critical
tags: [tech:python, tech:cpp, phase:specification, kind:verification-gap]
recorded_by: planner
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:03:00Z
---
## Trigger
Generating golden fixtures by converting a model's internal cents convention to frequency, when the model defines more than one reference pitch for different purposes (here: a generator reference, 220 Hz, and a separate pitch-class-origin reference inside the harmonicity term, C4).
## What went wrong
tests/make_fixtures.py emitted cents without stating which reference they were relative to. Converting with the wrong one (the model's own REF_HZ constant, the obvious one to reach for) silently shifts the roughness term by up to 0.082 score units -- nothing raises, the sampler would just track the wrong level set.
## Correction
make_fixtures.py now writes an explicit ref_hz field (and a one-line explanation of the two references and why they differ) into every fixture file; a new test (T-000) asserts every fixture declares it before any other test runs.
## Prevention rule
When a model defines more than one reference value for the same unit (here two different frequencies both called a "reference"), every fixture using that unit must declare which reference it used, and a cheap, dependency-free test must assert the declaration is present before any value-level test runs.
## Detection check
grep -L ref_hz tests/fixtures/*.json should print nothing; T-000 enforces this at test time.
## Evidence
premortem/round-1.md, finding R-001 (Critical, closed); vst/tests/make_fixtures.py's write() function; vst/src/soc_core.h's comment on kModelRefHz vs kGeneratorRefHz. Recorded retroactively when the addendum was adopted mid-run.
