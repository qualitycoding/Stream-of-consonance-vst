"""Additive-synthesis renderer using the SAME Timbre object the model scores (guards against timbre mismatch)."""
from __future__ import annotations
import wave
import numpy as np
from .composite import CompositeModel
from .timbre import Timbre


def render_stream(notes_cents, timbre: Timbre, path: str, model: CompositeModel | None = None, ref_hz: float = 220.0,
                  note_dur: float = 0.5, sustain_notes: int = 4, sr: int = 44100, max_hz: float = 20000.0) -> str:
    """Each note starts every `note_dur` s and sounds for `sustain_notes*note_dur` s (sliding sonority of that many notes)."""
    if model is not None:
        model.check_timbre(timbre)
    dur = note_dur * (len(notes_cents) + sustain_notes) + 0.3
    y = np.zeros(int(dur * sr))
    ratios, amps = np.asarray(timbre.ratios), np.asarray(timbre.amps)
    for k, c in enumerate(notes_cents):
        f0 = ref_hz * 2.0 ** (c / 1200.0)
        n = int(note_dur * sustain_notes * sr)
        t = np.arange(n) / sr
        tone = np.zeros(n)
        for r, a in zip(ratios, amps):
            if f0 * r < max_hz:
                tone += a * np.sin(2 * np.pi * f0 * r * t)
        att, rel = int(0.02 * sr), int(0.25 * sr)
        env = np.ones(n)
        env[:att] = np.linspace(0, 1, att)
        env[-rel:] = np.linspace(1, 0, rel)
        s = int(k * note_dur * sr)
        y[s:s + n] += tone * env
    y /= max(1e-9, np.max(np.abs(y))) / 0.8
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((y * 32767).astype("<i2").tobytes())
    return path
