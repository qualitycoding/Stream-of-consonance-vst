---
id: L-20261004T150400Z-interface-gap-found-only-by-implementing
title: "A frozen interface header specified generateStream without any way to learn which candidate was chosen"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: High
tags: [tech:cpp, phase:specification, kind:wrong-assumption]
recorded_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:04:00Z
---
## Trigger
Freezing a C++ class interface (CandidateScorer) based on what its test callers need to construct and call, without separately checking what a function that must consume its results (generateStream) needs to read back out of it.
## What went wrong
generateStream(scorer, config, nSteps, rng) must return the actual cents chosen at each step, but CandidateScorer exposed only score() (one number per candidate) and candidateCount() -- never the candidate cents themselves, and generateStream's own signature carried no candidate-cents parameter either. The gap was invisible to Phase 2.3 red verification (stubs just throw, regardless of whether the real signatures are sufficient) and was only caught by actually writing generateStream's real implementation.
## Correction
Added one read-only accessor, CandidateScorer::candidateCentsView(), documented in INTERFACE_AMENDMENT.md as a post-freeze amendment with its root cause, and re-generated the freeze manifest.
## Prevention rule
Before freezing a C++ (or any strongly-typed) interface header, write a throwaway sketch implementation of every declared function against the header alone, not just enough to let stub-based red verification pass -- red verification proves the header compiles, not that it is sufficient.
## Detection check
A header passes this check only once every declared function has at least a sketch (even TODO-bodied) implementation written against the frozen signatures with no signature changes needed.
## Evidence
vst/INTERFACE_AMENDMENT.md (full root-cause writeup); src/soc_core.h diff adding candidateCentsView(). Recorded during S-RETRO.
