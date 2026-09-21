# FROZEN — do not modify.
# API: consonance.sampler.metropolis_chord(energy_fn, n_notes, grid_cents, target, sigma, n_steps, rng, burn_in=0) -> np.ndarray[n_steps, n_notes]
#      consonance.sampler.dyad_level_set(dyad_energy_fn, grid_cents, target, tol) -> np.ndarray of grid values
import itertools
import numpy as np
from consonance.sampler import metropolis_chord, dyad_level_set

GRID = np.arange(0, 1200, 100, dtype=float)  # 12 points -> 144 ordered pairs


def pair_energy(chord):
    return abs(chord[0] - chord[1]) / 100.0


def test_metropolis_matches_exact_boltzmann_target():
    target, sigma = 4.0, 1.5
    states = list(itertools.product(GRID, GRID))
    w = np.array([np.exp(-((pair_energy(s) - target) ** 2) / (2 * sigma ** 2)) for s in states])
    p = w / w.sum()
    idx = {s: i for i, s in enumerate(states)}
    r = np.random.default_rng(2024)
    xs = metropolis_chord(pair_energy, 2, GRID, target, sigma, n_steps=200_000, rng=r, burn_in=5_000)
    emp = np.zeros(len(states))
    for a, b in xs:
        emp[idx[(a, b)]] += 1
    emp /= emp.sum()
    assert 0.5 * np.abs(emp - p).sum() < 0.08


def test_dyad_level_set_is_exact_against_brute_force():
    f = lambda c: np.abs(np.asarray(c, dtype=float)) / 100.0
    grid = np.arange(0, 2401, dtype=float)
    got = dyad_level_set(f, grid, target=7.0, tol=0.25)
    want = grid[np.abs(f(grid) - 7.0) <= 0.25]
    assert np.array_equal(np.sort(got), np.sort(want))
