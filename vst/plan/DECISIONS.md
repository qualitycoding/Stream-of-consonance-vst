# DECISIONS

Decision records and the if→then rules the implementer applies without asking.

## D-001 — Pin JUCE 8.0.15, not JUCE 9
JUCE 9.0.0 (2026-07-21) through 9.0.2 (2026-09-07) exist, but 9.0.0 carries 35+ breaking changes
including a restructuring of the VST3 client extension API (`VST3ClientExtensions` split into
`VST3Interface` plus a `JUCE_VST3_COMPATIBLE_CLASSES` define). The user's existing JUCE projects
are on the 8 line. Pin **8.0.15**, the last 8.x tag.
*Rule:* if 8.0.15 is unavailable, use the highest 8.0.x tag available and log it. Never silently
upgrade to 9.x; that is a scope change requiring a new Phase 0.

## D-002 — Generation runs on its own thread, never on the audio thread
SPIKE-01 measured 612 ms/note in free 1-cent mode and 12 ms/note in standard mode in Python. Even
a 20× C++ speedup leaves free mode around 30 ms/note, which is an eternity in an audio callback.
Architecture: background generator thread + lock-free lookahead queue; audio thread synthesises
only.
*Resolution ladder rule:* if the generator cannot keep ahead, step free-mode resolution 1 → 2 → 5
cents, then raise lookahead 2 → 4, logging each step. Never move generation onto the audio thread,
and never relax T-013.

## D-003 — The timbre is fixed and shared
`CompositeModel` is fitted to 11 harmonics at 1/h, and `render.py` guards against a synthesis
timbre differing from the scoring timbre. The plugin exposes no timbre control, and the synth
asserts its timbre equals the scorer's. `familiarity_mode` is always `drop`, so microtonal chords
fall back to the neutral log-probability rather than raising.
*Rule:* any request for user timbres is out of scope and requires re-running Phase 0, because it
invalidates every fixture.

## D-004 — Harmonicity uses the rotation identity
On a 1-cent grid with 1200 bins, every candidate's pitch-class spectrum is an exact circular shift
of one precomputed single-note spectrum. SPIKE-02 verified this to 1.665e-15 and measured 6.8×
in numpy alone. The C++ port precomputes the note spectrum and the template FFT once per scorer.
*Rule:* the identity needs integer-cent candidates. For non-integer sets (the JI lattice), use the
literal path. Correctness before speed.

## D-005 — Bit-identical streams require numpy's PCG64
The sampler draws from `numpy.random.default_rng`. To reproduce streams exactly, the C++ port
implements PCG64 (XSL-RR 128/64) and numpy's double conversion `(raw >> 11) * 2^-53`.
*Fallback rule:* numpy's `SeedSequence` is the fiddly part. `tests/fixtures/rng.json` records the
initial 128-bit state and increment for seven seeds, so `Pcg64::fromState` needs no SeedSequence
at all. If `fromNumpySeed` cannot be made to agree, restrict the seed parameter to those seven
values and construct from state. Log it; do not weaken T-010.

## D-006 — MPE member bend range is ±2 semitones, set explicitly by RPN
The plugin only ever bends by the offset from the nearest 12-TET note, i.e. at most 50 cents.
±2 semitones over 14 bits gives 0.0244 cents per step; ±48 semitones would give 0.586 cents and
would fail T-012's 0.05-cent budget. The plugin sends the MPE zone RPN 6 and the bend-range
RPN 0,0 on every `prepareToPlay`.
*Rule:* if the host ignores the RPN, surface a Bend Range control and log it. Do not change the
default silently — every recorded bend value depends on it.

## D-007 — Both start parameters always exist
VST3 does not permit changing the parameter list after instantiation, and removing a parameter
orphans saved automation lanes. `Start Note` and `Start Frequency` are both always present and
both automatable; the Pitch Mode switch decides which one is *read*, and the editor greys the other.

## D-008 — The Python package is the oracle and stays frozen
`tests/` at the repository root remains frozen and is the reference implementation. The VST work
lives entirely under `vst/` so that the Python project's own frozen manifest, PLAN.md and
checkpoints are untouched. Fixtures under `vst/tests/fixtures/` are generated from the Python
package and are themselves frozen.
*Rule:* if a fixture appears wrong, that is a Test Challenge (see `vst/tests/FROZEN.md`), not an
edit. Regenerating fixtures is changing the specification.

## D-009 — Consonance parameter range narrowed to −0.7 … 2.2, not the full regression range
A-004 originally set the Consonance control to the composite model's full published regression
range, −0.7 … 3.1. That range describes scores across *all* chord sizes; it is not what a 4-note
window (A-006's default) can actually reach. The knowledge store loaded while adopting the
lessons & knowledge addendum (`K-20261004T102022Z-composite-score-attainable-range`, from the
original consonance-model research run) measured the attainable range directly: 1500 random
4-note chords under the same timbre and weights gave median/p95/max scores of 0.81/1.29/2.02, and
a calibration run targeting 2.4 "collapsed onto 3-4 repeated pitch classes" and only reached
tolerance 76% of the time. The sampler is directed (weighted toward the target), not pure random
search, so it reaches somewhat higher than random search alone -- but not past where the
candidate set simply has no chord close enough to the target to select. −0.7 … 2.2 keeps the top
of the range inside what a 4-note window can plausibly reach without the collapse behaviour the
knowledge item documents; this still needs verification in S-016's soak test once the real
instrument exists. This directly sharpens R-012 (saturation near the range's ends), which named
the risk without quantifying it.
*Rule:* if S-016's soak test shows the sampler still saturating well inside 2.2, apply the same
default decision rule as D-002's resolution ladder: narrow the range further and log it, rather
than relaxing any test.

## Parameters (normative)

| Parameter | Type | Range / values | Default | Automatable | Notes |
|---|---|---|---|---|---|
| `pitchMode` | Choice | `Note`, `Frequency` | `Note` | yes | Selects start units *and* candidate set (A-002) |
| `startNote` | Int | 0–127 | 57 (A3 = 220 Hz) | yes | Read at stream start only (A-003) |
| `startFreq` | Float | 20–5000 Hz, exponential skew | 220.0 | yes | Read at stream start only |
| `consonance` | Float | −0.7 … 2.2 | 1.6 | yes | Latched per note at generation time (A-005); range narrowed from the full regression range by D-009 |
| `sigma` | Float | 0.02 … 1.0 | 0.1 | yes | Tightness of the level set (A-009) |
| `rate` | Choice | 1/1 … 1/16 | 1/4 | yes | Tempo-synced (A-006) |
| `seed` | Int | 0–9999 | 7 | **no** | Saved with the preset (A-007) |
| `restart` | Button | — | — | no | Applies pending start value immediately |
