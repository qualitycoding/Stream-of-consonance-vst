"""Pitch-class harmonicity after Milne (2013) / Harrison & Pearce (2018), following the MIT-licensed R packages
`incon` (R/model-har18.R) and `hrep` (R/milne-pc-spectrum.R): expand each note into weighted partials on a circular
pitch-class axis, smooth with a Gaussian (sigma=6.83 cents), sweep a harmonic template around the circle (cosine
similarity), and take the KL divergence (bits) of the normalised similarity profile from the uniform distribution."""
from __future__ import annotations
import numpy as np

SIGMA_CENTS = 6.83
RHO_EXPONENT = 0.75  # perceptual amplitude compression: weight = amp**0.75 (incon: rho = roll_off * 0.75)


def _weights(timbre, rho_exponent):
    return np.asarray(timbre.ratios), np.asarray(timbre.amps) ** rho_exponent


def _note_spectra(cents, timbre, n_bins, grid_cents, sigma, rho_exponent, chunk=128):
    """(N,) fundamental pitch classes in cents -> (N, n_bins) smoothed circular spectra."""
    cents = np.atleast_1d(np.asarray(cents, dtype=float))
    ratios, w = _weights(timbre, rho_exponent)
    offs = 1200.0 * np.log2(ratios)                       # (P,)
    bins = np.arange(n_bins) * grid_cents                 # (B,)
    out = np.empty((cents.size, n_bins))
    for s in range(0, cents.size, chunk):
        pos = np.mod(cents[s:s + chunk, None] + offs[None, :], 1200.0)         # (n,P)
        d = np.abs(bins[None, None, :] - pos[:, :, None])
        d = np.minimum(d, 1200.0 - d)
        out[s:s + chunk] = (w[None, :, None] * np.exp(-0.5 * (d / sigma) ** 2)).sum(axis=1)
    return out


def _kl_from_uniform_bits(S, T):
    """S: (N,B) chord spectra; T: (B,) template. Cosine-similarity sweep (circular) -> KL(p || uniform) in bits."""
    B = S.shape[1]
    r = np.fft.irfft(np.fft.rfft(S, axis=1) * np.conj(np.fft.rfft(T))[None, :], n=B, axis=1)
    denom = np.linalg.norm(S, axis=1, keepdims=True) * np.linalg.norm(T)
    cos = np.clip(r / np.where(denom > 0, denom, 1.0), 0.0, None)
    tot = cos.sum(axis=1, keepdims=True)
    p = cos / np.where(tot > 0, tot, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(p > 0, p * np.log2(p * B), 0.0)
    return np.maximum(term.sum(axis=1), 0.0)


def _template(timbre, n_bins, grid_cents, sigma, rho_exponent):
    return _note_spectra([0.0], timbre, n_bins, grid_cents, sigma, rho_exponent)[0]


def harmonicity(cents, timbre, grid_cents: float = 1.0, sigma: float = SIGMA_CENTS, rho_exponent: float = RHO_EXPONENT) -> float:
    """Pitch-class harmonicity (bits) of notes given as cents (any octave; only pitch class matters)."""
    c = np.asarray(cents, dtype=float).ravel()
    if c.size == 0 or not np.all(np.isfinite(c)):
        raise ValueError("cents must be finite and non-empty")
    B = int(round(1200.0 / grid_cents))
    S = _note_spectra(c, timbre, B, grid_cents, sigma, rho_exponent).sum(axis=0, keepdims=True)
    return float(_kl_from_uniform_bits(S, _template(timbre, B, grid_cents, sigma, rho_exponent))[0])


def harmonicity_with_candidates(held_cents, cand_cents, timbre, grid_cents: float = 1.0,
                                sigma: float = SIGMA_CENTS, rho_exponent: float = RHO_EXPONENT) -> np.ndarray:
    """Vectorised harmonicity of held ∪ {candidate} for each candidate. Returns (N,)."""
    B = int(round(1200.0 / grid_cents))
    held = np.asarray(held_cents, dtype=float).ravel()
    S0 = _note_spectra(held, timbre, B, grid_cents, sigma, rho_exponent).sum(axis=0) if held.size else np.zeros(B)
    S = S0[None, :] + _note_spectra(cand_cents, timbre, B, grid_cents, sigma, rho_exponent)
    return _kl_from_uniform_bits(S, _template(timbre, B, grid_cents, sigma, rho_exponent))
