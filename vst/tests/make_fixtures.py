"""Generate golden fixtures from the Python `consonance` package.

These files ARE the specification for the C++ port: every C++ unit test asserts against them.
Regenerating them is equivalent to changing the spec and requires the Phase 2 unfreeze procedure
(see tests/FROZEN.md and plan/PLAN.md S-012).

Run from the repository root:  PYTHONPATH=. python vst/tests/make_fixtures.py
"""
from __future__ import annotations

import hashlib
import json
import os

import numpy as np

from consonance import familiarity as fam
from consonance.composite import REF_HZ, CompositeModel
from consonance.generator import ToneStreamGenerator
from consonance.harmonicity import harmonicity
from consonance.interference import dissonance
from consonance.pitchset import JUST_INTERVALS_CENTS, candidate_cents
from consonance.timbre import harmonic_timbre

OUT = os.path.join(os.path.dirname(__file__), "fixtures")
TIMBRE = harmonic_timbre(11, 1.0)
REF_A3 = 220.0

CHORDS_CENTS = {
    "unison": [0.0],
    "octave": [0.0, 1200.0],
    "perfect_fifth": [0.0, 700.0],
    "tritone": [0.0, 600.0],
    "minor_second": [0.0, 100.0],
    "major_triad": [0.0, 400.0, 700.0],
    "minor_triad": [0.0, 300.0, 700.0],
    "diminished_triad": [0.0, 300.0, 600.0],
    "dominant_seventh": [0.0, 400.0, 700.0, 1000.0],
    "cluster": [0.0, 100.0, 200.0, 300.0],
    "ji_major_triad": [0.0, 386.3137138648348, 701.9550008653874],
    "microtonal_quartertone": [0.0, 350.0, 750.0],
    "wide_spread": [-600.0, 0.0, 700.0, 1750.0],
}


def hz(cents, ref=REF_A3):
    return ref * 2.0 ** (np.asarray(cents, dtype=float) / 1200.0)


def write(name, payload):
    # Every fixture states its own cents reference. Without this a reader cannot tell whether
    # `cents` is relative to 220 Hz (the generator reference) or to C4 261.6255... (the model's
    # internal pitch-class origin). Choosing wrongly does not raise -- it silently shifts the
    # roughness term by up to 0.08 score units. See premortem R-001.
    if isinstance(payload, dict) and "ref_hz" not in payload:
        payload = dict(payload)
        payload["ref_hz"] = REF_A3
        payload["ref_hz_note"] = (
            "All `cents` values in this file are relative to ref_hz. Convert with "
            "f = ref_hz * 2**(cents/1200). Do NOT use composite.REF_HZ (C4) here: that constant "
            "only fixes the pitch-class origin inside the harmonicity term."
        )
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print(f"  {name:<34} {digest[:16]}  {os.path.getsize(path):>8} bytes")
    return digest


def f_timbre():
    return {"ratios": list(TIMBRE.ratios), "amps": list(TIMBRE.amps),
            "n_harmonics": 11, "roll_off": 1.0, "ref_hz_model": REF_HZ, "ref_hz_generator": REF_A3}


def f_interference():
    rows = []
    for name, cents in CHORDS_CENTS.items():
        f = hz(cents)
        rows.append({"name": name, "cents": cents, "freqs_hz": [float(x) for x in f],
                     "hutchinson": dissonance(f, TIMBRE, "hutchinson"),
                     "sethares": dissonance(f, TIMBRE, "sethares"),
                     "vassilakis": dissonance(f, TIMBRE, "vassilakis")})
    return {"tolerance_abs": 1e-9, "cases": rows}


def f_harmonicity():
    rows = [{"name": n, "cents": c, "bits": harmonicity(np.asarray(c) + 1200.0 * np.log2(REF_A3 / REF_HZ), TIMBRE)}
            for n, c in CHORDS_CENTS.items()]
    return {"tolerance_abs": 1e-9, "grid_cents": 1.0, "sigma_cents": 6.83, "rho_exponent": 0.75, "cases": rows}


