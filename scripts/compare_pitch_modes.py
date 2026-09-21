"""Compare pitch modes: how well each tracks a target, and how varied the result is.
Usage: python scripts/compare_pitch_modes.py [out_dir]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from consonance.generator import ToneStreamGenerator
from consonance.pitchset import JUST_INTERVALS_CENTS

TARGETS = [0.8, 1.2, 1.6, 2.0]
SEEDS = [1, 2, 3]
MODES = [("standard (12-TET)", dict(pitch_mode="standard")),
         ("standard (31-EDO)", dict(pitch_mode="standard", edo=31)),
         ("free (1-cent grid)", dict(pitch_mode="free", resolution_cents=1.0)),
         ("free (JI lattice)", dict(pitch_mode="free", snap_to=JUST_INTERVALS_CENTS))]


def main(out_dir):
    rows = []
    for label, kw in MODES:
        for tgt in TARGETS:
            err, hit, dis = [], [], []
            for seed in SEEDS:
                g = ToneStreamGenerator(**kw)
                _, sc = g.generate(target=tgt, n_steps=24, seed=seed)
                e = np.array(sc) - tgt
                err += e.tolist(); hit += (np.abs(e) <= 0.25).tolist()
            rows.append({"mode": label, "n_candidates": int(g.candidates.size), "target": tgt,
                         "mean_error": float(np.mean(err)), "mean_abs_error": float(np.mean(np.abs(err))),
                         "frac_within_0.25": float(np.mean(hit))})
            print(rows[-1], flush=True)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(rows, open(os.path.join(out_dir, "pitch_modes.json"), "w"), indent=1)
    md = ["# Pitch-mode comparison", "",
          "24-note streams, window 4, sigma 0.1, novelty 1.5, seeds 1-3, harmonic timbre (11 partials).", "",
          "| mode | candidates | target | mean err | mean abs err | within ±0.25 |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['mode']} | {r['n_candidates']} | {r['target']:.1f} | {r['mean_error']:+.3f} | "
                  f"{r['mean_abs_error']:.3f} | {r['frac_within_0.25']:.0%} |")
    open(os.path.join(out_dir, "PITCH_MODES.md"), "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs")
