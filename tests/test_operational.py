# FROZEN — do not modify.
# API: CompositeModel.score_with_candidates(held_hz, candidate_hz) -> np.ndarray  (vectorised; one score per candidate)
import time
import numpy as np
import pytest
from consonance.composite import CompositeModel
from consonance.sampler import sample_next
from conftest import hz


@pytest.mark.perf
def test_one_step_over_one_octave_grid_with_six_held_notes_is_under_two_seconds(timbre6):
    m = CompositeModel(timbre6, familiarity_mode="drop")
    held = hz([0, 386, 702, 1088, 1400, 1902])
    grid = np.arange(0, 1200, dtype=float)  # 1200 candidates at 1-cent resolution

    def energy(cands):
        return m.score_with_candidates(held, hz(cands))

    t0 = time.perf_counter()
    sample_next(energy, grid, target=0.0, sigma=0.3, rng=np.random.default_rng(0))
    assert time.perf_counter() - t0 < 2.0


def test_twelve_note_chord_is_finite(timbre6):
    m = CompositeModel(timbre6, familiarity_mode="drop")
    assert np.isfinite(m.score(hz(list(range(0, 1200, 100)))))
