# PLAN — Stream-of-Consonance VST3/MPE instrument

**STATUS: READY**

| Metric | Count |
|---|---|
| Claims: verified | 11 |
| Claims: corroborated | 3 |
| Claims: single-source | 1 (C-015, Medium risk R-006) |
| Claims: inferred | 0 |
| Frozen tests (core, red-verified) | 15 (T-000 … T-014) |
| Frozen tests (plugin, specified, not red-verified) | 6 (T-015 … T-020) — see R-005 |
| Plan steps | 18 |
| Risks: Critical / High / Medium / Low | 0 / 0 / 5 / 4 |

Read `../HANDOFF.md` first. This file assumes you have.

---

## Goal

Package the `consonance` Python model (this repository, `main`) as a Windows VST3 instrument
that continuously generates a stream of tones whose sounding sonority tracks an automatable
target consonance, starting from a pitch the user specifies either as a note or as a frequency,
and that also emits the stream as MPE MIDI.

## In scope

* A C++17 port of the composite model and the conditional sampler, byte-verified against the
  Python oracle.
* A JUCE VST3 + Standalone instrument with a built-in additive synth matching the model's timbre.
* MPE MIDI output of the same stream.
* Host-automatable parameters: **Start Note / Start Frequency**, **Consonance**, **Sigma**.
* Windows x64, Ableton Live 12.

## Out of scope

* macOS, AU, LV2, AAX, VST2, Linux. (`JUCE_VST3_CAN_REPLACE_VST2=0`; see A-008.)
* Changing the consonance model itself, its coefficients, or its calibration.
* Audio input processing, MIDI input note handling, or user-supplied timbres (D-003).
* Re-validating the model perceptually. `docs/LISTENING_PROTOCOL.md` remains future work.

## Success criteria

| ID | Criterion | Measured by |
|---|---|---|
| SC-1 | The C++ core reproduces every Python oracle value to ≤1e-9 absolute | T-001…T-007, T-009, T-014 |
| SC-2 | Both pitch modes are reachable; one switch selects both the start-value units and the candidate set | T-008, T-017 |
| SC-3 | Free 1-cent generation stays ahead of the note clock at 120 BPM ¼-notes with no dropout over 30 min | T-013, T-019 |
| SC-4 | Same seed + same automation ⇒ bit-identical note sequence; two bounces are sample-identical | T-010, T-011, T-018 |
| SC-5 | Start and Consonance are automatable in Ableton; MPE output matches internal pitch to ≤0.05 cents | T-012, T-015, T-016 |
| SC-6 | Builds Release x64 and passes `pluginval --strictness-level 10`; loads in Live 12 | T-020 |

## Constraints

C++17, JUCE 8.0.15 (D-001), MSVC 19.4x, CMake ≥3.22 + Ninja, Windows 10/11 x64, Apache-2.0
(inherited; JUCE AGPLv3-or-commercial applies to distribution — see A-010 and R-007).

---

## Step template key

Every step below is literal. `Done when` names the frozen test IDs that must pass. Do not
proceed past a step whose `Done when` is unmet; follow `On failure` instead.

---

### S-001 Verify the inherited artifacts before touching anything
- Tier: Haiku
- Depends on: none
- Inputs: `vst/tests/fixtures/`, `vst/tests/FROZEN_MANIFEST.sha256`, `tests/FROZEN.sha256`
- Actions:
  1. `cd <repo root>`
  2. `sh vst/tests/verify_frozen.sh` — verifies the VST freeze manifest.
  3. `sh scripts/verify_frozen.sh && python -m pytest` — verifies the *Python* project is
     still green, because it is the oracle. 59 tests must pass.
  4. Record both outputs in `vst/.checkpoints/state.json` under `completed`.
- Outputs: updated `vst/.checkpoints/state.json`
- Done when: both verification scripts exit 0 and pytest reports 59 passed.
- Checkpoint: `phase: "implementation", subphase: "S-001"`, artifact hashes re-verified.
- On failure: if the Python suite fails, **halt and write `BLOCKED.md`** — the oracle is not
  trustworthy and every fixture downstream is suspect. Do not regenerate fixtures to make it pass.
- Relevant: D-008, C-009

### S-002 Pin and verify the build environment
- Tier: Sonnet
- Depends on: S-001
- Inputs: `vst/plan/ENVIRONMENT.md`
- Actions: execute every command in `ENVIRONMENT.md` §Setup verbatim, in the x64 Native Tools
  Command Prompt, and paste each command's output into `vst/.checkpoints/env_verification.txt`.
