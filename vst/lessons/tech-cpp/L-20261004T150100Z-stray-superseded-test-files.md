---
id: L-20261004T150100Z-stray-superseded-test-files
title: "Two superseded test files with FROZEN headers and a contradictory test-ID scheme sat alongside the real frozen suite"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: High
tags: [tech:cpp, phase:verification, kind:integrity]
recorded_by: planner
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:01:00Z
---
## Trigger
A generation branch's tests/cpp/ directory is about to be frozen (manifest written) after other files may already have been written into the same tree during the run.
## What went wrong
tests/cpp/test_model_port.cpp and tests/cpp/test_plugin_behaviour.cpp carried FROZEN headers, claimed manifest coverage they did not have, used a contradictory test-ID scheme (T-020..T-070) against an earlier draft of the success criteria, and referenced a Catch2 dependency the plan never established. Found only during the Phase 5 final consistency check, by actually listing every file under tests/cpp/ rather than trusting that only the files I had deliberately written were there.
## Correction
Removed both files, added a note to tests/FROZEN.md stating the manifest is authoritative and test_core.cpp is the only core test file, and re-verified the freeze.
## Prevention rule
Before writing FROZEN_MANIFEST.sha256, run `find tests/ -type f` (not just `ls` on the files you intended to create) and account for every file present, not only the ones you wrote.
## Detection check
find tests/cpp -name '*.cpp' | wc -l should equal 1 (test_core.cpp) before freezing; any other .cpp file under tests/cpp is unaccounted for.
## Evidence
Phase-5 final-consistency-check commit message ("Final consistency check removed two superseded test files..."). Recorded retroactively when the addendum was adopted mid-run.
