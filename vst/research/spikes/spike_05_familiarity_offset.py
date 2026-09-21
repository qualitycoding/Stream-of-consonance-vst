"""SPIKE-05 — cross-library floating point discrepancy at the familiarity boundary.

Found while implementing S-008 (T-011 failed on free5_t1.6_seed7, diverging from note 2
onward). Root cause: numpy's ARRAY (SIMD-vectorized) log2/pow ufuncs round the last bit
differently from numpy's own SCALAR path for some inputs, and both differ from glibc's
std::log2/std::pow. For a chord landing exactly on familiarity's 20-cent tolerance boundary,
this sub-ULP noise flips the discrete defined/undefined branch.

Fix (implemented in CandidateScorer, not in the general Hz-based compositeScore/
familiarityLogP, which correctly mirror Python's own Hz-round-trip approach and cannot
avoid this in general): compute model-relative cents as
    cents_model[i] = cents_stream[i] + offset,   offset = 1200*log2(refHz/modelRef)
computed ONCE, rather than round-tripping every note through Hz independently. The shared
offset's rounding error cancels exactly in familiarity's rel = x - lo difference.

This script reproduces both the discrepancy and the fix, standalone.
"""
import numpy as np

REF_HZ_STREAM = 220.0
REF_HZ_MODEL = 261.6255653005986


def model_cents_via_hz_roundtrip(streamCents, arrayPath=True):
    c = np.asarray(streamCents, dtype=float)
    freq = REF_HZ_STREAM * (2.0 ** (c / 1200.0) if arrayPath else np.array(
        [2.0 ** (x / 1200.0) for x in c]))
    if arrayPath:
        return 1200.0 * np.log2(freq / REF_HZ_MODEL)
    return np.array([1200.0 * np.log2(f / REF_HZ_MODEL) for f in freq])


def model_cents_via_offset(streamCents):
    offset = 1200.0 * np.log2(REF_HZ_STREAM / REF_HZ_MODEL)
    return np.asarray(streamCents, dtype=float) + offset


if __name__ == "__main__":
    chord = [0.0, 700.0, 930.0, -590.0]   # the exact failing case from free5_t1.6_seed7 step 2

    arr = model_cents_via_hz_roundtrip(chord, arrayPath=True)     # what the Python oracle used
    scalar = model_cents_via_hz_roundtrip(chord, arrayPath=False)  # what naive scalar C++ gave
    offset = model_cents_via_offset(chord)                         # the fix

    for label, cm in [("numpy array (oracle)", arr), ("scalar round-trip (bug)", scalar),
                      ("shared offset (fix)", offset)]:
        lo = cm.min()
        rel = cm - lo
        r = np.round(rel / 100.0)
        diff = rel - 100.0 * r
        print(f"{label:28s} rel[2]={rel[2]!r:24s} diff[2]={diff[2]!r:24s} "
              f">20: {bool(abs(diff[2]) > 20.0)}")

    assert bool(np.abs((model_cents_via_offset(chord) - model_cents_via_offset(chord).min())[2]
                       - 100 * 15) > 20.0) is False, "fix did not resolve the boundary case"
    print("PASS: shared-offset formulation matches the oracle's array-path boundary decision")
