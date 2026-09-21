# NOT part of the frozen suite (added after the freeze; see IMPLEMENTATION_REPORT.md).
import numpy as np
import pytest
from consonance.pitchgrid import (DEFAULT_JUST_RATIOS, FREE, STANDARD, candidate_grid, note_name)


def test_standard_mode_yields_only_equal_tempered_degrees():
    g = candidate_grid(STANDARD, -600, 1800)
    assert np.allclose(g % 100.0, 0.0)
    assert g.size == 25 and g.min() == -600 and g.max() == 1800


def test_standard_mode_supports_other_edos():
    g = candidate_grid(STANDARD, 0, 1200, edo=31)
    assert g.size == 32
    assert np.allclose(np.diff(g), 1200 / 31)


def test_standard_mode_excludes_just_major_third():
    assert not np.any(np.isclose(candidate_grid(STANDARD, 0, 1200), 386.3137, atol=1.0))


def test_free_mode_contains_exact_just_ratios():
    g = candidate_grid(FREE, 0, 1200, resolution_cents=5.0)
    for r in DEFAULT_JUST_RATIOS:
        assert np.any(np.isclose(g, 1200 * np.log2(float(r)), atol=1e-6))


def test_free_mode_resolution_and_monotonicity():
    g = candidate_grid(FREE, 0, 1200, resolution_cents=1.0, include_just=False)
    assert g.size == 1201 and np.all(np.diff(g) > 0)


def test_reference_offset_shifts_the_scale():
    assert np.allclose(candidate_grid(STANDARD, 0, 1200, ref_cents=50.0) % 100.0, 50.0)


@pytest.mark.parametrize("kw", [dict(mode="nonsense"), dict(low_cents=100, high_cents=0), dict(edo=0)])
def test_invalid_arguments_rejected(kw):
    args = dict(mode=STANDARD, low_cents=0, high_cents=1200)
    args.update(kw)
    with pytest.raises(ValueError):
        candidate_grid(**args)


def test_note_names():
    assert note_name(0.0, 220.0) == "A3"
    assert note_name(400.0, 220.0) == "C#4"
    assert note_name(386.3137, 220.0).startswith("C#4 -14")
