# FROZEN — do not modify. API: consonance.interference.dissonance(freqs_hz, timbre, model="sethares", max_hz=20000.0) -> float >= 0
import numpy as np
import pytest
from consonance.interference import dissonance
from conftest import hz


def erb(f):  # Glasberg & Moore 1990 (definitional constant for this test only)
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def test_unison_pure_tones_have_zero_dissonance(pure):
    assert dissonance([440.0, 440.0], pure) == pytest.approx(0.0, abs=1e-9)


def test_pure_tone_dissonance_peaks_at_a_fraction_of_critical_bandwidth(pure):
    f = 500.0
    seps = np.linspace(0.5, 200.0, 400)
    d = np.array([dissonance([f, f + s], pure) for s in seps])
    peak = seps[int(np.argmax(d))]
    assert 0.05 * erb(f) <= peak <= 0.60 * erb(f)
    assert d[-1] < 0.5 * d.max()
    assert d[0] < d.max()


def test_fifth_less_dissonant_than_tritone_for_harmonic_tones(timbre6):
    fifth = dissonance(hz([0, 702]), timbre6)
    tritone = dissonance(hz([0, 600]), timbre6)
    assert fifth < tritone


def test_minor_second_more_dissonant_than_octave(timbre6):
    assert dissonance(hz([0, 100]), timbre6) > dissonance(hz([0, 1200]), timbre6)


def test_same_ratio_is_more_dissonant_in_low_register(timbre6):
    low = dissonance(hz([0, 386], ref=110.0), timbre6)
    high = dissonance(hz([0, 386], ref=880.0), timbre6)
    assert low > high


def test_order_of_frequencies_is_irrelevant(timbre6):
    a = dissonance(hz([0, 386, 702]), timbre6)
    b = dissonance(hz([702, 0, 386]), timbre6)
    assert a == pytest.approx(b, rel=1e-12)


@pytest.mark.parametrize("bad", [[0.0, 440.0], [-1.0, 440.0], [float("nan"), 440.0], [float("inf"), 440.0]])
def test_invalid_frequencies_are_rejected(bad, pure):
    with pytest.raises(ValueError):
        dissonance(bad, pure)


def test_partials_above_max_hz_are_ignored():
    from consonance.timbre import Timbre
    base = Timbre(ratios=(1, 2, 3), amps=(1.0, 0.5, 0.33))
    loud_ultrasonic = Timbre(ratios=(1, 2, 3, 1000), amps=(1.0, 0.5, 0.33, 50.0))
    f = hz([0, 386])
    assert dissonance(f, loud_ultrasonic, max_hz=20000.0) == pytest.approx(dissonance(f, base), rel=1e-12)
