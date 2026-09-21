"""Pure-tone-pair interference (roughness) models, following the formulas in the MIT-licensed R package `incon`
(R/model-dycon.R): Sethares (1993; min-amplitude variant of Sethares 2005), Hutchinson & Knopoff (1978, Mashinter 2006
parametrisation, cut-off 1.2 CBW) and Vassilakis (2001)."""
from __future__ import annotations
import numpy as np


def _validate(freqs) -> np.ndarray:
    f = np.asarray(freqs, dtype=float).ravel()
    if f.size == 0 or not np.all(np.isfinite(f)) or np.any(f <= 0):
        raise ValueError("frequencies must be finite and > 0")
    return f


def _partials(freqs_hz: np.ndarray, timbre, max_hz: float):
    """(K,) partial frequencies and amplitudes; partials above max_hz get amplitude 0 (=ignored)."""
    ratios = np.asarray(timbre.ratios)
    amps = np.asarray(timbre.amps)
    f = (freqs_hz[..., None] * ratios).reshape(*freqs_hz.shape[:-1], -1)
    a = np.broadcast_to(np.tile(amps, freqs_hz.shape[-1]), f.shape).copy()
    a[f > max_hz] = 0.0
    return f, a


def _pair_terms(model: str, f1, f2, a1, a2):
    d = np.abs(f1 - f2)
    if model == "sethares":
        s = 0.24 / (0.021 * np.minimum(f1, f2) + 19.0)
        return np.minimum(a1, a2) * (np.exp(-3.5 * s * d) - np.exp(-5.75 * s * d))
    if model == "hutchinson":
        cbw = 1.72 * ((f1 + f2) / 2.0) ** 0.65
        y = d / cbw
        g = ((y / 0.25) * np.exp(1.0 - y / 0.25)) ** 2
        g = np.where(y > 1.2, 0.0, g)
        return a1 * a2 * g
    if model == "vassilakis":
        s = 0.24 / (0.0207 * np.minimum(f1, f2) + 18.96)
        tot = a1 + a2
        ratio = np.where(tot > 0, 2.0 * np.minimum(a1, a2) / np.where(tot > 0, tot, 1.0), 0.0)
        x = s * d
        return 2.0 * ((a1 * a2) ** 0.1) * 0.5 * ratio ** 3.11 * (np.exp(-3.5 * x) - np.exp(-5.75 * x))
    raise ValueError(f"unknown interference model {model!r}")


def dissonance_from_partials(F: np.ndarray, A: np.ndarray, model: str = "sethares", chunk: int = 512) -> np.ndarray:
    """Batch roughness. F, A: (N, K). Returns (N,). Sum over unordered partial pairs; Hutchinson is divided by sum(A**2)."""
    F = np.atleast_2d(F)
    A = np.atleast_2d(A)
    n, k = F.shape
    iu, ju = np.triu_indices(k, 1)
    out = np.empty(n)
    for s in range(0, n, chunk):
        f, a = F[s:s + chunk], A[s:s + chunk]
        terms = _pair_terms(model, f[:, iu], f[:, ju], a[:, iu], a[:, ju])
        tot = terms.sum(axis=1)
        if model == "hutchinson":
            den = (a ** 2).sum(axis=1)
            tot = np.where(den > 0, tot / np.where(den > 0, den, 1.0), 0.0)
        out[s:s + chunk] = tot
    return out


def dissonance(freqs_hz, timbre, model: str = "sethares", max_hz: float = 20000.0) -> float:
    """Roughness of a set of simultaneous notes (fundamentals in Hz) rendered with `timbre`. Higher = rougher."""
    f = _validate(freqs_hz)
    F, A = _partials(f[None, :], timbre, max_hz)
    return float(dissonance_from_partials(F, A, model)[0])
