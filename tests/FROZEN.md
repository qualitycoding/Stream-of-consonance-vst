# FROZEN TEST SUITE
Status: FROZEN at generation time. Implementing agents must NOT modify, skip, xfail, deselect, or adapt any file listed in FROZEN.sha256.
Reset Rule: if a test is judged invalid, halt, reopen the protocol, and re-run from Phase 0 (new generation branch).
Verify integrity: `sha256sum -c tests/FROZEN.sha256` (run from repo root). Expected initial state is RED (ModuleNotFoundError: consonance) — that is TDD, not a defect.
Design rule used: assertions are literature orderings, exact linear/analytic identities, or seeded statistical bounds derived analytically — no unvalidated magic numbers except the one performance budget (test_operational.py, marked `perf`).
