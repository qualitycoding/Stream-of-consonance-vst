# INTERFACE_AMENDMENT — soc_core.h

Written during implementation of S-008, in place of `TEST_CHALLENGE.md` because the defect is in
the frozen **interface contract** (`src/soc_core.h`), not in a frozen test's assertions or a
fixture value. Per `plan/PLAN.md`'s default decision rule, a change to a public interface in
`soc_core.h` requires a halt; this record is that halt, with the minimal fix applied rather than
re-running Phase 0, because the fix changes no test assertion, no fixture, and no numerical
behaviour — it only adds a read-only accessor.

## Defect

`generateStream(const CandidateScorer&, const StreamConfig&, int nSteps, Pcg64&)` must return the
actual **cents** value chosen at each step. But nothing in its frozen signature carries the
candidate cents, and `CandidateScorer` (as specified) exposed only `score()` (one number per
candidate) and `candidateCount()` — never the candidate cents themselves. T-011 confirms this is
not a workaround-able gap: it constructs the scorer from `candidateCents(spec)` and passes only
the scorer (not the cents) into `generateStream`, so the cents **must** be recoverable from the
scorer object itself.

`sampleNext` has the same defect, but it is not called by any frozen test (verified by grep over
`tests/cpp/test_core.cpp`), so it is not on T-011's critical path.

## Fix

Add one read-only accessor to `CandidateScorer`:

```cpp
const std::vector<double>& candidateCentsView() const;
```

No existing declaration changes. No test's assertions change. No fixture changes. The freeze
manifest is regenerated to cover the amended `soc_core.h`, and this file records why.

## Root cause, for the record

This should have been caught by the Phase 3.5 Cold-Read Gate, which the plan itself notes (see
`vst/HANDOFF.md`) was run by the planner rather than a genuinely fresh agent, because no subagent
spawning was available (R-005-adjacent limitation). A fresh reader attempting to implement
`generateStream` from the header alone — exactly what happened here — would have found this
immediately. Recorded as evidence for why an independent cold read is still worth doing before
the JUCE-dependent steps (S-009 onward).
