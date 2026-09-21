# FROZEN — do not modify.
# API: consonance.composite.CompositeModel(timbre, weights=None, familiarity_mode="drop"|"strict")
#      .features(freqs_hz)->dict(interference,harmonicity,familiarity|None,n_notes) ; .score(freqs_hz)->float ; .check_timbre(t)
#      consonance.composite.Weights(interference,harmonicity,familiarity,n_notes,intercept) ; UnsupportedTuningError ; TimbreMismatchError
import numpy as np
import pytest
from consonance.composite import CompositeModel, Weights, UnsupportedTuningError, TimbreMismatchError
from consonance.timbre import Timbre
from conftest import hz


def test_score_is_exact_linear_combination_of_features(timbre6):
    w = Weights(interference=-0.7, harmonicity=0.9, familiarity=0.5, n_notes=-0.1, intercept=0.3)
    m = CompositeModel(timbre6, weights=w)
    f = hz([0, 400, 700])
    ft = m.features(f)
    expected = w.intercept + w.interference * ft["interference"] + w.harmonicity * ft["harmonicity"] \
        + w.familiarity * ft["familiarity"] + w.n_notes * ft["n_notes"]
    assert m.score(f) == pytest.approx(expected, rel=1e-12)


def test_default_weight_signs_follow_published_directions(timbre6):
    w = CompositeModel(timbre6).weights
    assert w.interference < 0 and w.harmonicity > 0 and w.familiarity > 0


def test_major_triad_outscores_augmented_and_cluster(timbre6):
    m = CompositeModel(timbre6)
    major = m.score(hz([0, 400, 700]))
    assert major > m.score(hz([0, 400, 800]))
    assert major > m.score(hz([0, 100, 200]))


def test_microtonal_chord_scores_when_familiarity_dropped(timbre6):
    m = CompositeModel(timbre6, familiarity_mode="drop")
    f = hz([0, 6 * 38.7097, 18 * 38.7097])  # 31-EDO steps
    assert m.features(f)["familiarity"] is None
    assert np.isfinite(m.score(f))


def test_microtonal_chord_raises_in_strict_mode(timbre6):
    m = CompositeModel(timbre6, familiarity_mode="strict")
    with pytest.raises(UnsupportedTuningError):
        m.score(hz([0, 6 * 38.7097, 18 * 38.7097]))


def test_timbre_mismatch_is_detected(timbre6):
    m = CompositeModel(timbre6)
    other = Timbre(ratios=(1, 2.76, 5.4), amps=(1.0, 0.6, 0.3))
    with pytest.raises(TimbreMismatchError):
        m.check_timbre(other)
    m.check_timbre(timbre6)  # same timbre must not raise