def f_familiarity():
    rows = []
    for name, cents in CHORDS_CENTS.items():
        t = fam.chord_type_from_cents(cents)
        rows.append({"name": name, "cents": cents,
                     "supported": t is not None,
                     "chord_type_pcs": sorted(t) if t is not None else None,
                     "chord_type_id": fam.chord_type_id(sorted(t)) if t is not None else None,
                     "log_prob": fam.familiarity_from_cents(cents)})
    return {"tolerance_abs": 1e-12, "neutral_log_prob": fam.neutral_log_prob(),
            "tolerance_cents": fam.TOLERANCE_CENTS, "cases": rows}


def f_composite():
    m = CompositeModel(TIMBRE)
    rows = []
    for name, cents in CHORDS_CENTS.items():
        ft = m.features(hz(cents))
        rows.append({"name": name, "cents": cents, "score": m.score(hz(cents)),
                     "features": {k: (None if v is None else float(v)) for k, v in ft.items()}})
    w = m.weights
    return {"tolerance_abs": 1e-9,
            "weights": {"interference": w.interference, "harmonicity": w.harmonicity,
                        "familiarity": w.familiarity, "n_notes": w.n_notes, "intercept": w.intercept},
            "cases": rows}


def f_candidates():
    rows = []
    for label, kw in [("standard_12tet", dict(mode="standard", edo=12)),
                      ("standard_31edo", dict(mode="standard", edo=31)),
                      ("standard_19edo", dict(mode="standard", edo=19)),
                      ("free_1cent", dict(mode="free", resolution_cents=1.0)),
                      ("free_5cent", dict(mode="free", resolution_cents=5.0)),
                      ("free_ji", dict(mode="free", snap_to=JUST_INTERVALS_CENTS))]:
        mode = kw.pop("mode")
        c = candidate_cents(mode, -600.0, 1800.0, **kw)
        rows.append({"name": label, "mode": mode, "params": kw, "low_cents": -600.0, "high_cents": 1800.0,
                     "n": int(c.size), "first": float(c[0]), "last": float(c[-1]),
                     "integer_cent_grid": bool(np.allclose(c, np.rint(c))),
                     "sha256_of_values": hashlib.sha256(
                         ",".join(f"{x:.9f}" for x in c).encode()).hexdigest(),
                     "sample": [float(x) for x in c[:12]]})
    return {"tolerance_abs": 1e-9, "cases": rows}


def f_score_with_candidates():
    """The plugin's hot path: held sonority + every candidate, scored in one batch."""
    m = CompositeModel(TIMBRE)
    rows = []
    for label, held_cents, cand_kw in [
        ("empty_held_12tet", [], dict(mode="standard", edo=12)),
        ("triad_held_12tet", [0.0, 400.0, 700.0], dict(mode="standard", edo=12)),
        ("dyad_held_free5", [0.0, 700.0], dict(mode="free", resolution_cents=5.0)),
    ]:
        mode = cand_kw.pop("mode")
        cand = candidate_cents(mode, -600.0, 1800.0, **cand_kw)
        vals = m.score_with_candidates(hz(held_cents) if held_cents else np.empty(0), hz(cand))
        rows.append({"name": label, "held_cents": held_cents, "candidate_mode": mode, "candidate_params": cand_kw,
                     "n_candidates": int(cand.size),
                     "values": [float(v) for v in vals]})
    return {"tolerance_abs": 1e-9, "cases": rows}


