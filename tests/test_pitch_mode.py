# NOT frozen: added after the freeze (tests/FROZEN.sha256 covers the original suite only).
import numpy as np
import pytest
from consonance.generator import ToneStreamGenerator
from consonance.pitchset import JUST_INTERVALS_CENTS, PitchMode, candidate_cents


def test_standard_mode_yields_only_equal_tempered_notes():
    c = candidate_cents("standard", -600, 1800)
    assert np.allclose(c % 100.0, 0.0)
    assert c.min() == -600.0 and c.max() == 1800.0


def test_standard_mode_honours_edo_and_offset():
    c = candidate_cents(PitchMode.STANDARD, 0, 1200, edo=31)
    assert c.size == 32 and np.allclose(np.diff(c), 1200 / 31)
    assert candidate_cents("standard", 0, 1200, offset_cents=50.0)[0] == 50.0


def test_free_mode_reaches_microtonal_and_just_pitches():
    c = candidate_cents("free", 0, 1200, resolution_cents=1.0)
    assert np.allclose(np.diff(c), 1.0)
    just_third = 1200 * np.log2(5 / 4)            # 386.31 cents, absent from 12-TET
    assert np.abs(c - just_third).min() <= 0.5
    assert not np.allclose(c % 100.0, 0.0)


def test_free_mode_can_snap_to_a_just_lattice():
    c = candidate_cents("free", 0, 2400, snap_to=JUST_INTERVALS_CENTS)
    assert np.abs(c - 1200 * np.log2(3 / 2)).min() < 1e-9
    assert np.abs(c - 1200 * np.log2(3)).min() < 1e-9   # repeated in the next octave
    assert np.abs(c - 100.0).min() > 5.0                 # 12-TET semitone is not on the lattice


def test_invalid_mode_and_range_are_rejected():
    with pytest.raises(ValueError):
        candidate_cents("chromatic-ish", 0, 1200)
    with pytest.raises(ValueError):
        candidate_cents("free", 1200, 0)


def test_generator_switch_changes_the_pitches_but_both_track_the_target():
    out = {}
    for mode in ("standard", "free"):
        g = ToneStreamGenerator(pitch_mode=mode, ref_hz=220.0)
        res, scores = g.generate(target=1.6, n_steps=12, seed=5)
        out[mode] = res.notes
        assert np.mean(np.abs(np.array(scores) - 1.6) <= 0.35) >= 0.75
    assert np.allclose(np.mod(out["standard"], 100.0), 0.0)
    assert not np.allclose(np.mod(out["free"], 100.0), 0.0)


def test_generator_is_deterministic_per_seed():
    a = ToneStreamGenerator(pitch_mode="free").generate(1.2, 8, seed=11)[0].notes
    b = ToneStreamGenerator(pitch_mode="free").generate(1.2, 8, seed=11)[0].notes
    assert a == b
