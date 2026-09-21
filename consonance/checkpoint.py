"""Atomic, versioned JSON checkpoints with a rolling backup."""
from __future__ import annotations
import json
import os

SCHEMA_VERSION = 1


class CheckpointVersionError(RuntimeError):
    pass


class Checkpoint:
    def __init__(self, path: str):
        self.path = path
        self.bak = path + ".bak"
        self.recovered = False

    @staticmethod
    def _read(p):
        with open(p) as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("checkpoint is not an object")
        if data.get("schema_version") != SCHEMA_VERSION:
            raise CheckpointVersionError(f"unsupported checkpoint schema_version {data.get('schema_version')!r}")
        return data

    def save(self, state: dict) -> None:
        data = dict(state)
        data["schema_version"] = SCHEMA_VERSION
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w") as fh:
                json.dump(data, fh)
                fh.flush()
                os.fsync(fh.fileno())
            if os.path.exists(self.path):
                try:
                    self._read(self.path)
                    rotate = True
                except CheckpointVersionError:
                    rotate = True
                except ValueError:                  # corrupt current file: never let it overwrite a good backup
                    rotate = False
                if rotate:
                    os.replace(self.path, self.bak)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    def load(self):
        self.recovered = False
        if os.path.exists(self.path):
            try:
                return self._read(self.path)
            except CheckpointVersionError:
                raise
            except (ValueError, OSError):
                pass
        if os.path.exists(self.bak):
            data = self._read(self.bak)            # version errors propagate
            self.recovered = True
            return data
        return None
