# FROZEN — the VST test suite

`tests/cpp/test_core.cpp` and everything in `tests/fixtures/` are frozen. Their SHA-256 hashes
are recorded in `tests/FROZEN_MANIFEST.sha256` and checked by `tests/verify_frozen.sh`.

## Immutability rule
An implementing agent may not modify, skip, mark expected-failure, or weaken a frozen test, and
may not regenerate a fixture. The fixtures are the specification: regenerating them is changing
what the software is supposed to do.

## Why the fixtures are the specification
They are golden values captured from the frozen Python `consonance` package at commit `9c8e5e1`,
which is the reference implementation. The C++ port is correct exactly insofar as it reproduces
them. `tests/make_fixtures.py` records how they were produced; it is committed for auditability,
not for routine use.

## Test Challenge procedure
If you believe a frozen test or fixture is *invalid* (not merely inconvenient):

1. Stop. Do not edit anything under `tests/`.
2. Write `vst/TEST_CHALLENGE.md` containing: the test or fixture ID, the exact evidence that it
   is wrong, and your proposed correction.
3. The protocol is re-run from Phase 0. In particular the claim behind the test is re-researched
   before any fixture is regenerated.

A test failing is not evidence that the test is invalid. It is ordinarily evidence that the
implementation is incomplete.

## Red-verification status
The 15 core tests (T-000 … T-014) were compiled and red-verified during planning: they build
clean, load their fixtures, and fail only with not-implemented errors. The recorded output is
`research/spikes/spike_03_red_verify_output.txt`.

The plugin-level tests T-015 … T-020 are **specified but not red-verified**, because JUCE and a
DAW could not be installed in the planning sandbox. This is risk R-005. S-009's `Done when`
requires the implementer to red-verify them against stubs before implementing them.

## What is frozen, exactly
`FROZEN_MANIFEST.sha256` is authoritative. As of this commit it covers exactly:
`tests/cpp/test_core.cpp`, all ten files in `tests/fixtures/`, and `src/soc_core.h`.

There is **one** core test file, `tests/cpp/test_core.cpp`, containing T-000 … T-014. If you
encounter any other file claiming to be a frozen test, it is not covered by the manifest and is
not part of this plan; treat it as spurious and report it via `TEST_CHALLENGE.md`.
