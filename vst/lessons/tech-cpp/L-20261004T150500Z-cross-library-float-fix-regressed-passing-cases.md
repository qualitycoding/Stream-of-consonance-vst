---
id: L-20261004T150500Z-cross-library-float-fix-regressed-passing-cases
title: "A fix for one failing floating-point boundary case was adopted before re-running the full suite, and it silently broke 12 previously-passing values"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: High
tags: [tech:cpp, tech:numpy, phase:implementation, kind:process]
recorded_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:05:00Z
---
## Trigger
A C++ reimplementation of a numpy-array-computed reference disagrees with the oracle only on a chord sitting exactly on a discrete threshold (here familiarity's 20-cent tolerance), traced to numpy's SIMD array ufunc rounding the last bit differently from numpy's own scalar path for the same input.
## What went wrong
Reformulated the cents computation (summing exact stream cents with one shared, once-computed offset instead of round-tripping each note through Hz independently) to make the one failing boundary chord land correctly. It did: that one chord now matched. But the fix was adopted on the strength of that single case, without re-running the complete test suite first -- it actually changed the numeric value computed for every chord, not just the boundary one, and regressed 12 previously-passing values in T-009 plus a previously-exact stream (free1_t1.6_seed3).
## Correction
Reverted immediately on discovering the regression (full-suite check count dropped, not rose). Filed TEST_CHALLENGE.md documenting the root cause (numpy array-vs-scalar ufunc rounding is not reproducible from another language's standard libm) and three real options, without pretending a local reformulation could fix a cross-library rounding mismatch in general.
## Prevention rule
After any change to shared or general-purpose scoring code motivated by fixing one specific failing case, re-run the complete test suite before considering the fix validated -- especially when the change alters a computed numeric value rather than only a branch condition, since a value-level change can silently shift other, previously-correct cases.
## Detection check
A fix for test X is not accepted until the full suite's pass/check counts are compared before and after; any count that drops anywhere is a rejection of the fix, regardless of whether X now passes.
## Evidence
vst/TEST_CHALLENGE.md (full writeup, including the reverted diff's description); vst/research/spikes/spike_05_familiarity_offset.py. Recorded during S-RETRO.
