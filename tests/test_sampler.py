# FROZEN — do not modify.
# API: consonance.sampler.sample_next(energy_fn, candidates_cents, target, sigma, rng, exclude=(), tolerance=0.05) -> SampleResult(cents, value, reached)
#      energy_fn(np.ndarray[float]) -> np.ndarray[float]  (vectorised consonance of state ∪ candidate)
import numpy as np
import pytest
from consonance.sampler import sample_next

GRID = np.arange(0, 1201, dtype=float)


def C(c):  # synthetic, exactly invertible energy: value = cents/100
    return np.asarray(c, dtype=float) / 100.0


def draw(n, sigma, target=5.0, seed=1, **kw):
    r = np.random.default_rng(seed)
    return np.array([sample_next(C, GRID, target, sigma, r, **kw).cents for _ in range(n)])


def test_samples_follow_the_analytic_gaussian_target():
    x = draw(3000, sigma=0.1)          # theory: mean 500 cents, std 10 cents
    assert abs(x.mean() - 500.0) < 3.0
    assert 8.0 < x.std() < 12.0


def test_larger_sigma_gives_wider_spread():
    assert draw(1500, 0.3).std() > 2.0 * draw(1500, 0.1).std()


def test_same_seed_same_draws_different_seed_differs():
    assert np.array_equal(draw(50, 0.2, seed=7), draw(50, 0.2, seed=7))
    assert not np.array_equal(draw(50, 0.2, seed=7), draw(50, 0.2, seed=8))


def test_vanishing_sigma_returns_exact_argmin():
    r = np.random.default_rng(0)
    assert sample_next(C, GRID, 5.0, 1e-6, r).cents == 500.0


def test_unreachable_target_is_numerically_stable_and_flagged():
    r = np.random.default_rng(0)
    res = sample_next(C, GRID, 1e9, 0.1, r)
    assert np.isfinite(res.value) and res.cents == 1200.0 and res.reached is False


def test_reached_flag_true_when_within_tolerance():
    r = np.random.default_rng(0)
    assert sample_next(C, GRID, 5.0, 1e-6, r, tolerance=0.05).reached is True


def test_excluded_candidates_are_never_returned():
    x = draw(500, 0.1, exclude=tuple(range(495, 506)))
    assert not np.isin(x, np.arange(495, 506)).any()