- Outputs: `vst/.checkpoints/env_verification.txt`
- Done when: `cmake --version` ≥ 3.22, `ninja --version` succeeds, JUCE at the pinned tag,
  and the JUCE `AudioPluginHost` example builds.
- Checkpoint: record the exact JUCE commit SHA.
- On failure: if the JUCE tag is unavailable, use the newest 8.0.x tag ≤8.0.15 and log it in
  `DEVIATIONS.md`. **Do not** move to JUCE 9 — see D-001 and R-003.
- Relevant: D-001, C-013, C-014

### S-003 Implement PCG64
- Tier: Sonnet
- Depends on: S-002
- Inputs: `vst/src/soc_core.h`, `vst/tests/fixtures/rng.json`
- Actions:
  1. Create `vst/src/soc_core.cpp`. Implement `Pcg64::fromState`, `nextUint64`, `nextDouble`.
     Multiplier `0x2360ED051FC65DA44385DF649FCCF645`, XSL-RR 128→64 output, advance
     `state = state * mult + inc`. `nextDouble()` is `(raw >> 11) * 0x1p-53`.
  2. Implement `Pcg64::fromNumpySeed` by reproducing numpy's `SeedSequence` entropy pool.
  3. Build and run `make -C vst/tests/cpp IMPL=../../src/soc_core.cpp run`.
- Outputs: `vst/src/soc_core.cpp` (partial)
- Done when: **T-010 passes** with tolerance 0.0 (exact equality) for all 7 fixture seeds.
- Checkpoint: `"T-010": "pass"`.
- On failure: if `fromNumpySeed` cannot be made to agree, apply D-005's fallback — restrict the
  plugin's seed parameter to the seeds in `rng.json` and construct via `fromState`. Log in
  `DEVIATIONS.md`. This is explicitly permitted and does **not** require a `BLOCKED.md`.
- Relevant: D-005, C-008

### S-004 Implement timbre, interference and familiarity
- Tier: Sonnet
- Depends on: S-003
- Inputs: `consonance/timbre.py`, `consonance/interference.py`, `consonance/familiarity.py`,
  `consonance/data/billboard_pc_chord_type_counts.json`
- Actions:
  1. Implement `harmonicTimbre`, `hutchinsonRoughness`, `familiarityLogP`, `neutralLogProb`.
  2. Embed the Billboard counts. Convert the JSON to a `constexpr` array with
     `python vst/tools/embed_counts.py > vst/src/soc_billboard.inc` (write this tool; it must be
     deterministic and its output committed).
  3. Reproduce `chord_type_from_cents` exactly, including that the interval test is
     `abs(rel - 100*round(rel/100)) > 20.0` — strictly greater, so 20.0 cents is *inside*.
  4. Validate all frequencies: empty, non-positive or non-finite input throws.
- Outputs: `vst/src/soc_core.cpp`, `vst/src/soc_billboard.inc`, `vst/tools/embed_counts.py`
- Done when: **T-001, T-002, T-004, T-005, T-007 pass.**
- Checkpoint: record the sha256 of `soc_billboard.inc`.
- On failure: if roughness disagrees, check the Hutchinson cut-off (`y > 1.2` ⇒ 0) and the
  normalisation by `sum(A²)` before suspecting the pair loop.
- Relevant: C-002, C-004, R-008

### S-005 Implement harmonicity with the rotation optimisation
- Tier: Opus
- Depends on: S-004
- Inputs: `consonance/harmonicity.py`, `vst/research/spikes/spike_02_rotation.py`
- Actions:
  1. Implement `harmonicityBits` as the literal translation first — Gaussian-smoothed circular
     spectrum on a 1200-bin grid, σ=6.83 cents, ρ=0.75, cosine-similarity sweep, KL from uniform
     in bits.
  2. Verify T-003 against the literal version **before** optimising.
  3. Then add the rotation path used by `CandidateScorer`: precompute the single-note spectrum
     once, and obtain each candidate's spectrum by circular index shift (SPIKE-02 proves this is
     exact to 1.7e-15). Precompute the template's real FFT once per scorer.
  4. Re-run T-003. The literal and rotated paths must agree to 1e-12.
