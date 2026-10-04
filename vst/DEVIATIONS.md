# DEVIATIONS

Logged per the plan's default decision rule: reversible, non-scope-expanding choices made
during implementation, applied and continued rather than halted on.

## Build: core test suite compiled at -O3, not -O2

`tests/cpp/Makefile`'s default `CXXFLAGS` changed from `-O2` to `-O3` (no `-ffast-math`, no
semantics change). Measured effect on T-013's benchmark: 51.5 ms -> 48.1 ms. Verified this does
not change any test's pass/fail status other than the timing itself (all 15 tests produce
identical results at -O2 and -O3, checked before and after). Does not touch `soc_core.h` or any
frozen file's *content*, only a build flag in the non-frozen Makefile.

## T-013 remains over budget (S-006's documented failure path)

Measured 48-52 ms against the 40 ms budget in this planning sandbox, a shared cloud container of
unknown, possibly throttled CPU characteristics -- not the target Windows machine. Per S-006's
`On failure`, the correct response is D-002's resolution ladder (drop free mode's default
candidate resolution), applied once real hardware is available to measure against, rather than
weakening T-013 itself. Likely bottleneck, for whoever picks this up: `CandidateScorer::score()`'s
held-candidate cross-roughness term calls `std::pow(x, 0.65)` and `std::exp()` roughly 870,000
times per call (heldPartials x candPartials x nCandidates, here 33 x 11 x 2401) -- an
algorithmic cost, not something `-O3` alone resolves. Left as-is rather than risking an
unverified rewrite of the numerically load-bearing roughness term under time pressure; the
existing implementation is *correct* (T-002, T-006, T-009, T-014 all pass), only not yet fast
enough on this specific machine.

## T-011: see TEST_CHALLENGE.md

Filed formally rather than logged here, since it required reverting an attempted fix.

## Adopted the lessons & knowledge addendum (v3.1 -> v3.2 addendum)

Mid-run, as the implementing agent, per the addendum's "Implementing agent (the plan is already
pushed)" adoption path. No frozen test, security control, data integrity guarantee, public
interface, or evidence class is touched by this — it adds process (Rules 11-13), two closing plan
steps, and new non-frozen files (`lessons/`, `knowledge/`, `research/PRIOR_KNOWLEDGE.md`,
`RETROSPECTIVE.md`, `plan/GATES.md`) — so v3.1's default decision rule permits applying it without
a halt. Ran the retroactive-lessons catch-up (10 lessons for corrections already made this run)
and the knowledge-item catch-up (6 new facts), per the addendum's explicit instructions for this
adoption path; skipped R0 proper (research is over) but read the store as part of S-RETRO instead,
recording applicability in `research/PRIOR_KNOWLEDGE.md`.

**Two-repo split, not the addendum's single-store default.** The addendum's default proposal is
one repository (`agent-knowledge`) holding both `lessons/` and `knowledge/`. The human specified
two separate repositories instead (`qualitycoding/Lessons`, `qualitycoding/knowledge`), matching
their own pre-existing convention from an earlier run on this same codebase (confirmed: both
repos already existed, populated by `gen-20260919T204010Z-consonance-inverse`, the run that built
the Python `consonance` package this plugin ports). Followed the human's explicit instruction and
established convention rather than the addendum's generic default.

**One planning correction made as a direct result of the catch-up read**: `D-009` narrows the
Consonance parameter's range from the model's full published regression range (−0.7…3.1) to
−0.7…2.2, using attainable-range evidence for 4-note sonorities that the knowledge store already
held (`K-20261004T102022Z-composite-score-attainable-range`) but this plan's original `A-004` had
not checked. Logged as its own decision record (D-009) and as a recurrence of an existing lesson
(`L-20261004T151000Z`, `recurrence_of: L-20261004T102005Z`), not silently folded into this entry.
