# Calibration report (model-consonance, not perceptual)

Setup: {"timbre": "harmonic, 11 partials, amp 1/h", "sigma": 0.1, "tolerance": 0.25, "window": 4, "novelty_weight": 1.5, "n_steps": 30, "seeds": [1, 2, 3], "candidates": "-600..1795 cents re 220 Hz, 5-cent grid", "seconds": 83.88678669929504}

| target c* | mean err | std | mean abs err | within ±0.25 | distinct pcs (quarter-tone bins, of 30 notes) | max pc share |
|---|---|---|---|---|---|---|
| 0.4 | +0.043 | 0.096 | 0.090 | 100% | 16.7 | 14% |
| 0.8 | -0.020 | 0.091 | 0.073 | 99% | 20.0 | 10% |
| 1.2 | -0.056 | 0.093 | 0.089 | 99% | 18.3 | 10% |
| 1.6 | -0.090 | 0.112 | 0.116 | 91% | 15.3 | 11% |
| 2.0 | -0.125 | 0.093 | 0.134 | 90% | 13.0 | 17% |
| 2.4 | -0.205 | 0.095 | 0.208 | 76% | 4.3 | 43% |

Attainable model-consonance by sonority size (1500 random chords each, so extremes are underestimated):

| notes | min | p5 | median | p95 | max |
|---|---|---|---|---|---|
| 2 | 0.46 | 0.91 | 1.88 | 2.29 | 3.06 |
| 3 | -0.11 | 0.53 | 1.28 | 1.80 | 2.98 |
| 4 | -0.68 | 0.17 | 0.81 | 1.29 | 2.02 |
