"""Generate consonance-targeted tone streams in each pitch mode and render them to WAV.
Usage: python examples/generate_demo.py [out_dir]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from consonance.generator import ToneStreamGenerator
from consonance.pitchset import JUST_INTERVALS_CENTS
from consonance.render import render_stream

out = sys.argv[1] if len(sys.argv) > 1 else "examples/out"
os.makedirs(out, exist_ok=True)
CASES = [("standard", 0.8, dict(pitch_mode="standard")),
         ("standard", 1.6, dict(pitch_mode="standard")),
         ("standard", 2.0, dict(pitch_mode="standard")),
         ("free", 0.8, dict(pitch_mode="free", resolution_cents=1.0)),
         ("free", 1.6, dict(pitch_mode="free", resolution_cents=1.0)),
         ("free", 2.0, dict(pitch_mode="free", resolution_cents=1.0)),
         ("just", 1.6, dict(pitch_mode="free", snap_to=JUST_INTERVALS_CENTS))]
summary = {}
for tag, target, kw in CASES:
    g = ToneStreamGenerator(ref_hz=220.0, **kw)
    res, scores = g.generate(target=target, n_steps=24, seed=7, start=(0.0, 700.0))
    name = f"{tag}_target_{target:.1f}"
    render_stream(res.notes, g.timbre, os.path.join(out, name + ".wav"), model=g.model, ref_hz=g.ref_hz, sustain_notes=4)
    summary[name] = {"pitch_mode": g.description(), "target": target, "notes_cents_re_220Hz": res.notes,
                     "notes_hz": [round(float(x), 3) for x in g.hz(res.notes)],
                     "realised_scores": scores, "mean_realised": float(np.mean(scores))}
    print(f"{name:20s} {g.description():65s} mean realised {np.mean(scores):.3f}", flush=True)
json.dump(summary, open(os.path.join(out, "streams.json"), "w"), indent=1)
