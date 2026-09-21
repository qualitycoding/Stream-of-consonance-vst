"""Inversion of a consonance model by conditional sampling.

Target distribution over candidate pitches p given the current sonority S:
    pi(p) ∝ exp( -(C(S ∪ {p}) - c*)^2 / (2 sigma^2) ) * prior(p)
sigma controls how tightly the level set {C = c*} is enforced (sigma -> 0 gives the exact argmin). This is this
project's own design (no published inversion of the composite model was found); it uses the same exponential-family
energy form as Harrison & Pearce (2018, ISMIR)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .checkpoint import Checkpoint


@dataclass(frozen=True)
class SampleResult:
    cents: float
    value: float
    reached: bool


@dataclass
class StreamResult:
    notes: list
    complete: bool


def _log_weights(values, target, sigma, log_prior=None):
    if sigma <= 0 or not np.isfinite(sigma):
        raise ValueError("sigma must be finite and > 0")
    z = (np.asarray(values, dtype=float) - target) / sigma
    lw = -0.5 * z * z
    if log_prior is not None:
        lw = lw + log_prior
    return lw


def sample_next(energy_fn: Callable, candidates_cents, target: float, sigma: float, rng, exclude=(),
                tolerance: float = 0.05, log_prior=None) -> SampleResult:
    cands = np.asarray(candidates_cents, dtype=float)
    vals = np.asarray(energy_fn(cands), dtype=float)
    if vals.shape != cands.shape:
        raise ValueError("energy_fn must return one value per candidate")
    lw = _log_weights(np.where(np.isfinite(vals), vals, np.inf), target, sigma, log_prior)
    excl = np.asarray(list(exclude) if not isinstance(exclude, np.ndarray) else exclude, dtype=float)
    if excl.size:
        lw = np.where(np.isin(cands, excl), -np.inf, lw)
    if not np.isfinite(lw).any():
        raise ValueError("no admissible candidate")
    lw = lw - np.max(lw[np.isfinite(lw)])                 # log-sum-exp stabilisation
    w = np.exp(lw)
    cdf = np.cumsum(w)
    i = int(np.searchsorted(cdf, rng.random() * cdf[-1], side="right"))
    i = min(i, cands.size - 1)
    return SampleResult(float(cands[i]), float(vals[i]), bool(abs(vals[i] - target) <= tolerance))


def generate_stream(energy_for_state: Callable, candidates_cents, n_steps: int, target: float, sigma: float,
                    rng_seed: int, start=(), checkpoint: Checkpoint | None = None, checkpoint_every: int = 5,
                    max_steps_this_run: int | None = None, window: int | None = None,
                    min_separation_cents: float = 0.0, tolerance: float = 0.05,
                    novelty_weight: float = 0.0, novelty_memory: int = 8, novelty_width_cents: float = 25.0) -> StreamResult:
    """Generate n_steps notes, each chosen so that the consonance of the sounding notes stays near `target`.

    window: size of the sliding sonority. The chosen note is scored together with the last `window - 1` notes
    (incl. `start`), so exactly `window` notes sound at once; None = all notes accumulate.
    novelty_weight: >0 adds log-prior -novelty_weight * (#recent generated notes with the same pitch class within
    novelty_width_cents, among the last `novelty_memory` notes) to fight repetitive output (mode collapse).
    Resumable: with a Checkpoint, state (step, notes, RNG state, config) is saved every `checkpoint_every` steps and on
    interruption, and an identical call resumes bit-identically."""
    cands = np.asarray(candidates_cents, dtype=float)
    config = {"n_steps": n_steps, "target": target, "sigma": sigma, "rng_seed": rng_seed, "start": [float(x) for x in start],
              "window": window, "min_sep": min_separation_cents, "nov": [novelty_weight, novelty_memory, novelty_width_cents], "n_cand": int(cands.size), "cand_sum": float(cands.sum())}
    rng = np.random.default_rng(rng_seed)
    notes: list = []
    step = 0
    if checkpoint is not None:
        saved = checkpoint.load()
        if saved is not None:
            if saved.get("config") != config:
                raise ValueError("checkpoint was written for a different configuration")
            notes, step = list(saved["notes"]), int(saved["step"])
            rng.bit_generator.state = saved["rng_state"]

    def save():
        if checkpoint is not None:
            checkpoint.save({"config": config, "step": step, "notes": notes, "rng_state": rng.bit_generator.state})

    done_this_run = 0
    while step < n_steps:
        if max_steps_this_run is not None and done_this_run >= max_steps_this_run:
            save()
            return StreamResult(notes, False)
        state = [float(x) for x in start] + notes
        if window is not None:
            state = state[-(window - 1):] if window > 1 else []
        excl = ()
        if min_separation_cents > 0 and state:
            near = np.any(np.abs(cands[:, None] - np.asarray(state)[None, :]) < min_separation_cents, axis=1)
            excl = cands[near]
        prior = None
        if novelty_weight > 0 and notes:
            recent = np.asarray(notes[-novelty_memory:])
            d = np.abs(np.mod(cands[:, None] - recent[None, :] + 600.0, 1200.0) - 600.0)
            prior = -novelty_weight * (d <= novelty_width_cents).sum(axis=1)
        res = sample_next(energy_for_state(tuple(state)), cands, target, sigma, rng, exclude=excl, tolerance=tolerance,
                          log_prior=prior)
        notes.append(res.cents)
        step += 1
        done_this_run += 1
        if checkpoint is not None and step % checkpoint_every == 0:
            save()
    save()
    return StreamResult(notes, True)


def metropolis_chord(energy_fn: Callable, n_notes: int, grid_cents, target: float, sigma: float, n_steps: int, rng,
                     burn_in: int = 0) -> np.ndarray:
    """Metropolis sampler over whole chords (single-note independence proposals) targeting
    pi(chord) ∝ exp(-(C(chord) - target)^2 / (2 sigma^2)). Returns (n_steps, n_notes)."""
    grid = np.asarray(grid_cents, dtype=float)
    chord = rng.choice(grid, size=n_notes)
    logp = float(_log_weights([energy_fn(chord)], target, sigma)[0])
    out = np.empty((n_steps, n_notes))
    for t in range(burn_in + n_steps):
        i = int(rng.integers(n_notes))
        prop = chord.copy()
        prop[i] = grid[int(rng.integers(grid.size))]
        lp = float(_log_weights([energy_fn(prop)], target, sigma)[0])
        if np.log(rng.random()) < lp - logp:
            chord, logp = prop, lp
        if t >= burn_in:
            out[t - burn_in] = chord
    return out


def dyad_level_set(dyad_energy_fn: Callable, grid_cents, target: float, tol: float) -> np.ndarray:
    """Exact level set {interval on grid : |C - target| <= tol} (dyads: invert by lookup)."""
    grid = np.asarray(grid_cents, dtype=float)
    vals = np.asarray(dyad_energy_fn(grid), dtype=float)
    return grid[np.abs(vals - target) <= tol]
