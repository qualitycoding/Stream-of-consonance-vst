# RETROSPECTIVE (S-RETRO)

Written adopting the lessons & knowledge addendum mid-run, as the implementing agent, on a plan
already pushed. This is one pass over the run's records; it re-runs nothing and changes no
deliverable except the lesson/knowledge files it produces and the one planning correction
(D-009) already made and logged separately in `DEVIATIONS.md` before this file was written.

## Inputs reviewed

Full commit history on this branch, `DEVIATIONS.md`, `TEST_CHALLENGE.md`,
`INTERFACE_AMENDMENT.md`, `premortem/round-1.md` and `round-2.md`, `plan/TRACEABILITY.md`'s
implementation-status note, and `research/PRIOR_KNOWLEDGE.md` (this run's catch-up store read).
No `EXECUTION_LOG.md`, `BLOCKED.md`, or `GATE-*.md` exist on this branch — the run never halted
and no human gate preceded this one.

## 1. What went wrong, and is every correction recorded as a lesson?

Ten corrections were identified across the run (two during planning, eight during
implementation): stray superseded test files contradicting the freeze; a frozen header's default
contradicting a frozen fixture; an undeclared cents reference in the fixtures (the Critical
pre-mortem finding, R-001); a genuine gap in the frozen `soc_core.h` contract found only by
implementing against it; an attempted floating-point fix that regressed previously-passing tests
before being reverted; a `git push` transport failure worked around via the GitHub REST API; a
scripted edit that silently no-op'd; a bulk delete that removed a tracked file; a local branch
left diverged from an API-pushed remote; and a UI parameter range set without checking the
attainable range for the actual configuration. **All ten are recorded** as `L-20261004T1501..1510`
in `lessons/`, each with the trigger, correction, and a checkable prevention rule.

## 2. What was overlooked?

- **A step that should have been in the plan**: nothing in `plan/PLAN.md` instructed red-verifying
  the plugin-level tests (T-015..T-020) before S-009 begins implementing against them — S-009's
  `Done when` covers it, but the step template's `Actions` don't call it out explicitly the way
  S-004's actions do for the core suite. Not corrected (would touch a frozen plan step); noted
  here for whoever runs S-009.
- **A check that would have caught a problem sooner**: the Phase 3.5 Cold-Read Gate was run by
  the planner itself (no subagent spawning available), not a genuinely fresh reader. Both defects
  it did catch (the MPE bend-range contradiction, the interface gap found while implementing
  `generateStream`) are exactly the class of defect a fresh reader is supposed to catch — the gate
  worked, but a second, truly independent pass before S-009 is still worth doing, as
  `INTERFACE_AMENDMENT.md` already recommended.
- **Knowledge that had to be rediscovered**: none found. The store (once loaded this turn) covered
  the upstream Python model thoroughly; nothing in this run's C++ port contradicted it.

## 3. Which lessons loaded in R0 (here, the catch-up read) were not applied, or recurred anyway?

See `research/PRIOR_KNOWLEDGE.md`'s applicability table in full. One genuine recurrence:
`L-20261004T102005Z-calibration-targets-before-attainable-range` (the original Python-package
run's finding that calibration/UI targets need an attainable-range check, not the model's nominal
range) recurred in this run's own `A-004` (the Consonance parameter's original −0.7…3.1 range).
Recorded as `L-20261004T151000Z`, with `recurrence_of` set and the prevention rule strengthened
("treat *range = model's published range* as a default to actively distrust"), and corrected via
`D-009`. Every other loaded lesson either did not apply to a C++/JUCE port or was already followed.

## 4. Which new facts about the Subject are not yet knowledge items?

Six were identified and written (`K-20261004T1511..1516`): PCG64's advance-then-output ordering,
the reverse-engineered SeedSequence algorithm, the numpy array-vs-scalar ufunc rounding
discrepancy, the circular-correlation shift-linearity optimization, the JUCE 8-vs-9 VST3 breaking
change, and the GitHub REST API push fallback. No further undocumented facts were found on review.

## Schema check

`python3 check_knowledge_schema.py` (run from `vst/`) reports **all entries valid** for all 10
lessons and 6 knowledge items written this run.

## Done when

Every finding above links to an `L-` or `K-` file, and the schema check passes. Both hold.
