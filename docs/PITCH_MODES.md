# Pitch-mode comparison

24-note streams, window 4, sigma 0.1, novelty 1.5, seeds 1-3, harmonic timbre (11 partials).

| mode | candidates | target | mean err | mean abs err | within ±0.25 |
|---|---|---|---|---|---|
| standard (12-TET) | 25 | 0.8 | -0.011 | 0.087 | 96% |
| standard (12-TET) | 25 | 1.2 | -0.038 | 0.087 | 99% |
| standard (12-TET) | 25 | 1.6 | -0.046 | 0.103 | 96% |
| standard (12-TET) | 25 | 2.0 | -0.066 | 0.112 | 93% |
| standard (31-EDO) | 62 | 0.8 | +0.008 | 0.077 | 100% |
| standard (31-EDO) | 62 | 1.2 | -0.048 | 0.084 | 100% |
| standard (31-EDO) | 62 | 1.6 | -0.069 | 0.110 | 94% |
| standard (31-EDO) | 62 | 2.0 | -0.133 | 0.149 | 86% |
| free (1-cent grid) | 2401 | 0.8 | +0.011 | 0.071 | 100% |
| free (1-cent grid) | 2401 | 1.2 | -0.044 | 0.101 | 99% |
| free (1-cent grid) | 2401 | 1.6 | -0.120 | 0.134 | 89% |
| free (1-cent grid) | 2401 | 2.0 | -0.112 | 0.134 | 96% |
| free (JI lattice) | 24 | 0.8 | +0.001 | 0.091 | 100% |
| free (JI lattice) | 24 | 1.2 | -0.030 | 0.085 | 97% |
| free (JI lattice) | 24 | 1.6 | -0.079 | 0.109 | 92% |
| free (JI lattice) | 24 | 2.0 | -0.096 | 0.138 | 89% |
