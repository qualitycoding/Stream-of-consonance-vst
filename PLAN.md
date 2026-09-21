# Execution Plan — Reversible Consonance Model & Consonance-Targeted Tone-Stream Generator
Generation branch: `gen-20260919T204010Z-consonance-inverse`
Authoring model tier: Sonnet (see Phase 0 limitation). Status: PLAN + IMPLEMENTED 2026-09-19 (see IMPLEMENTATION_REPORT.md). Plan text below is unchanged from generation.

## Goal
Given a target consonance value c*, generate a stream of tones whose model-consonance stays at c*. The model must be usable in reverse (sample/solve for tones given c*).

## Phase 0 — Diagnostic & tier delegation
- Subagent spawning: NOT available in this environment (no spawn tool exposed). Tags below are recommendations for a host that supports it. The plan author ran at Sonnet tier, so tier-reserved work (architecture, pre-mortem) was performed at Sonnet and MUST get a Fable/Mythos review before acceptance (see Risk R-META).
- Tier hierarchy honoured: Mythos (orchestration, Reset decisions) > Fable (system design) > Opus (analysis/code logic) > Sonnet (synthesis/refactor) > Haiku (retrieval/parsing).

## Phase 1 — Isolation, research, checkpoints
- Branch: `gen-20260919T204010Z-consonance-inverse` (created locally; see PUSH STATUS).
- Research log with citations and VERIFIED/UNVERIFIED tags: `research/RESEARCH_LOG.md`.
- Checkpoint file: `.checkpoints/state.json` (schema_version 1) written after each sub-phase.

## Phase 2 — Frozen tests (see tests/FROZEN.md, tests/FROZEN.sha256)
Files: test_interference, test_harmonicity, test_composite, test_sampler, test_stream_and_checkpoint, test_chord_mh_and_level_set, test_operational.
Reset log: Before freezing, self-review found the first draft of the performance test invalid (it forced 6000 Python-level score calls, an unattainable budget dictated by the test rather than the requirement). Nothing had been committed, so the protocol was restarted at Phase 2 with a corrected test on the same, still-empty branch (equivalent to a Phase 0 re-run).

### Frozen API contract (implementing agents must match; package `consonance`)
- `timbre.Timbre(ratios, amps)`; `interference.dissonance(freqs_hz, timbre, model="sethares", max_hz=20000.0)` — raises ValueError on non-finite or <=0 freqs; ignores partials above max_hz.
- `harmonicity.harmonicity(cents, timbre, grid_cents=1.0)` — pitch-class, transposition/octave/permutation invariant, >=0.
- `composite.CompositeModel(timbre, weights=None, familiarity_mode="drop"|"strict")` with `.features`, `.score`, `.score_with_candidates(held_hz, candidate_hz)`, `.check_timbre`; `Weights`, `UnsupportedTuningError`, `TimbreMismatchError`. Familiarity for unseen 12-TET chord types must use additive smoothing (finite). Default weight signs: interference<0, harmonicity>0, familiarity>0.
- `sampler.sample_next`, `generate_stream`, `metropolis_chord`, `dyad_level_set` — log-sum-exp softmax; `SampleResult(cents, value, reached)`.
- `checkpoint.Checkpoint` — atomic write MUST use `os.replace`; keeps `<path>.bak`; `schema_version` field; `CheckpointVersionError`.

## Phase 3 — Plan (min tier per step; every long step ends with CHECKPOINT)
| Step | Tier | Work | Exit gate |
|---|---|---|---|
| S0 | Haiku | Verify UNVERIFIED items R7–R9 against primary sources; find `incon` license/URL. If a verified constant contradicts a frozen test → HALT, invoke Reset Rule. | Log updated, CHECKPOINT |
| S1 | Sonnet | Scaffold package, `Timbre`, config, weights file (H&P signs), CI running `sha256sum -c` before pytest. | tests import |
| S2 | Opus | Interference (Sethares first; Hutchinson-Knopoff variant behind `model=`). Vectorised over candidates. | test_interference green, CHECKPOINT |
| S3 | Opus | Harmonicity (Milne pitch-class spectrum, Gaussian blur, template sweep, KL from uniform). | test_harmonicity green, CHECKPOINT |
| S4 | Sonnet | Familiarity lookup (smoothed), `drop`/`strict` modes. | test_composite partial |
| S5 | Opus | Composite + `score_with_candidates`, timbre guard. | test_composite green, CHECKPOINT |
| S6 | Fable | Sampler design: candidate softmax, Metropolis chords, level-set dyads, optional Langevin refinement, diversity/novelty term, sequential terms (voice-leading, spectral distance). | design note approved by Mythos |
| S7 | Opus | Implement S6; unreachable-target handling. | test_sampler, test_chord_mh green, CHECKPOINT |
| S8 | Sonnet | Checkpoint/resume (atomic, .bak, versioned). | test_stream_and_checkpoint green |
| S9 | Opus | Validation harness: (a) calibration table c* → realised score distribution; (b) small listening-test protocol for non-12-TET/inharmonic timbres; (c) diversity metrics. | report committed |
| S10 | Haiku | Docs and usage examples. | docs build |
| GATE | Mythos | Accept/Reset decision; reviews Risks R1–R12. | signed |

