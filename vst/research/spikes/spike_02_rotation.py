"""SPIKE-02 — the harmonicity hot path is a circular rotation. Informs C-006, D-004.

Claim under test: every candidate's pitch-class spectrum is an exact circular shift of one
precomputed single-note spectrum, so the O(n_cand x P x B) construction in _note_spectra can be
replaced by indexing. If true, free mode at 1-cent resolution is affordable in C++.
Run: PYTHONPATH=<repo root> python3 spike_02_rotation.py
"""
import time
import numpy as np
from consonance.harmonicity import (RHO_EXPONENT, SIGMA_CENTS, _kl_from_uniform_bits,
                                    _note_spectra, _template, harmonicity_with_candidates)
from consonance.pitchset import candidate_cents
from consonance.timbre import harmonic_timbre

t, B = harmonic_timbre(11, 1.0), 1200
cand = candidate_cents("free", -600.0, 1800.0)
held = np.array([0.0, 700.0, 400.0])

s = time.perf_counter(); ref = harmonicity_with_candidates(held, cand, t); t_ref = time.perf_counter() - s

T0 = _note_spectra([0.0], t, B, 1.0, SIGMA_CENTS, RHO_EXPONENT)[0]
S0 = _note_spectra(held, t, B, 1.0, SIGMA_CENTS, RHO_EXPONENT).sum(axis=0)
s = time.perf_counter()
k = np.mod(np.rint(cand).astype(int), B)
S = S0[None, :] + T0[(np.arange(B)[None, :] - k[:, None]) % B]
fast = _kl_from_uniform_bits(S, _template(t, B, 1.0, SIGMA_CENTS, RHO_EXPONENT))
t_fast = time.perf_counter() - s

print(f"max abs diff {np.abs(ref - fast).max():.3e}")
print(f"reference {t_ref*1000:7.1f} ms -> rotation {t_fast*1000:7.1f} ms  ({t_ref/t_fast:.1f}x)")
assert np.allclose(ref, fast, rtol=0, atol=1e-12), "rotation identity does not hold"
print("PASS: rotation identity holds to machine precision")
