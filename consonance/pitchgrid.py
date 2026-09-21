"""Pitch-set switch: which pitches the generator is allowed to choose from.

Two modes:
  PitchMode.STANDARD — only notes of an equal-tempered chromatic scale (default 12-TET: A, C#, ...).
                       Familiarity (corpus) term of the composite model is defined here.
  PitchMode.FREE     — any frequency on a fine cent grid, optionally with exact just-intonation
                       ratios inserted, so microtonal and JI intervals are reachable.
"""
from __future__ import annotations
from fractions import Fraction

import numpy as np

STANDARD = "standard"
FREE = "free"
MODES = (STANDARD, FREE)

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

#: 5- and 7-limit ratios within one octave, used to seed FREE mode with exact just intervals.
DEFAULT_JUST_RATIOS = (
    Fraction(1, 1), Fraction(16, 15), Fraction(9, 8), Fraction(7, 6), Fraction(6, 5), Fraction(5, 4),
    Fraction(4, 3), Fraction(7, 5), Fraction(10, 7), Fraction(3, 2), Fraction(8, 5), Fraction(5, 3),
    Fraction(7, 4), Fraction(9, 5), Fraction(15, 8),
)


class PitchMode:
    STANDARD = STANDARD
    FREE = FREE


def _check_range(low_cents, high_cents):
    if not (np.isfinite(low_cents) and np.isfinite(high_cents)) or high_cents <= low_cents:
        raise ValueError("require low_cents < high_cents, both finite")


def candidate_grid(mode: str, low_cents: float, high_cents: float, *, edo: int = 12,
                   resolution_cents: float = 1.0, include_just: bool = True,
                   just_ratios=DEFAULT_JUST_RATIOS, ref_cents: float = 0.0) -> np.ndarray:
    """Allowed pitches, in cents relative to the generator's reference pitch.

    mode=STANDARD: exactly the `edo`-tone equal-tempered scale degrees (edo=12 gives A, C#, ...).
    mode=FREE:     a `resolution_cents` grid, plus (if include_just) exact just ratios in every octave.
    `ref_cents` shifts the whole scale (e.g. to tune the chromatic grid off the reference pitch).
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    _check_range(low_cents, high_cents)

    if mode == STANDARD:
        if not isinstance(edo, (int, np.integer)) or edo < 1:
            raise ValueError("edo must be a positive integer")
        step = 1200.0 / edo
        k0 = int(np.ceil((low_cents - ref_cents) / step))
        k1 = int(np.floor((high_cents - ref_cents) / step))
        if k1 < k0:
            raise ValueError("no scale degree falls inside the requested range")
        return ref_cents + step * np.arange(k0, k1 + 1, dtype=float)

    if not np.isfinite(resolution_cents) or resolution_cents <= 0:
        raise ValueError("resolution_cents must be finite and > 0")
    grid = np.arange(low_cents, high_cents + 1e-9, resolution_cents, dtype=float)
    if include_just and just_ratios:
        just = np.array([1200.0 * np.log2(float(r)) for r in just_ratios], dtype=float)
        oct_lo = int(np.floor((low_cents - ref_cents) / 1200.0))
        oct_hi = int(np.ceil((high_cents - ref_cents) / 1200.0))
        offs = np.concatenate([ref_cents + just + 1200.0 * o for o in range(oct_lo, oct_hi + 1)])
        offs = offs[(offs >= low_cents) & (offs <= high_cents)]
        grid = np.concatenate([grid, offs])
    return np.unique(np.round(grid, 6))


def note_name(cents: float, ref_hz: float = 220.0, *, show_deviation: bool = True) -> str:
    """Name a pitch (cents re ref_hz) by its nearest 12-TET note, e.g. 'C#5' or 'E5 -14c' (just major third)."""
    midi_ref = 69.0 + 12.0 * np.log2(ref_hz / 440.0)
    midi = midi_ref + cents / 100.0
    n = int(round(midi))
    dev = (midi - n) * 100.0
    name = f"{NOTE_NAMES[n % 12]}{n // 12 - 1}"
    if show_deviation and abs(dev) >= 0.5:
        name += f" {dev:+.0f}c"
    return name


def describe(mode: str, grid: np.ndarray) -> str:
    kind = "12-TET scale degrees only" if mode == STANDARD else "any frequency on the cent grid (microtonal/JI)"
    return f"{mode}: {grid.size} candidates, {kind}, {grid.min():.0f}..{grid.max():.0f} cents"