- Outputs: `vst/src/soc_core.cpp`
- Done when: **T-003 passes** for both paths.
- Checkpoint: `"harmonicity": "literal+rotated agree"`.
- On failure: the rotation identity requires integer-cent candidates. If a pitch set produces
  non-integer cents (JI lattice), fall back to the literal path for that scorer — correctness
  before speed. Log in `DEVIATIONS.md`.
- Relevant: D-004, C-006, R-002

### S-006 Implement the composite score and CandidateScorer
- Tier: Opus
- Depends on: S-005
- Inputs: `consonance/composite.py`
- Actions:
  1. Implement `compositeScore` with the `Weights` defaults already in `soc_core.h`.
  2. Implement `CandidateScorer`: held partials computed once, candidate partials broadcast,
     roughness over the combined partial set, harmonicity via the rotation path, familiarity per
     candidate, then the weighted sum. `familiarity_mode` is always `drop` (D-003).
  3. Delete `vst/src/soc_core_stub.cpp` from the build. Keep the file; it is the red-state
     reference and is referenced by `tests/cpp/Makefile`.
  4. Preallocate every buffer in the constructor. `score()` must not allocate.
- Outputs: `vst/src/soc_core.cpp`
- Done when: **T-006, T-009, T-013, T-014 pass.** T-013 must print a measured time under 40 ms.
- Checkpoint: record the T-013 measured ms.
- On failure: if T-013 exceeds 40 ms, do **not** relax the test. Apply D-002's resolution ladder:
  drop free mode's default resolution to 2 cents, then 5 cents, logging the change in
  `DEVIATIONS.md` and surfacing it as a user-visible Resolution control. The budget is
  load-bearing for SC-3.
- Relevant: D-002, D-004, C-005, C-012

### S-007 Implement pitch sets
- Tier: Haiku
- Depends on: S-006
- Inputs: `consonance/pitchset.py`
- Actions: implement `candidateCents` for Standard (step 1200/edo) and Free (uniform step, or
  `snapTo` repeated per octave and clipped to range). Populate `kJustIntervalsCents` from the
  12 ratios in `pitchset.py`.
- Outputs: `vst/src/soc_core.cpp`
- Done when: **T-008 passes** for all six fixture pitch sets.
- On failure: check `ceil`/`floor` on the range endpoints — the Python uses
  `first = ceil((low - offset)/step)`, `last = floor((high - offset)/step)`, inclusive.
- Relevant: C-007

### S-008 Implement the sampler and stream generator
- Tier: Opus
- Depends on: S-007
- Inputs: `consonance/sampler.py`
- Actions:
  1. Implement `sampleNext`: log-weights `-0.5*((v - target)/sigma)²`, plus the novelty log-prior,
     with excluded candidates set to `-inf`, log-sum-exp stabilised by subtracting the max finite
     weight, then inverse-CDF selection with `searchsorted(cdf, rng.random()*cdf[-1], side="right")`
     clamped to the last index.
  2. Implement `generateStream`: sliding state of the last `window - 1` notes including `start`,
     min-separation exclusion, novelty prior over the last 8 notes by pitch class within 25 cents.
  3. The order of RNG draws must match Python exactly — one `random()` per note, drawn after the
     weights are built. Any extra draw desynchronises every subsequent note.
- Outputs: `vst/src/soc_core.cpp`
- Done when: **T-011 passes** — all 5 fixture streams reproduce exactly, notes and realised scores.
- Checkpoint: `"T-011": "pass"`, note the first 4 notes of `standard_t1.6_seed7` (500, 1000, 0, -200).
- On failure: if notes diverge only after note *k*, the RNG is desynchronised, not the scoring —
  compare the candidate weight vector at step *k-1* against a Python dump before touching the model.
- Relevant: D-005, C-009

### S-009 JUCE plugin skeleton and parameters
- Tier: Sonnet
- Depends on: S-008
- Inputs: `vst/plan/ENVIRONMENT.md`, `vst/plan/DECISIONS.md` §Parameters
- Actions:
  1. Create `vst/CMakeLists.txt` using `juce_add_plugin` with
     `FORMATS VST3 Standalone`, `IS_SYNTH TRUE`, `NEEDS_MIDI_INPUT FALSE`,
     `NEEDS_MIDI_OUTPUT TRUE`, `IS_MIDI_EFFECT FALSE`.
  2. Set `add_compile_definitions(JUCE_VST3_CAN_REPLACE_VST2=0)` at directory scope **before**
     `add_subdirectory(${JUCE_PATH})`, or the Standalone target will not pick it up.
  3. Declare parameters exactly as in DECISIONS.md §Parameters, using `AudioProcessorValueTreeState`.
  4. `Pitch Mode` is an `AudioParameterChoice` with `{"Note", "Frequency"}`.
  5. `Start Note` and `Start Frequency` are **both** always present and both automatable; the
     inactive one is greyed in the editor but never removed — VST3 forbids changing the parameter
     list after instantiation, and removing it would break saved automation lanes (R-004).
