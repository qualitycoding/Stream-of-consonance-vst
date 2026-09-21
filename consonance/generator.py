"""One-call front end: pick a pitch mode, a target consonance, and generate a stream of tones."""
from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np

from .composite import CompositeModel
from .pitchset import PitchMode, candidate_cents, describe
from .sampler import generate_stream
from .timbre import Timbre, harmonic_timbre


@dataclass
class ToneStreamGenerator:
    """Generate tones whose sounding sonority tracks a target consonance value.

    pitch_mode: "standard" (only 12-TET notes: A, C#, ...) or "free" (any frequency on a fine cent grid — just
    intonation, microtonal, anything). Pass `edo` to change the standard scale, or `snap_to` (e.g.
    pitchset.JUST_INTERVALS_CENTS) to restrict free mode to a just-intonation lattice."""
    pitch_mode: str = PitchMode.STANDARD
    timbre: Timbre = field(default_factory=lambda: harmonic_timbre(11, 1.0))
    ref_hz: float = 220.0
    low_cents: float = -600.0
    high_cents: float = 1800.0
    edo: int = 12
    resolution_cents: float = 1.0
    offset_cents: float = 0.0
    snap_to: object = None
    window: int = 4
    sigma: float = 0.1
    min_separation_cents: float = 30.0
    novelty_weight: float = 1.5
    familiarity_mode: str = "drop"

    def __post_init__(self):
        self.pitch_mode = PitchMode.coerce(self.pitch_mode)
        self.model = CompositeModel(self.timbre, familiarity_mode=self.familiarity_mode)
        self.candidates = candidate_cents(self.pitch_mode, self.low_cents, self.high_cents, edo=self.edo,
                                          resolution_cents=self.resolution_cents, offset_cents=self.offset_cents,
                                          snap_to=self.snap_to)
        if self.candidates.size == 0:
            raise ValueError("no candidate pitches in the requested range")

    # -- helpers --------------------------------------------------------------------------------------------
    def hz(self, cents) -> np.ndarray:
        return self.ref_hz * 2.0 ** (np.asarray(cents, dtype=float) / 1200.0)

    def description(self) -> str:
        return f"{describe(self.pitch_mode, edo=self.edo, resolution_cents=self.resolution_cents, snap_to=self.snap_to)}, {self.candidates.size} candidates"

    def score(self, cents) -> float:
        return self.model.score(self.hz(cents))

    def _energy_for_state(self, state):
        held = self.hz(list(state)) if len(state) else np.empty(0)
        return lambda c: self.model.score_with_candidates(held, self.hz(c))

    # -- generation -----------------------------------------------------------------------------------------
    def generate(self, target: float, n_steps: int = 24, seed: int = 0, start=(0.0,), checkpoint=None,
                 checkpoint_every: int = 5, max_steps_this_run: int | None = None, tolerance: float = 0.25):
        """Returns (StreamResult, realised score after each note)."""
        res = generate_stream(self._energy_for_state, self.candidates, n_steps, target, self.sigma, seed,
                              start=start, checkpoint=checkpoint, checkpoint_every=checkpoint_every,
                              max_steps_this_run=max_steps_this_run, window=self.window,
                              min_separation_cents=self.min_separation_cents, tolerance=tolerance,
                              novelty_weight=self.novelty_weight)
        state, scores = [float(x) for x in start], []
        for n in res.notes:
            state = (state + [n])[-self.window:]
            scores.append(self.score(state))
        return res, scores
