# PRIOR_KNOWLEDGE

Written adopting the lessons & knowledge addendum as the **implementing agent, plan already
pushed**. Per the addendum's adoption rules this run skips a formal R0 (research is over, and a
plan that has passed its pre-mortem should not be reopened mid-implementation) — this file is the
catch-up read of the store instead, done during `S-RETRO`, recording which loaded items would
have applied had R0 run before Phase 1.

## Store read

Both `qualitycoding/Lessons` and `qualitycoding/knowledge` existed already, populated by an
earlier run (`gen-20260919T204010Z-consonance-inverse`) that built the Python `consonance`
package this VST ports — the exact upstream of this task's Subject. 11 lessons, 14 knowledge
items, all tagged and read in full.

**Task tags** (Appendix C), chosen now and recorded as `A-011`: `domain:audio`,
`domain:music-perception`, `tech:python` (the oracle), `tech:numpy`, `tech:git`, `tech:github`,
plus two new tags this run adds to the taxonomy: `tech:cpp`, `tech:juce`.

## Checklist (prevention rules compiled from matching lessons, severity then recency)

1. **[High]** For every parameter that defines the scored state, confirm how many notes the
   energy function actually receives before writing calibration or demo code.
   (`L-20261004T102003Z-window-semantics-off-by-one`)
2. **[Medium]** Derive every performance budget from a measured reference run, not the test's own
   shape. (`L-20261004T102002Z-perf-test-budget-not-derived`)
3. **[Medium]** Before closing implementation, map every plan step and pre-mortem control to a
   file or test that delivers it; list each unmapped one in `DEVIATIONS.md`.
   (`L-20261004T102010Z-plan-controls-not-traced-to-delivery`)
4. **[Medium]** Validate a file before rotating it to a backup; never let an unvalidated write
   replace the only good backup. (`L-20261004T102004Z-checkpoint-rotated-corrupt-file`)
5. **[Medium]** Produce every reported test count from the test runner in the same turn; never
   carry a count over from earlier text. (`L-20261004T102009Z-stale-test-counts-in-reports`)
6. **[Medium]** Before adding a module for a capability, grep the package for one with the same
   responsibility; if two exist, name the unused one before the push.
   (`L-20261004T102008Z-duplicate-pitch-modules-shipped`)
7. **[Medium]** At the start of a turn that continues a run, verify the working tree against the
   remote before trusting it. (`L-20261004T102007Z-sandbox-reset-lost-working-tree`)
8. **[Medium]** Before a citation, formula constant or default value appears in code, retrieve it
   from the primary source in the same turn; otherwise label it UNVERIFIED.
   (`L-20261004T102001Z-recalled-literature-facts-wrong`)
9. **[Low]** Write the intended expression directly; grep the staged diff for multiply-by-zero,
   TODO and FIXME before committing. (`L-20261004T102006Z-placeholder-arithmetic-left-in-code`)
10. **[Low]** Estimate the attainable score range before choosing calibration or UI targets.
    (`L-20261004T102005Z-calibration-targets-before-attainable-range`)
11. **[Low]** Label a causal explanation not backed by a run in the same session as a hypothesis.
    (`L-20261004T102011Z-untested-causal-explanation-stated-as-fact`)

## Applicability to this run

| Lesson | Applied? | How |
|---|---|---|
| 1 (window semantics) | Already correct | `CandidateScorer`/`generateStream`'s window handling (`state = full[-(window-1):]`) was built directly from the *corrected* Python source (`consonance/sampler.py` post-fix), so it already uses `window-1` held notes, not `window`. Confirmed by re-reading the cited commit's fix against `soc_core.cpp`'s identical logic. No action needed. |
| 2 (perf budget) | Partially — see R-002 | T-013's 40ms budget came from a Python reference measurement (`spike_01_timing.py`), not the test's own shape, which is the rule's intent. But the budget was derived from the planning sandbox's Python timing, not a measurement on the actual target machine — DEVIATIONS.md already flags this as unresolved (D-002's resolution ladder pending real hardware). |
| 3 (controls traced to delivery) | Partially — see TRACEABILITY.md | `plan/TRACEABILITY.md` maps every test to a step, but S-009 onward (the JUCE plugin itself) is entirely undelivered, documented as environment-blocked rather than silently dropped. |
| 4 (backup validation) | N/A | No checkpoint-rotation code exists in this port; `soc_core.cpp` has no persistence layer. |
| 5 (stale test counts) | Already followed | Every test count reported to the user this run came from an actual `./test_core` invocation in the same turn, never carried over. Re-verified against this run's own transcript before writing this file. |
| 6 (duplicate modules) | **Checked, confirmed clean** | Verified `kJustIntervalsCents` in `soc_core.cpp` was ported from `consonance/pitchset.py::JUST_INTERVALS_CENTS` (the module `generator.py` actually imports), not the dead `consonance/pitchgrid.py::DEFAULT_JUST_RATIOS` this lesson warns about. T-008's exact match against the oracle's `candidate_cents()` output already proved this indirectly; this is the direct confirmation. |
| 7 (working tree reset) | Not triggered, but gap found | The working tree survived every turn of this run so far (no reset observed). Separately, this turn found the local branch had diverged from what the API push actually sent to GitHub — not a sandbox reset, but the same class of problem (trusting local state without checking the remote). See `L-20261004T213000Z-local-head-diverged-from-api-push` below. |
| 8 (recalled facts) | Already followed | Every model constant in `soc_core.cpp` (roughness CBW formula, harmonicity sigma/rho, composite weights) was read directly from `consonance/*.py` source and cross-checked against fixtures, never recalled from training data. |
| 9 (placeholder arithmetic) | Already clean | No placeholder or TODO arithmetic was committed; `sampleNext`'s known limitation (no novelty-prior support) is implemented honestly as a documented restriction, not a stub. |
| 10 (attainable range before targets) | **Was violated, now fixed** | A-004's original Consonance range (−0.7…3.1) was the model's full regression range, not an attainable-range measurement for the plugin's actual 4-note window — exactly this lesson's mistake. Corrected via D-009 using `K-20261004T102022Z-composite-score-attainable-range`'s numbers. See the plan diff accompanying this run. |
| 11 (untested causal claims) | Already followed | No causal "because/since" explanation for an empirical result was stated in this run without a cited measurement (e.g. the 612ms/30ms-budget claims cite `spike_01_timing.py` directly). |

Lesson 10 is the one genuine recurrence this run would have prevented had R0 run first — logged as
its own lesson below rather than silently fixed, per Rule 11's recurrence handling.
