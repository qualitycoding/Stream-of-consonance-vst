# Listening-test protocol (S9b) — NOT YET RUN
Purpose: measure how far model-consonance c* departs from perceived consonance, especially outside the calibration
domain (12-TET Western chords, harmonic timbres): microtonal sonorities, inharmonic timbres.
Design: for 3 timbres (harmonic; stretched-harmonic; inharmonic percussive) x 3 tunings (12-TET, 31-EDO, just) x
5 targets (0.4,0.8,1.2,1.6,2.0) generate 4-note sonorities (fixed seeds, min 30 cents separation). Listeners rate
"pleasantness" 1-7 (H&P operationalisation) in randomised order, headphones, 20+ listeners, with anchors (octave, major
triad, cluster). Analysis: mixed-effects regression of rating on c* with random intercepts per listener; report slope,
R^2 and per-condition deviations. Acceptance: slope > 0 with CI excluding 0 in every condition; where it fails, mark
the condition outside the validated domain (the library's `familiarity_mode='drop'` fallback is only a stop-gap).