- Outputs: `vst/CMakeLists.txt`, `vst/src/PluginProcessor.{h,cpp}`
- Done when: the Standalone target builds and launches; `Consonance`, `Start Note`,
  `Start Frequency` and `Sigma` appear in Ableton's automation lane list.
- Checkpoint: record the built VST3 path and its size.
- On failure: VST3 install permission errors → set `VST3_COPY_DIR` to
  `$ENV{LOCALAPPDATA}/Programs/Common/VST3` rather than running elevated.
- Relevant: D-006, D-007, C-014, R-004

### S-010 Generator thread and lookahead queue
- Tier: Opus
- Depends on: S-009
- Inputs: `vst/src/soc_core.h`
- Actions:
  1. One `juce::Thread` owning the `CandidateScorer` and `Pcg64`. It never touches the audio
     thread's state directly.
  2. A single-producer/single-consumer lock-free ring of `GeneratedNote { double cents; double
     targetAtGeneration; int64 sequenceIndex; }`, capacity 8, using `juce::AbstractFifo`.
  3. The audio thread pops notes; it must never block, allocate, or call `score()`.
  4. Lookahead depth 2 (A-005): the generator keeps 2 notes queued ahead of the sounding note.
  5. The consonance target is latched from the parameter at the instant generation of a note
     begins, and stored in `targetAtGeneration` for the determinism check in T-018.
  6. If the queue underruns, the audio thread repeats the last sounding note at reduced gain
     rather than going silent, and sets an atomic underrun counter surfaced in the editor.
- Outputs: `vst/src/GeneratorThread.{h,cpp}`
- Done when: **T-019 passes** (30-minute soak, zero underruns at 120 BPM ¼-notes, free 1-cent).
- Checkpoint: record underrun count and max queue latency.
- On failure: underruns ⇒ apply the D-002 resolution ladder, then raise lookahead to 4. Do not
  move generation onto the audio thread under any circumstances.
- Relevant: D-002, C-012, R-002

### S-011 Additive synth voice
- Tier: Sonnet
- Depends on: S-010
- Inputs: `consonance/render.py`, `vst/tests/fixtures/timbre.json`
- Actions: implement a polyphonic additive voice using the **same** `Timbre` the scorer uses —
  11 partials at 1/h, partials above 20 kHz muted, 20 ms linear attack and 250 ms linear release,
  `window` (4) notes sounding at once. Assert at construction that the synth timbre equals the
  scorer timbre (the C++ equivalent of `CompositeModel.check_timbre`).
- Outputs: `vst/src/SynthVoice.{h,cpp}`
- Done when: the Standalone produces audio; offline render of `standard_t1.6_seed7` correlates
  >0.99 with `examples/out/standard_target_1.6.wav` after level normalisation.
- On failure: a correlation dip at note boundaries indicates the envelope, not the pitch.
- Relevant: D-003, C-001, R-009

### S-012 MPE output
- Tier: Sonnet
- Depends on: S-011
- Inputs: `vst/tests/fixtures/mpe.json`
- Actions:
  1. On `prepareToPlay`, emit the MPE lower-zone configuration (RPN 6 on channel 1 with member
     channel count 15) and set the member pitch-bend range to **±2 semitones** via RPN 0,0.
  2. Allocate member channels 2–16 round-robin, one note per channel, never reusing a channel
     while its note sounds.
  3. Encode each note as nearest 12-TET note plus 14-bit bend (`encodeMpe`).
  4. In Standard mode the bend is always exactly 8192 — assert this.
- Outputs: `vst/src/MpeOutput.{h,cpp}`
- Done when: **T-012, T-016 pass.**
- Checkpoint: record the RPN byte sequence actually emitted.
- On failure: if Live ignores the bend range RPN, do **not** switch to ±48 semitones silently —
  that changes resolution by 24× and every recorded bend value. Log it, surface a Bend Range
  control, and keep ±2 the default. See R-006.
- Relevant: D-006, C-010, C-011, R-006

