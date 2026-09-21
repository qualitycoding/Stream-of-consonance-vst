# HANDOFF — Stream-of-Consonance VST3/MPE instrument

You are the implementing agent. You have this branch and nothing else: no access to the planner,
the human, or the conversation that produced this. Everything you need is here. If you find
something that is genuinely not here, that is a defect in this plan — follow the halt protocol
at the bottom rather than guessing.

**Status: READY.** 0 Critical and 0 High risks outstanding. No human sign-off required.

## What you are building

A Windows VST3 instrument that continuously generates a stream of tones whose sounding sonority
tracks an automatable target consonance. The user sets the stream's starting pitch either as a
MIDI note or as a frequency in Hz, chosen by a Note/Frequency switch that **also** selects
whether candidate pitches are 12-TET notes or any frequency on a 1-cent grid. The plugin
synthesises the stream itself and simultaneously emits it as MPE MIDI.

The consonance model already exists and is correct: it is the Python package in this repository's
root, frozen, and it is your oracle. Your job is a faithful C++ port plus the plugin around it.

## Reading order

1. This file.
2. `plan/ASSUMPTIONS.md` — what was decided for you and why. A-001 … A-010.
3. `plan/DECISIONS.md` — the binding decisions and the if→then rules. Read D-002 and D-005 before
   writing any code; they shape the architecture.
4. `plan/ENVIRONMENT.md` — pinned versions and the setup commands to run first.
5. `plan/PLAN.md` — the 18 steps. Execute them in order.
6. `premortem/RISK_REGISTER.md` — what is expected to go wrong. Skim it now, re-read when
   something does.
7. `research/claims.json` and `research/rounds/round-2.md` — only if you want to know why a
   decision was made, or if you are about to contradict one.

## The three things most likely to bite you

1. **Two reference pitches coexist.** `composite.py` defines `REF_HZ` = C4 = 261.6255653005986 Hz;
   that constant fixes the pitch-class origin inside the harmonicity term *only*. Every `cents`
   value in every fixture is relative to **220 Hz**, declared as `ref_hz` in each fixture file.
   Using C4 instead does not raise — it silently shifts the roughness term by up to 0.082 score
   units. This is R-001, and it is the reason T-000 exists.
2. **Generation cannot run on the audio thread.** Measured at 612 ms per note in free 1-cent mode
   in Python. Background thread plus lookahead queue, always. See D-002.
3. **Streams must be bit-identical to Python**, which means implementing numpy's PCG64. There is
   a documented fallback if numpy's `SeedSequence` defeats you — see D-005. Take the fallback
   rather than weakening T-010.

## Environment setup

Run everything in `plan/ENVIRONMENT.md` §Setup verbatim and record the output. Do not skip the
step that runs the *Python* test suite: the oracle must be green before you trust a single fixture.

## Running the tests

The core suite is deliberately JUCE-free and CMake-free, so you can run it before any plugin
scaffolding exists:

```
make -C vst/tests/cpp red                                   # against the stub: must FAIL
make -C vst/tests/cpp IMPL=../../src/soc_core.cpp run       # against your port: must PASS
```

`make red` is the recorded red state and is how you confirm the harness still works. The expected
red output is `research/spikes/spike_03_red_verify_output.txt`: 1 of 15 tests passing (T-000, the
fixture-integrity test) and 14 failing with not-implemented errors.

## Verifying the freeze

```
sh vst/tests/verify_frozen.sh
```

`tests/cpp/test_core.cpp`, everything in `tests/fixtures/`, and `src/soc_core.h` are frozen. You
may not modify, skip, weaken, or regenerate any of them. `src/soc_core.h` is frozen because it is
the contract: implement `soc_core.cpp` against it, do not change signatures. See `tests/FROZEN.md`.

## Steps at a glance

| Step | What | Gate |
|---|---|---|
| S-001 | Verify inherited freezes and the Python oracle | both verify scripts + 59 pytest |
| S-002 | Pin and verify the build environment | JUCE 8.0.15 SHA recorded |
| S-003 | PCG64 | T-010 |
| S-004 | Timbre, roughness, familiarity | T-001, T-002, T-004, T-005, T-007 |
| S-005 | Harmonicity (literal, then rotation) | T-003 |
| S-006 | Composite + CandidateScorer; drop the stub | T-006, T-009, T-013, T-014 |
| S-007 | Pitch sets | T-008 |
| S-008 | Sampler and stream generator | T-011 |
| S-009 | JUCE plugin skeleton and parameters | Standalone builds; params visible in Live |
| S-010 | Generator thread and lookahead queue | T-019 |
| S-011 | Additive synth voice | correlation >0.99 with the reference render |
| S-012 | MPE output | T-012, T-016 |
| S-013 | Transport sync and determinism | T-018 |
| S-014 | Editor | T-017 |
| S-015 | pluginval and Ableton validation | T-020 |
| S-016 | Performance and soak | zero underruns over 30 min |
| S-017 | Re-freeze and release build | manifest unchanged, 15/15 core tests |
| S-018 | Documentation | — |

## Halt and deviation protocol

**Default rule.** For anything not covered by a step's `On failure`: take the most reversible
option that does not expand scope, log it in `vst/DEVIATIONS.md` with your rationale, and carry
on — **unless** it touches a frozen test, the model's numerical behaviour, or a public interface
in `soc_core.h`.

**Halt** and write `vst/BLOCKED.md` if it does touch one of those, or if the Python oracle fails
at S-001.

**Test Challenge.** If you conclude a frozen test or fixture is genuinely invalid, stop and write
`vst/TEST_CHALLENGE.md` with the ID, your evidence, and a proposed fix. Do not edit the test.
A failing test is ordinarily evidence of an incomplete implementation, not an invalid test.

## Known gaps, stated plainly

* Plugin-level tests T-015 … T-020 are specified but were never red-verified, because JUCE could
  not be installed in the planning environment. S-009 requires you to red-verify them before
  implementing them. This is R-005.
* C-015 (that Ableton honours MPE zone configuration from a plugin's MIDI output) is
  single-source and could not be tested without a running Live. S-012 carries an explicit rule
  for what to do if it turns out false. This is R-006.
* The timings in C-012 were measured on the planning sandbox, not your machine. The conclusion
  they support (generation off the audio thread) is robust to that; the specific 40 ms budget in
  T-013 may need the D-002 resolution ladder on slower hardware.
