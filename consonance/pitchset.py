"""Pitch-mode switch: which frequencies the generator is allowed to choose from.

Two modes:
  PitchMode.STANDARD ("standard") — only notes of an equal-tempered chromatic scale (12-TET by default: A, C#, ...).
  PitchMode.FREE     ("free")     — any frequency on a fine cent grid, so just-intonation and arbitrary microtonal
                                    pitches are all reachable (5-limit JI intervals land within ~2 cents of a 1-cent grid).

Both produce a candidate array in cents relative to the generator's reference pitch, which is what the sampler
consumes; everything downstream (scoring, sampling, checkpointing) is unchanged."""
from __future__ import annotations
from enum import Enum

import numpy as np

# Common just intervals (5-limit + harmonic 7th), cents above the reference. Usable as a `snap_to` set in FREE mode.
JUST_INTERVALS_CENTS = tuple(1200.0 * np.log2(np.array([
    1 / 1, 16 / 15, 9 / 8, 6 / 5, 5 / 4, 4 / 3, 45 / 32, 3 / 2, 8 / 5, 5 / 3, 7 / 4, 15 / 8,
])))


class PitchMode(str, Enum):
    STANDARD = "standard"
    FREE = "free"

    @classmethod
    def coerce(cls, value) -> "PitchMode":
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError:
            raise ValueError(f"pitch mode must be one of {[m.value for m in cls]}, got {value!r}") from None


def candidate_cents(mode, low_cents: float = -600.0, high_cents: float = 1800.0, *, edo: int = 12,
                    resolution_cents: float = 1.0, offset_cents: float = 0.0, snap_to=None) -> np.ndarray:
    """Allowed pitches, in cents relative to the reference pitch, over [low_cents, high_cents].

    STANDARD: steps of 1200/edo cents (edo=12 gives the usual chromatic notes), shifted by `offset_cents`.
    FREE:     steps of `resolution_cents` cents; or, if `snap_to` is given (e.g. JUST_INTERVALS_CENTS), exactly those
              intervals repeated in every octave — a just-intonation lattice rather than a uniform grid."""
    mode = PitchMode.coerce(mode)
    if high_cents <= low_cents:
        raise ValueError("high_cents must exceed low_cents")

    if mode is PitchMode.STANDARD:
        if edo < 1:
            raise ValueError("edo must be >= 1")
        step = 1200.0 / edo
    elif snap_to is None:
        if resolution_cents <= 0:
            raise ValueError("resolution_cents must be > 0")
        step = float(resolution_cents)
    else:
        base = np.mod(np.asarray(snap_to, dtype=float) + offset_cents, 1200.0)
        octaves = np.arange(np.floor(low_cents / 1200.0), np.ceil(high_cents / 1200.0) + 1) * 1200.0
        cand = np.unique((octaves[:, None] + base[None, :]).ravel())
        return cand[(cand >= low_cents) & (cand <= high_cents)]

    first = np.ceil((low_cents - offset_cents) / step)
    last = np.floor((high_cents - offset_cents) / step)
    return offset_cents + step * np.arange(first, last + 1)


def describe(mode, **kwargs) -> str:
    mode = PitchMode.coerce(mode)
    if mode is PitchMode.STANDARD:
        return f"standard notes ({kwargs.get('edo', 12)}-tone equal temperament)"
    if kwargs.get("snap_to") is not None:
        return "free pitch, snapped to a just-intonation lattice"
    return f"free pitch ({kwargs.get('resolution_cents', 1.0):g}-cent grid; JI and microtonal pitches reachable)"