### S-013 Transport sync and determinism
- Tier: Opus
- Depends on: S-012
- Inputs: `vst/src/GeneratorThread.h`
- Actions:
  1. Derive the note clock from `AudioPlayHead::PositionInfo` ppq position, not from an
     accumulating sample counter, so looping and locating are handled.
  2. On transport start or locate-to-zero, reset the RNG from the seed parameter and clear the
     queue — this is what makes a bounce repeatable (A-007).
  3. The `Start Note`/`Start Frequency` value is read **at stream start only** (A-003); changes
     mid-stream are latched for the next restart and shown as "pending" in the editor.
- Outputs: `vst/src/PluginProcessor.cpp`
- Done when: **T-018 passes** — two consecutive offline bounces of the same 60-second arrangement
  with identical automation are sample-identical.
- On failure: non-identical bounces almost always mean the note clock drifted from ppq, or the
  RNG was not reset at transport start.
- Relevant: D-005, A-003, A-007, R-010

### S-014 Editor
- Tier: Sonnet
- Depends on: S-013
- Inputs: none beyond the processor
- Actions: a minimal editor — the Note/Frequency switch, the start control (note name or Hz
  readout depending on mode), Consonance, Sigma, a Restart button, a readout of the realised
  consonance of the sounding window, and the underrun counter. Attach every control through
  `AudioProcessorValueTreeState::SliderAttachment` etc. so automation and UI cannot diverge.
- Outputs: `vst/src/PluginEditor.{h,cpp}`
- Done when: **T-017 passes** (switching mode changes both the start units and the candidate set);
  the realised-consonance readout tracks the target within ±0.25 in steady state.
- On failure: a control that updates the UI but not the parameter (or vice versa) means a raw
  listener was used instead of an attachment.
- Relevant: SC-2, A-002

### S-015 Host validation
- Tier: Haiku
- Depends on: S-014
- Actions:
  1. `pluginval --strictness-level 10 --validate <path to VST3>`
  2. Load in Ableton Live 12: instantiate, record automation for Consonance, bounce, reload the
     set, confirm parameter values and automation survive a save/reload cycle.
  3. Route the MPE output to a second track with an MPE-capable instrument and confirm pitches.
- Outputs: `vst/.checkpoints/pluginval_output.txt`
- Done when: **T-020 passes** — pluginval exits 0 at strictness 10.
- On failure: pluginval parameter-thread warnings usually mean a parameter is read on the audio
  thread without an atomic. Fix the plugin, never the validator's settings.
- Relevant: C-015, R-004, R-006

### S-016 Performance and soak
- Tier: Sonnet
- Depends on: S-015
- Actions: run T-019 for 30 minutes at 120 BPM in free 1-cent mode with Consonance automated as
  a 0.05 Hz triangle across its full range; record CPU, underruns, and queue depth every 10 s.
- Outputs: `vst/.checkpoints/soak_log.csv`
- Done when: zero underruns, generator CPU below 25% of one core.
- On failure: D-002 resolution ladder.
- Relevant: C-012, R-002

### S-017 Re-freeze and release build
- Tier: Haiku
- Depends on: S-016
- Actions:
  1. `sh vst/tests/verify_frozen.sh` — must still pass; no frozen file may have changed.
  2. Build Release x64 with `-DCMAKE_BUILD_TYPE=Release` **explicitly set**.
  3. Re-run the full core suite against the release build.
- Done when: freeze verification passes and all 15 core tests pass.
- On failure: a changed manifest hash means the immutability rule was broken — stop and write
  `TEST_CHALLENGE.md`.
- Relevant: D-008

### S-018 Documentation
- Tier: Sonnet
- Depends on: S-017
- Actions: write `vst/README.md` covering install, the two pitch modes, what the Consonance
  parameter means (including that it is *model* consonance fitted to Western listeners' ratings
  of 12-TET chords, per the root README's caveat), the automation latency of 2 notes, and the
  MPE routing recipe for Live. Update `NOTICE` if any new third-party code was vendored
  (nlohmann/json is already vendored under `vst/third_party/`, MIT).
- Done when: a reader who has never seen the project can install it and get sound.
- Relevant: A-010, R-007

---

## Default decision rule

For any situation not covered above: choose the most reversible option that does not expand
scope, log it in `vst/DEVIATIONS.md` with the rationale, and continue — **unless** it touches a
frozen test, the consonance model's numerical behaviour, or a public interface in `soc_core.h`,
in which case halt and write `vst/BLOCKED.md`.
