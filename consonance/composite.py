"""Harrison & Pearce (2020) composite consonance model.

score = intercept + w_int*roughness_HK + w_har*harmonicity_KL + w_fam*log P(chord type | Billboard) + w_n*n_notes

Default coefficients are those of incon::har_19_composite_coef (MIT; see NOTICE): intercept 0.6284, chord_size 0.4223
(disabled by default, as in incon, because the effect is thought to be a confound of the Bowling et al. 2018 data),
Hutchinson-Knopoff roughness -1.6200, harmonicity +1.7799, corpus dissonance (= -log P) -0.0892, i.e. +0.0892 on log P.
incon defaults for the spectrum: 11 harmonics, amplitude 1/h (see timbre.harmonic_timbre)."""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from . import familiarity as fam
from .harmonicity import harmonicity, harmonicity_with_candidates
from .interference import _partials, _validate, dissonance_from_partials
from .timbre import Timbre

REF_HZ = 261.6255653005986  # C4; only fixes the pitch-class origin (harmonicity is transposition invariant)


class UnsupportedTuningError(ValueError):
    """Familiarity is undefined for non-12-TET chords and familiarity_mode='strict'."""


class TimbreMismatchError(ValueError):
    """Scoring timbre differs from the timbre supplied for synthesis."""


@dataclass(frozen=True)
class Weights:
    interference: float = -1.62001025973261
    harmonicity: float = 1.77992362857478
    familiarity: float = 0.0892234643584134   # applied to log P (incon: -0.0892 on -log P)
    n_notes: float = 0.0                      # incon default: chord-size effect disabled (0.42226769860 if enabled)
    intercept: float = 0.628434666589357


class CompositeModel:
    def __init__(self, timbre: Timbre, weights: Weights | None = None, familiarity_mode: str = "drop",
                 max_hz: float = 20000.0):
        if familiarity_mode not in ("drop", "strict"):
            raise ValueError("familiarity_mode must be 'drop' or 'strict'")
        self.timbre = timbre
        self.weights = weights if weights is not None else Weights()
        self.familiarity_mode = familiarity_mode
        self.max_hz = max_hz

    # -- guards ---------------------------------------------------------------------------------------------
    def check_timbre(self, other: Timbre) -> None:
        if other != self.timbre:
            raise TimbreMismatchError("timbre used for synthesis differs from the timbre the model scores")

    def _fam(self, cents_abs):
        v = fam.familiarity_from_cents(cents_abs)
        if v is None and self.familiarity_mode == "strict":
            raise UnsupportedTuningError("chord is not 12-TET; familiarity undefined (use familiarity_mode='drop')")
        return v

    # -- single chord ---------------------------------------------------------------------------------------
    def features(self, freqs_hz) -> dict:
        f = _validate(freqs_hz)
        F, A = _partials(f[None, :], self.timbre, self.max_hz)
        cents = 1200.0 * np.log2(f / REF_HZ)
        return {
            "interference": float(dissonance_from_partials(F, A, "hutchinson")[0]),
            "harmonicity": harmonicity(cents, self.timbre),
            "familiarity": self._fam(cents),
            "n_notes": int(f.size),
        }

    def _combine(self, ft) -> float:
        w = self.weights
        fam_v = ft["familiarity"] if ft["familiarity"] is not None else fam.neutral_log_prob()
        return (w.intercept + w.interference * ft["interference"] + w.harmonicity * ft["harmonicity"]
                + w.familiarity * fam_v + w.n_notes * ft["n_notes"])

    def score(self, freqs_hz) -> float:
        return float(self._combine(self.features(freqs_hz)))

    # -- vectorised: score held ∪ {candidate} for every candidate --------------------------------------------
    def score_with_candidates(self, held_hz, candidate_hz) -> np.ndarray:
        held = np.asarray(held_hz, dtype=float).ravel()
        cand = _validate(candidate_hz)
        if held.size:
            _validate(held)
        n = cand.size
        hp_f, hp_a = _partials(held[None, :], self.timbre, self.max_hz) if held.size else (np.empty((1, 0)), np.empty((1, 0)))
        cp_f, cp_a = _partials(cand[:, None], self.timbre, self.max_hz)
        F = np.concatenate([np.broadcast_to(hp_f, (n, hp_f.shape[1])), cp_f], axis=1)
        A = np.concatenate([np.broadcast_to(hp_a, (n, hp_a.shape[1])), cp_a], axis=1)
        rough = dissonance_from_partials(F, A, "hutchinson")
        held_c = 1200.0 * np.log2(held / REF_HZ) if held.size else np.empty(0)
        cand_c = 1200.0 * np.log2(cand / REF_HZ)
        har = harmonicity_with_candidates(held_c, cand_c, self.timbre)
        famv = np.empty(n)
        held_list = held_c.tolist()
        for i in range(n):
            v = self._fam(held_list + [cand_c[i]])
            famv[i] = v if v is not None else fam.neutral_log_prob()
        w = self.weights
        return (w.intercept + w.interference * rough + w.harmonicity * har + w.familiarity * famv
                + w.n_notes * (held.size + 1))
