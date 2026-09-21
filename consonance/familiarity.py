"""Corpus-based cultural familiarity: log-probability of a chord's pitch-class chord type (bass-relative pitch-class
set) in the McGill Billboard corpus, add-one smoothed. Data and encoding taken from the MIT-licensed R package `incon`
(see NOTICE). Defined for 12-tone-equal-tempered chords only."""
from __future__ import annotations
import json
import math
import os
from functools import lru_cache

import numpy as np

_DATA = os.path.join(os.path.dirname(__file__), "data", "billboard_pc_chord_type_counts.json")
TOLERANCE_CENTS = 20.0


@lru_cache(maxsize=1)
def _table():
    with open(_DATA) as fh:
        counts = np.asarray(json.load(fh)["counts"], dtype=float)
    p = (counts + 1.0) / (counts + 1.0).sum()
    return np.log(p), float((counts / counts.sum() * np.log(p)).sum())


def neutral_log_prob() -> float:
    """Count-weighted mean log-probability of a chord type (used when the tuning is unsupported and mode='drop')."""
    return _table()[1]


def chord_type_id(rel_pcs) -> int:
    return 1 + sum(2 ** (11 - j) for j in rel_pcs if j >= 1)


def chord_type_from_cents(cents_abs) -> frozenset | None:
    """Bass-relative 12-TET pitch-class set, or None if any interval is > TOLERANCE_CENTS from equal temperament."""
    c = [float(x) for x in cents_abs]
    lo = min(c)
    pcs = set()
    for x in c:
        rel = x - lo
        r = round(rel / 100.0)
        if abs(rel - 100.0 * r) > TOLERANCE_CENTS:
            return None
        pcs.add(int(r) % 12)
    pcs.add(0)
    return frozenset(pcs)


def log_prob_of_type(chord_type: frozenset) -> float:
    return float(_table()[0][chord_type_id(chord_type) - 1])


def familiarity_from_cents(cents_abs) -> float | None:
    t = chord_type_from_cents(cents_abs)
    return None if t is None else log_prob_of_type(t)
