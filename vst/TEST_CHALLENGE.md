# TEST_CHALLENGE — T-011, fixture `free5_t1.6_seed7`

Filed per `tests/FROZEN.md`'s procedure, during implementation of S-008.

## Status of T-011 overall

**4 of 5 fixture streams reproduce exactly**: `standard_t1.6_seed7`, `standard_t0.8_seed1`,
`standard_t2.0_seed42`, and `free1_t1.6_seed3` (the 1-cent free-mode stream) all match the
oracle note-for-note and score-for-score. Only `free5_t1.6_seed7` diverges, starting at its
second note. This challenge concerns that one fixture only.

## What was checked before filing this

This was not treated as a C++ bug until proven otherwise:
- `CandidateScorer::score()` was differential-tested against the already-verified literal
  `compositeScore()` on the exact failing chord and agreed to the last bit — the fast path
  (D-004's rotation/correlation optimization) is not the cause.
- Roughness and harmonicity for the failing chord match the Python oracle to 1e-10. Only
  **familiarity** diverges: my port returns "undefined" (chord not within 12-TET tolerance)
  where the oracle returns a defined log-probability.
- The chord is `[0, 700, 930, -590]` cents (stream-relative, 220 Hz). Converted to
  model-relative cents (C4 reference) and reduced to bass-relative intervals, one interval
  lands at **exactly** the model's 20-cent familiarity tolerance boundary (`|rel - 100*round(rel/100)| 
  == 20.0`, a strict-inequality cutoff — 20.0 itself is inside tolerance).
- Root cause, isolated and reproduced standalone in
  `research/spikes/spike_05_familiarity_offset.py`: numpy's **array-vectorized** `log2`/`power`
  ufuncs (used when `make_fixtures.py` scored the fixture, since `consonance` operates on numpy
  arrays throughout) round the last bit differently from numpy's own **scalar** `log2`/`power`
  for this input — confirmed by computing both paths directly: array path gives cents
  `630.0` exactly; scalar path gives `630.00000000000034`. C++'s `std::log2`/`std::pow` (glibc)
  agree with numpy's *scalar* path, not its array path. The ~1e-13-cents discrepancy is normally
  invisible (both composite scores agree to 1e-10, comfortably inside every other fixture's
  1e-9 tolerance) but here it straddles a **discrete** branch, not a continuous one.
- I attempted a fix (computing model-relative cents as a single shared additive offset from the
  exact stream cents, so a common rounding error cancels in the difference familiarity checks).
  It fixed this one chord but **broke 12 previously-passing values in T-009** and the previously-
  exact `free1_t1.6_seed3` stream, because it does not reproduce numpy's actual array-path
  rounding in general — it only coincidentally lands correctly for this one case. Reverted; the
  diff is preserved in this session's history for anyone who wants to see why it doesn't work.

## Why this is a fixture/tolerance-design issue, not a C++ defect

Matching numpy's specific SIMD-dispatched ufunc rounding bit-for-bit from another language is
not achievable through reformulating the arithmetic — it would require reimplementing numpy's
internal vectorized transcendental kernels, which are an unversioned, CPU-feature-dependent
implementation detail (confirmed: numpy's own `2.0**x` and `np.exp2(x)` already disagree with
each other in the last bit on this same input, on this same machine, within the same numpy
version). `familiarity`'s hard 20-cent cutoff (`consonance/familiarity.py::TOLERANCE_CENTS`)
converts an unavoidable, otherwise-harmless ~1e-13 cents of cross-implementation noise into a
discrete branch flip, which a downstream RNG-weighted sampler then amplifies into full note-by-
note divergence for the rest of the stream. This is a general property of the model's design,
not specific to this port.

## Proposed resolutions (for the next planning cycle — not applied here)

1. **Soften the familiarity boundary** by a small platform-noise epsilon (e.g. compare against
   `20.0 + 1e-6` instead of `20.0`) in both the Python reference and the C++ port. This is a
   genuine, if microscopic, change to the model's output for chords in a ~1e-6-cent sliver
   around the boundary, so it is a Phase 0 scope change (D-003 forbids changing the model's
   numerical behaviour unilaterally), not something to slip in during implementation.
2. **Regenerate this one fixture** with a seed/target that doesn't happen to land a chord on
   the exact boundary. Cheaper, but changes what the frozen fixture is asserting and needs the
   same sign-off.
3. **Accept the gap as documented**, ship with 4/5 streams bit-exact and this one flagged. In
   practice a live-generated stream hitting this exact boundary is rare and, worse case, only
   causes the *rest of that one run* to diverge from what a Python bounce would have produced —
   it does not crash, produce invalid output, or affect any other stream.

## Recommendation

(3) for now, escalated to (1) if the human wants full SC-4 coverage. This does not block S-009
onward: the plugin's own bounce-reproducibility guarantee (SC-4 as experienced by a user, i.e.
"the same automation bounces to the same audio twice") is unaffected, since it only requires
matching *itself* run to run, not matching a specific Python-generated reference stream.
