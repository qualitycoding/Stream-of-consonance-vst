# Stream-of-consonance-vst

A planned Windows VST3 instrument that plays a continuous stream of tones whose sonority follows an
automatable target consonance, and also sends the stream out as MPE MIDI. The starting pitch is a MIDI note or a
frequency in Hz, chosen with a Note/Frequency switch that also decides whether candidate pitches are 12-TET notes
or any frequency on a 1-cent grid.

> **Status: the C++ model port is partly done; there is no plugin yet.** The repository has two parts:
>
> 1. **The Python model** (`consonance/`, at the repository root). This is the reference the port is checked
>    against. It is working and its 59 tests pass. It is described below, and it is the same code as
>    [Stream-of-consonance](https://github.com/qualitycoding/Stream-of-consonance).
> 2. **The C++ port** (`vst/`). `vst/src/soc_core.cpp` ports the model, and `vst/tests/` holds golden fixtures
>    and core tests. There is no JUCE plugin code, no audio output and no MPE output yet (`vst/plan/PLAN.md` has 18
>    steps; the plugin steps are not done).

## Where the port stands

I built the core tests in a scratch directory and ran them against `soc_core.cpp`:

- **13 of 15 core tests pass.**
- **T-011 fails** for one of five fixture streams (`free5_t1.6_seed7`): the C++ stream diverges from the
  Python one from its second note. The reasons are written up in `vst/TEST_CHALLENGE.md`.
- **T-013 fails** on speed: scoring 2,401 free-mode candidates took about 59 ms on the machine I used, against a
  40 ms budget. Timing depends on the machine.
- The 6 plugin-level tests (T-015 to T-020) are specified but not yet runnable.
- The blind listening gate (`GATE-G-LISTEN.LISTENING.md`) is blocked: nothing has been rendered or scored.

To run the core tests (needs a C++17 compiler; the golden fixtures are committed in `vst/tests/fixtures/`):

```bash
cd vst/tests/cpp && make IMPL=../../src/soc_core.cpp run
```

Without `IMPL=...` the suite builds against a stub and every test is expected to fail. The fixtures were made from the
Python model by `vst/tests/make_fixtures.py`; regenerating them counts as changing the specification
(`vst/tests/FROZEN.md`).

The plan, research, risk register and reviews are under `vst/` (start with `vst/HANDOFF.md`).

# The Python model (`consonance`)

Reversible consonance model & consonance-targeted tone streams (Python package `consonance`).

Scores chords with the Harrison & Pearce (2020) composite model (Hutchinson-Knopoff roughness + pitch-class harmonicity
+ corpus familiarity) and *inverts* it by conditional sampling: given a target consonance c*, pick each new tone so the
sounding sonority stays near c*.

```python
from consonance.generator import ToneStreamGenerator

g = ToneStreamGenerator(pitch_mode="standard")     # 1 — only standard notes (A, C#, ...)
g = ToneStreamGenerator(pitch_mode="free")         # 2 — any frequency that fits (JI, microtonal, 1-cent grid)
res, scores = g.generate(target=1.6, n_steps=24, seed=7, start=(0.0, 700.0))
notes_hz = g.hz(res.notes)
```

### Pitch mode (the switch)
| `pitch_mode` | what it allows | tuning knobs |
|---|---|---|
| `"standard"` | only equal-tempered scale notes | `edo` (12 by default; 31, 19, ... work), `offset_cents` |
| `"free"` | any frequency on a fine cent grid — just intonation and arbitrary microtonal pitches | `resolution_cents` (1.0), or `snap_to=JUST_INTERVALS_CENTS` for a JI lattice |

Both modes feed the same sampler, so accuracy is comparable (docs/PITCH_MODES.md); standard mode with 25 candidates
per 2 octaves is coarser but still lands within ±0.25 of the target 93–99% of the time. Low-level use:
`pitchset.candidate_cents(mode, low, high, ...)` builds the candidate array, `sampler.generate_stream` consumes it.
- `sigma` = how tightly the level set {C = c*} is enforced (score units). `window` = notes sounding together.
- Whole-chord sampling: `sampler.metropolis_chord`; dyads: exact lookup `sampler.dyad_level_set`.
- Resumable runs: pass `Checkpoint(path)`; interrupted runs resume bit-identically.
- Demo audio: `python examples/generate_demo.py` (rendered in `examples/out/`: standard vs free vs JI at several targets).

### Setup

Needs Python 3.10 or later and `numpy`. Run everything from the repository root, with `pip install numpy pytest`.
Installing the package with `pip install .` currently **fails**: the planning folders (`plan/`, `research/`,
`premortem/`, `reviews/`) sit next to `consonance/`, so setuptools reports "multiple top-level packages". Fixing
that needs a `packages = ["consonance"]` setting in `pyproject.toml`.

Run tests: `sh scripts/verify_frozen.sh && python -m pytest` (59 tests; `tests/` is FROZEN, see tests/FROZEN.md).
Calibration: `python scripts/calibration_report.py docs` -> docs/CALIBRATION.md; `python scripts/compare_pitch_modes.py docs` -> docs/PITCH_MODES.md.

**Scale:** score = the published regression output (about -0.7 to 3.1; higher = more consonant). It is *model*-consonance
fitted to Western listeners' ratings of 12-TET chords, not a guarantee of perceived consonance for other tunings or
timbres (see IMPLEMENTATION_REPORT.md, docs/LISTENING_PROTOCOL.md). Attribution: NOTICE.

License: Apache-2.0 (see LICENSE). Third-party attribution for the incon/hrep formulas and Billboard chord counts (MIT): NOTICE.
