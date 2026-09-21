"""SPIKE-01 — per-note generation cost in the Python reference. Informs C-012, R-002, D-002.

Question: can a note be generated inside the audio callback, or does generation need its own
thread with a lookahead queue?
Run: PYTHONPATH=<repo root> python3 spike_01_timing.py
"""
import time
from consonance.generator import ToneStreamGenerator

for mode, kw in [("standard", {}), ("free", {"resolution_cents": 5.0}), ("free", {})]:
    g = ToneStreamGenerator(pitch_mode=mode, **kw)
    t0 = time.perf_counter()
    res, _ = g.generate(target=1.6, n_steps=8, seed=7, start=(0.0, 700.0))
    ms = (time.perf_counter() - t0) / 8 * 1000
    print(f"{mode:9s} {str(kw):28s} {g.candidates.size:5d} candidates  {ms:8.1f} ms/note")
