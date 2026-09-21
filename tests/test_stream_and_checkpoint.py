# FROZEN — do not modify.
# API: consonance.sampler.generate_stream(energy_for_state, candidates_cents, n_steps, target, sigma, rng_seed,
#          start=(), checkpoint=None, checkpoint_every=5, max_steps_this_run=None) -> StreamResult(notes: list[float], complete: bool)
#      consonance.checkpoint.Checkpoint(path): .save(dict) atomic + keeps <path>.bak ; .load()->dict|None ; .recovered: bool
#      consonance.checkpoint.CheckpointVersionError
import json
import os
import numpy as np
import pytest
from consonance.sampler import generate_stream
from consonance.checkpoint import Checkpoint, CheckpointVersionError

GRID = np.arange(0, 1201, dtype=float)


def efs(state):
    return lambda c: np.asarray(c, dtype=float) / 100.0


def run(**kw):
    return generate_stream(efs, GRID, n_steps=40, target=5.0, sigma=0.1, rng_seed=99, **kw)


def test_every_step_lands_near_target():
    notes = run().notes
    assert len(notes) == 40
    assert all(abs(n / 100.0 - 5.0) < 0.5 for n in notes)


def test_interrupted_run_resumes_to_identical_stream(tmp_path):
    ref = run()
    ck = Checkpoint(str(tmp_path / "state.json"))
    part = run(checkpoint=ck, checkpoint_every=5, max_steps_this_run=17)
    assert part.complete is False
    full = run(checkpoint=ck, checkpoint_every=5)
    assert full.complete is True
    assert full.notes == ref.notes


def test_checkpoint_roundtrip(tmp_path):
    ck = Checkpoint(str(tmp_path / "state.json"))
    ck.save({"step": 3, "notes": [1.0, 2.0]})
    assert ck.load()["step"] == 3


def test_corrupt_latest_falls_back_to_backup(tmp_path):
    p = tmp_path / "state.json"
    ck = Checkpoint(str(p))
    ck.save({"step": 1})
    ck.save({"step": 2})
    p.write_text("{not json")
    got = ck.load()
    assert got["step"] == 1 and ck.recovered is True


def test_crash_during_write_leaves_previous_state_intact(tmp_path, monkeypatch):
    ck = Checkpoint(str(tmp_path / "state.json"))
    ck.save({"step": 1})
    monkeypatch.setattr(os, "replace", lambda *a, **k: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        ck.save({"step": 2})
    monkeypatch.undo()
    assert Checkpoint(str(tmp_path / "state.json")).load()["step"] == 1


def test_unknown_schema_version_is_refused(tmp_path):
    p = tmp_path / "state.json"
    p.write_text(json.dumps({"schema_version": 999, "step": 1}))
    with pytest.raises(CheckpointVersionError):
        Checkpoint(str(p)).load()
