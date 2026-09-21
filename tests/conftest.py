# FROZEN — do not modify (see tests/FROZEN.md)
import numpy as np
import pytest


@pytest.fixture
def rng():
    return np.random.default_rng(12345)


@pytest.fixture
def timbre6():
    from consonance.timbre import Timbre
    return Timbre(ratios=tuple(range(1, 7)), amps=tuple(1.0 / k for k in range(1, 7)))


@pytest.fixture
def pure():
    from consonance.timbre import Timbre
    return Timbre(ratios=(1,), amps=(1.0,))


def hz(cents, ref=220.0):
    return ref * 2.0 ** (np.asarray(cents, dtype=float) / 1200.0)
