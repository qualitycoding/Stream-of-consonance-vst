# Research round 2 — depth, adversarial and empirical

**Tier:** Opus synthesis, empirical spikes inline.

## Empirical (R6)
* SPIKE-01: per-note cost measured at 12 / 133 / 612 ms for standard / free-5c / free-1c.
  Profiled the hot path: harmonicity 556 ms, roughness 62 ms, familiarity 4 ms, partials 0.2 ms.
  ⇒ C-012 verified. Forces D-002 (generator thread).
* SPIKE-02: hypothesised that candidate spectra are circular rotations of one precomputed
  spectrum; verified to 1.665e-15 across 2401 candidates, 6.8× faster in numpy alone.
  ⇒ C-006 verified. Makes free 1-cent resolution affordable, so A-002's default survives.

## Adversarial (R5)
Attempted to disprove the load-bearing claims:
* *"The composite score is transposition invariant, so the cents reference doesn't matter."*
  **False.** Harmonicity is transposition invariant but roughness is not — critical bandwidth is
  frequency-dependent. Scoring the same cents at 220 Hz versus 261.6255 Hz shifts the composite
  by up to 0.082. This became **R-001** and is the most dangerous defect found in this plan,
  because nothing raises and the stream simply drifts off target.
* *"The C++ port can use any RNG."* **False** for SC-4: the fixture streams would then be
  unreproducible and T-011 could only be statistical. Led to D-005 and the `fromState` fallback.
* *"±48 semitones is the MPE default, so use it."* **False** for this plugin's precision budget:
  0.586 cents/step against a 0.05-cent requirement. Led to D-006 and to fixing a contradiction
  between `soc_core.h` (which defaulted to 48) and `mpe.json` (which records 2).
* *"JUCE is JUCE; use the latest."* **False.** JUCE 9.0.0 restructures the VST3 client API.
  ⇒ C-014, D-001.

## Depth (R4)
Queried the JUCE repository's tag list and `BREAKING_CHANGES.md` directly rather than relying on
secondary coverage ⇒ C-013 verified, C-014 corroborated.

## Saturation check
Round 3 produced no new load-bearing claims, no confidence downgrades and no unresolved
contradictions, except that **C-015 could not be raised above single-source**: verifying that
Ableton honours MPE zone configuration emitted from a plugin's MIDI output needs a running Live
installation, which the planning sandbox does not have. Carried into Phase 4 as R-006 (Medium)
with an explicit mitigation and decision rule in S-012.
