# Research round 1 — decompose and breadth

**Tier:** Opus (decomposition), mechanical retrieval inline.

Built the question tree. Read the whole `consonance` package (796 lines across 12 modules), the
README, and the existing frozen test suite. Established that the repository already carries its
own frozen tests and checkpoints, so the VST work must not write to the repository root (D-008).

New claims: C-001 … C-005, C-007, C-009 (all read directly from source, Tier 1).

Open at end of round: whether the model is fast enough to run in a plugin at all; what the
candidate-scoring cost profile looks like; which JUCE version to pin.
