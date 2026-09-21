from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Timbre:
    """Partial ratios (relative to the played fundamental) and amplitudes. One Timbre must be shared by scoring and synthesis."""
    ratios: tuple
    amps: tuple

    def __post_init__(self):
        r = tuple(float(x) for x in self.ratios)
        a = tuple(float(x) for x in self.amps)
        if not r or len(r) != len(a):
            raise ValueError("ratios and amps must be non-empty and of equal length")
        if any((not math.isfinite(x)) or x <= 0 for x in r):
            raise ValueError("ratios must be finite and > 0")
        if any((not math.isfinite(x)) or x < 0 for x in a):
            raise ValueError("amps must be finite and >= 0")
        object.__setattr__(self, "ratios", r)
        object.__setattr__(self, "amps", a)


def harmonic_timbre(n_harmonics: int = 11, roll_off: float = 1.0) -> Timbre:
    """Harmonic complex tone with amplitude 1/h**roll_off (incon composite defaults: 11 harmonics, roll_off 1)."""
    h = range(1, n_harmonics + 1)
    return Timbre(tuple(h), tuple(1.0 / (k ** roll_off) for k in h))
