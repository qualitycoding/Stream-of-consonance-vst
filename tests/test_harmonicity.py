# FROZEN — do not modify. API: consonance.harmonicity.harmonicity(cents, timbre, grid_cents=1.0) -> float >= 0 (pitch-class model)
import numpy as np
import pytest
from consonance.harmonicity import harmonicity

MAJOR = [0, 400, 700]
AUG = [0, 400, 800]


def test_fifth_more_harmonic_than_tritone(timbre6):
    assert harmonicity([0, 700], timbre6) > harmonicity([0, 600], timbre6)


def test_major_triad_more_harmonic_than_augmented_triad(timbre6):
    assert harmonicity(MAJOR, timbre6) > harmonicity(AUG, timbre6)


def test_transposition_invariance_integer_cents(timbre6):
    assert harmonicity([c + 137 for c in MAJOR], timbre6) == pytest.approx(harmonicity(MAJOR, timbre6), rel=1e-9)


def test_octave_equivalence(timbre6):
    assert harmonicity([1200, 400, 700 - 2400], timbre6) == pytest.approx(harmonicity(MAJOR, timbre6), rel=1e-9)


def test_permutation_invariance(timbre6):
    assert harmonicity([700, 0, 400], timbre6) == pytest.approx(harmonicity(MAJOR, timbre6), rel=1e-12)


@pytest.mark.parametrize("chord", [[0], list(range(0, 1200, 100)), [0, 1, 2]])
def test_output_is_finite_and_nonnegative(chord, timbre6):
    v = harmonicity(chord, timbre6)
    assert np.isfinite(v) and v >= 0.0