def f_streams():
    """End-to-end determinism: same seed + config must reproduce these exact note sequences."""
    rows = []
    for label, kw, gen in [
        ("standard_t1.6_seed7", dict(pitch_mode="standard"), dict(target=1.6, n_steps=24, seed=7, start=(0.0, 700.0))),
        ("standard_t0.8_seed1", dict(pitch_mode="standard"), dict(target=0.8, n_steps=16, seed=1, start=(0.0,))),
        ("standard_t2.0_seed42", dict(pitch_mode="standard"), dict(target=2.0, n_steps=16, seed=42, start=(300.0,))),
        ("free5_t1.6_seed7", dict(pitch_mode="free", resolution_cents=5.0), dict(target=1.6, n_steps=12, seed=7, start=(0.0, 700.0))),
        ("free1_t1.6_seed3", dict(pitch_mode="free", resolution_cents=1.0), dict(target=1.6, n_steps=8, seed=3, start=(0.0,))),
    ]:
        g = ToneStreamGenerator(**kw)
        res, scores = g.generate(**gen)
        cfg = dict(gen)
        cfg["start"] = list(cfg["start"])
        rows.append({"name": label, "generator": kw, "call": cfg,
                     "description": g.description(),
                     "sigma": g.sigma, "window": g.window, "novelty_weight": g.novelty_weight,
                     "min_separation_cents": g.min_separation_cents,
                     "notes_cents": [float(x) for x in res.notes],
                     "notes_hz": [float(x) for x in g.hz(res.notes)],
                     "realised_scores": [float(x) for x in scores],
                     "within_tolerance_frac": float(np.mean(np.abs(np.asarray(scores) - gen["target"]) <= 0.25))})
    return {"tolerance_cents": 1e-6, "tolerance_score_abs": 1e-9, "cases": rows}


def f_mpe():
    """Expected MPE encoding of free-mode pitches (D-004: +/-2 semitone per-note bend range)."""
    bend_range = 2.0
    rows = []
    for cents in [0.0, 1.0, -1.0, 49.0, 50.0, -50.0, 386.3137138648348, 701.9550008653874, 1750.0, -600.0]:
        f = REF_A3 * 2.0 ** (cents / 1200.0)
        midi_exact = 69.0 + 12.0 * np.log2(f / 440.0)
        note = int(np.rint(midi_exact))
        offset = (midi_exact - note) * 100.0
        val = int(np.clip(round(8192 + offset / (bend_range * 100.0) * 8191.5), 0, 16383))
        produced = (val - 8192) / 8191.5 * bend_range * 100.0
        rows.append({"cents_rel_ref": cents, "freq_hz": float(f), "midi_note": note,
                     "offset_cents": float(offset), "bend14": val,
                     "produced_offset_cents": float(produced),
                     "error_cents": float(produced - offset)})
    return {"bend_range_semitones": bend_range, "rpn": "0,0", "centre": 8192,
            "max_error_cents": 0.05, "zone": "lower, master ch 1, members ch 2-16", "cases": rows}


def f_rng():
    """numpy's PCG64 stream, which the C++ port must reproduce bit-for-bit or T-050 is unreachable.

    default_rng(seed) = SeedSequence(seed) -> 128-bit PCG64 state/inc; Generator.random() is
    (next_uint64 >> 11) * 2**-53. All three pieces must be ported exactly.
    """
    rows = []
    for seed in (0, 1, 3, 7, 42, 12345, 2**31 - 1):
        r = np.random.default_rng(seed)
        inner = r.bit_generator.state["state"]
        raw = [int(x) for x in np.random.default_rng(seed).bit_generator.random_raw(8)]
        r2 = np.random.default_rng(seed)
        rows.append({
            "seed": seed,
            "initial_state_hex": hex(inner["state"]),
            "initial_inc_hex": hex(inner["inc"]),
            "first_raw_uint64_hex": [hex(x) for x in raw],
            "first_doubles": [float(r2.random()) for _ in range(8)],
        })
    return {"bit_generator": "PCG64 (XSL-RR 128/64)", "seeding": "numpy SeedSequence",
            "double_from_raw": "(raw >> 11) * 2**-53", "tolerance_abs": 0.0, "cases": rows}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("writing golden fixtures ->", OUT)
    digests = {}
    for name, fn in [("timbre.json", f_timbre), ("interference.json", f_interference),
                     ("harmonicity.json", f_harmonicity), ("familiarity.json", f_familiarity),
                     ("composite.json", f_composite), ("candidates.json", f_candidates),
                     ("score_with_candidates.json", f_score_with_candidates),
                     ("streams.json", f_streams), ("mpe.json", f_mpe),
                     ("rng.json", f_rng)]:
        digests[name] = write(name, fn())
    with open(os.path.join(OUT, "MANIFEST.sha256"), "w") as fh:
        for n in sorted(digests):
            fh.write(f"{digests[n]}  {n}\n")
    print("done")
