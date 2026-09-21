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
