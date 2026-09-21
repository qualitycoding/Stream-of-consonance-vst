# Pre-mortem round 1

*It is March 2027. The plugin shipped, and it has failed.*

**Incident report.** The instrument loaded and made sound, so nobody looked closely for months.
What users eventually reported was vaguer: "the consonance knob doesn't really do anything at the
low end", and "it sounds different from the Python demos". Both had the same root cause. The C++
port converted the fixtures' `cents` using `REF_HZ`, the constant defined at the top of
`composite.py` — the obvious choice, since it is the only reference the model file names. But the
fixtures were generated at 220 Hz. Roughness depends on frequency through critical bandwidth, so
every score was off by up to 0.082. The sampler faithfully hit the *wrong* level set. No test
caught it, because the unit tests were written from the same misreading. The bug was invisible,
self-consistent, and audible only as a vague wrongness.

**Lenses examined:** technical correctness, scale/performance, dependency drift, invalid research
assumptions, security/licensing, operational reality, implementer misinterpretation.

**Findings:** R-001 (Critical), R-002 (High), R-003 (High), R-004 (High), R-005 (High),
R-007, R-009, R-010, R-011.

**Plan hardening applied:**
* `make_fixtures.py` now injects `ref_hz` and an explanatory note into every fixture; fixtures
  regenerated and re-verified (composite reproduces with error exactly 0.0 at 220 Hz, and fails
  all 13 cases at C4, confirming the hazard was real).
* **New test T-000** added: it loads every fixture, asserts `ref_hz` is declared and equals 220,
  and deliberately calls no `soc::` function — so it passes in the red state and proves the other
  tests' inputs exist. Added through the Phase 2 procedure: unfreeze, add, red-verify, re-freeze.
* `soc_core.h` gained both constants with a comment stating which is which and what confusing
  them costs.
* D-007 added (both start parameters permanent) closing R-004.
* A contradiction was found between two frozen artifacts: `soc_core.h` defaulted the MPE bend
  range to 48 semitones while `mpe.json` records 2. The header was corrected to 2 and D-006
  written. This is the class of defect the Cold-Read Gate exists to catch.
