"""S9 validation harness: for each target c*, generate streams with the real composite model and report the realised
consonance (mean/std/|error|), the fraction of steps within tolerance, and simple diversity metrics.
Usage: python scripts/calibration_report.py [out_dir]  (writes calibration.json and CALIBRATION.md)"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from consonance.composite import CompositeModel
from consonance.sampler import generate_stream
from consonance.timbre import harmonic_timbre

REF = 220.0
hz = lambda c: REF * 2.0 ** (np.asarray(c, float) / 1200.0)
TARGETS = [0.4, 0.8, 1.2, 1.6, 2.0, 2.4]
SEEDS = [1, 2, 3]
N_STEPS, WINDOW, SIGMA, TOL = 30, 4, 0.1, 0.25
NOVELTY = float(os.environ.get('NOVELTY', '0'))
CANDS = np.arange(-600.0, 1800.0, 5.0)


def run(out_dir):
    model = CompositeModel(harmonic_timbre(11, 1.0))
    efs = lambda state: (lambda c: model.score_with_candidates(hz(list(state)), hz(c)))
    rows, t0 = [], time.time()
    for tgt in TARGETS:
        errs, reached, pcs, top = [], [], [], []
        for seed in SEEDS:
            r = generate_stream(efs, CANDS, N_STEPS, tgt, SIGMA, seed, start=(0.0, 700.0), window=WINDOW,
                                min_separation_cents=30.0, tolerance=TOL, novelty_weight=NOVELTY)
            state = [0.0, 700.0]
            for n in r.notes:
                state = (state + [n])[-WINDOW:]   # WINDOW notes sound together (matches generate_stream semantics)
                s = model.score(hz(state))
                errs.append(s - tgt); reached.append(abs(s - tgt) <= TOL)
            pc = np.round(np.mod(np.array(r.notes), 1200.0) / 50.0).astype(int) % 24
            pcs.append(len(set(pc.tolist()))); top.append(np.bincount(pc, minlength=24).max() / len(pc))
        e = np.array(errs)
        rows.append({"target": tgt, "mean_error": float(e.mean()), "std": float(e.std()), "mean_abs_error": float(np.abs(e).mean()),
                     "frac_within_tol": float(np.mean(reached)), "distinct_quarter_tone_pcs": float(np.mean(pcs)),
                     "max_pc_share": float(np.mean(top))})
        print(rows[-1], flush=True)
    rng = np.random.default_rng(0)
    att = {}
    for k in (2, 3, 4):
        sc = np.array([model.score(hz(np.sort(rng.choice(CANDS, k, replace=False)))) for _ in range(1500)])
        att[str(k)] = {"min": float(sc.min()), "p5": float(np.percentile(sc, 5)), "median": float(np.median(sc)),
                       "p95": float(np.percentile(sc, 95)), "max": float(sc.max())}
    print("attainable (random search):", att, flush=True)
    os.makedirs(out_dir, exist_ok=True)
    meta = {"timbre": "harmonic, 11 partials, amp 1/h", "sigma": SIGMA, "tolerance": TOL, "window": WINDOW,
            "novelty_weight": NOVELTY, "n_steps": N_STEPS, "seeds": SEEDS, "candidates": "-600..1795 cents re 220 Hz, 5-cent grid", "seconds": time.time() - t0}
    json.dump({"meta": meta, "attainable_random_search": att, "rows": rows}, open(os.path.join(out_dir, "calibration.json"), "w"), indent=1)
    md = ["# Calibration report (model-consonance, not perceptual)", "",
          f"Setup: {json.dumps(meta)}", "",
          "| target c* | mean err | std | mean abs err | within ±%.2f | distinct pcs (quarter-tone bins, of 30 notes) | max pc share |" % TOL,
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['target']:.1f} | {r['mean_error']:+.3f} | {r['std']:.3f} | {r['mean_abs_error']:.3f} | {r['frac_within_tol']:.0%} | {r['distinct_quarter_tone_pcs']:.1f} | {r['max_pc_share']:.0%} |")
    md += ["", "Attainable model-consonance by sonority size (1500 random chords each, so extremes are underestimated):", "",
           "| notes | min | p5 | median | p95 | max |", "|---|---|---|---|---|---|"]
    for k, a in att.items():
        md.append(f"| {k} | {a['min']:.2f} | {a['p5']:.2f} | {a['median']:.2f} | {a['p95']:.2f} | {a['max']:.2f} |")
    open(os.path.join(out_dir, "CALIBRATION.md"), "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "docs")
