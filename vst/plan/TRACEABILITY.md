# TRACEABILITY

Every success criterion maps to at least one test; every test maps to a requirement and a step.

| Test | Enforces | Verified claims | Implemented by | Red-verified |
|---|---|---|---|---|
| T-000 | SC-1 (fixture integrity), R-001 | — | S-001 | yes (passes by design) |
| T-001 | SC-1 | C-001 | S-004 | yes |
| T-002 | SC-1 | C-002 | S-004 | yes |
| T-003 | SC-1 | C-003, C-006 | S-005 | yes |
| T-004 | SC-1 | C-004 | S-004 | yes |
| T-005 | SC-1 (boundary) | C-004 | S-004 | yes |
| T-006 | SC-1 | C-005 | S-006 | yes |
| T-007 | SC-1 (invalid input), R-008 | C-002 | S-004 | yes |
| T-008 | SC-2 | C-007 | S-007 | yes |
| T-009 | SC-1, SC-3 | C-005, C-006 | S-006 | yes |
| T-010 | SC-4 | C-008 | S-003 | yes |
| T-011 | SC-4 | C-009 | S-008 | yes |
| T-012 | SC-5 | C-010, C-011 | S-012 | yes |
| T-013 | SC-3 | C-012 | S-006 | yes |
| T-014 | SC-1 (boundary) | C-005 | S-006 | yes |
| T-015 | SC-5 (parameters automatable in host) | — | S-009 | **no — R-005** |
| T-016 | SC-5 (MPE routing in host) | C-015 | S-012 | **no — R-005** |
| T-017 | SC-2 (mode switch drives units and candidates) | C-007 | S-014 | **no — R-005** |
| T-018 | SC-4 (two bounces sample-identical) | C-009 | S-013 | **no — R-005** |
| T-019 | SC-3 (30-minute soak, zero underruns) | C-012 | S-010, S-016 | **no — R-005** |
| T-020 | SC-6 (pluginval strictness 10) | C-014 | S-015 | **no — R-005** |

## Criterion coverage

| Criterion | Covered by |
|---|---|
| SC-1 | T-000 … T-007, T-009, T-014 |
| SC-2 | T-008, T-017 |
| SC-3 | T-013, T-019 |
| SC-4 | T-010, T-011, T-018 |
| SC-5 | T-012, T-015, T-016 |
| SC-6 | T-020 |

## Steps with no test of their own
S-002 (environment), S-017 (re-freeze) and S-018 (documentation) are verified by command output
recorded in the checkpoint rather than by a test. This is intentional and noted here so the
matrix is not mistaken for incomplete.

## Implementation status (core, S-003..S-008)

13/15 core tests pass against the real `soc_core.cpp` (not the stub). T-011 fails on one of
five fixture streams (`free5_t1.6_seed7`) for a documented, isolated reason -- see
TEST_CHALLENGE.md; the other four streams, including the other free-mode stream
(`free1_t1.6_seed3`), reproduce exactly. T-013 fails its 40ms timing budget in the planning
sandbox (measured 48-52ms) -- see DEVIATIONS.md for the likely bottleneck and the legitimate
mitigation path (D-002's resolution ladder), not yet applied pending real-hardware measurement.
