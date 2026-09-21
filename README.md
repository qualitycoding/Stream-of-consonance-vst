# Stream-of-consonance

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

## Pitch mode (the switch)
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

Run tests: `sh scripts/verify_frozen.sh && python -m pytest` (59 tests; `tests/` is FROZEN, see tests/FROZEN.md).
Calibration: `python scripts/calibration_report.py docs` -> docs/CALIBRATION.md; `python scripts/compare_pitch_modes.py docs` -> docs/PITCH_MODES.md.

**Scale:** score = the published regression output (about -0.7 to 3.1; higher = more consonant). It is *model*-consonance
fitted to Western listeners' ratings of 12-TET chords, not a guarantee of perceived consonance for other tunings or
timbres (see IMPLEMENTATION_REPORT.md, docs/LISTENING_PROTOCOL.md). Attribution: NOTICE.

License: Apache-2.0 (see LICENSE). Third-party attribution for the incon/hrep formulas and Billboard chord counts (MIT): NOTICE.
