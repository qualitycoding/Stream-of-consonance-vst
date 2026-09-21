# SOURCES

## Tier 1 — source code, specifications, official docs at the pinned version, peer-reviewed papers
* `qualitycoding/Stream-of-consonance` @ `9c8e5e1` — `consonance/` package and its frozen test
  suite. The reference implementation and the oracle for every fixture.
* Harrison, P. M. C. & Pearce, M. T. (2020). Simultaneous consonance in music perception and
  composition. *Psychological Review* 127(2), 216–244. The regression the model implements.
* Harrison, P. M. C. & Pearce, M. T. (2018), ISMIR. Source of the exponential-family energy form
  the sampler reuses for inversion.
* R package `incon` (MIT) — `R/model-dycon.R`, `R/model-har18.R`, `har_19_composite_coef`.
  Attribution in the repository `NOTICE`.
* R package `hrep` (MIT) — `R/milne-pc-spectrum.R`.
* `juce-framework/JUCE` tag list, queried directly via `git ls-remote --tags` on 2026-09-20.
* `juce-framework/JUCE` `BREAKING_CHANGES.md` @ tag `9.0.2`.
* Ableton, "MPE in Live 11 and later FAQ", help.ableton.com/hc/en-us/articles/360019144999.
* numpy 2.4.4 `numpy.random.PCG64` documentation.

## Tier 2 — maintainer statements, changelogs, release metadata
* JUCE GitHub release history (tags 8.0.11 … 9.0.2 with publication dates).

## Tier 3 — reputable secondary write-ups
* cdm.link, "Ableton Live 11.3 in beta" — MPE expansion across Live devices. Used only to
  corroborate C-010, never alone.
* Sound On Sound, JUCE 8 release coverage — background only; no load-bearing claim rests on it.

## Tier 4 — not used
No forum or blog source supports any load-bearing claim in this plan.

## Own spikes (primary evidence generated for this plan)
* `research/spikes/spike_01_timing.py` + `spike_01_output.txt` — per-note cost (C-012).
* `research/spikes/spike_02_rotation.py` + `spike_02_output.txt` — rotation identity (C-006).
* `research/spikes/spike_03_red_verify_output.txt` — Phase 2.3 red verification.
* `tests/make_fixtures.py` + `tests/fixtures/` — the oracle capture itself.