Resiliency: each step reads `.checkpoints/state.json` on start, writes it on exit; generate_stream resumes bit-identically (RNG state saved).

## Phase 4 — Recursive pre-mortem (6 months post-deployment, assume catastrophic failure)
### Round 1 (initial exposure) — severity before mitigation
| ID | Failure vector | Sev | Control added |
|---|---|---|---|
| R1 | Composite weights fitted on Western 12-TET chords; generated "c*" not perceptually c* for microtonal/inharmonic material (research gap G1) | High | Output labelled "model-consonance"; `drop` mode for familiarity off-12-TET; S9 calibration + listening protocol; domain-of-validity warning emitted when tuning/timbre leaves calibrated domain |
| R2 | Scoring spectrum differs from synthesized spectrum | High | Single `Timbre` object; `check_timbre` runtime guard (frozen test) |
| R3 | Sethares/ERB/H-K constants misremembered (R7–R9 unverified) | High | S0 gate; tests use model-agnostic orderings/ERB fractions rather than exact constants; contradiction => Reset |
| R4 | Frozen test invalid or flaky (statistical/perf) | High | Statistical tests seeded with analytic bounds; single perf budget isolated under `perf` marker; Reset Rule |
| R5 | No published inversion method (G2): sampler may not converge for multi-note chords | High | Three redundant inversion routes (candidate softmax, MH, gradient refinement); unreachable targets return best effort + `reached=False`; dyad lookup exact |
| R6 | Softmax underflow/NaN for distant targets | Medium | Log-sum-exp; frozen stability test |
| R7 | Mode collapse: repetitive output that satisfies c* (e.g., stacking one interval) | High | Novelty penalty + diversity metrics in S9; sequential-consonance terms |
| R8 | Correctness vs published `incon` implementation unproven (G3) | Medium | Separate follow-up protocol run on a host with R to add golden-value tests (requires Reset/new freeze) |
| R9 | Licensing if `incon` code is reused | Medium | Clean-room reimplementation from papers; S0 records license |
| R10 | Real-time use: model evaluation too slow for an audio thread | Medium | Precompute tables/level sets off-thread; perf budget |
| R11 | Checkpoint corruption/half-write | Medium | Atomic replace + .bak + versioning (frozen tests) |
| R12 | Test tampering by implementing agent | Medium | `sha256sum -c` in CI gate |
| R-META | Pre-mortem authored at Sonnet tier only | High | Mythos/Fable review required at GATE before acceptance |

### Round 2 — re-examine after controls
- R1: residual because controls reduce but do not eliminate perceptual mismatch -> reclassified Medium (documented domain warning + labelling; listening protocol quantifies error).
- R5: new sub-risk — Langevin/gradient route not differentiable through familiarity -> control: gradient route uses interference+harmonicity only; familiarity handled by discrete grid. Medium.
- R7: diversity metric threshold unspecified -> S6 design note must fix numeric thresholds before S7; GATE checks. Medium.
- R2, R3, R4: controls testable/gated -> Medium (R3 stays gated by S0; if S0 finds a contradiction the run halts).
- R-META: control is procedural (human/higher-tier review) -> Medium pending GATE.

### Round 3 — re-examine
No new critical/high vectors found. Highest residual severity: Medium.
**Result: 0 critical / 0 high after Round 3, conditional on (a) S0 not contradicting frozen tests and (b) GATE review by Mythos/Fable.** These two conditions are stated dependencies, not solved risks.

## Known limitations (honest)
- Sampler design is this plan's proposal (G2), not a published method.
- Tests are RED by design; the perf budget (2 s/step) and R7–R9 constants are unvalidated until S0/S2.
- Cross-validation against `incon` is out of scope for this run (R8).

## PUSH STATUS (unchanged: still local-only; hand-off via git bundle + tarball)
GitHub push NOT performed: no credentials, no configured remote, and no target repository were available in this environment (unauthenticated api.github.com request returned HTTP 403). Commit is local only; a git bundle accompanies it.
