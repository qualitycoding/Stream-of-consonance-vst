# Mutation testing design — priced three-tier, one aggregator (v3.9)

**Repository:** `qualitycoding/Stream-of-consonance-vst`. **Tool:** Mull for the C++ VST plugin
scope; mutmut for the Python harness scope; both pinned after existence
checks.

## Pricing
- Fast-test time: estimate from repo size (~36 source files) — **estimate, first CI run confirms** (D-905).
- Budgets: incremental 20 min; scheduled full 120 min; deterministic sharding beyond budget.
- Post-conditions: non-empty parseable report, >= 10 mutants (>= 1 with small-scope D-ID).

## Triggers
Incremental on PR/push scoped to changed mutable files (`not-applicable`
otherwise); weekly scheduled full run with `qualitycoding` as named owner;
workflow_dispatch; killing-test/config changes force full run.

## Aggregator / gate
One always-running aggregator is the only required status; score computed
from the tool report; below-floor fixture demonstrated in CI; floor set five
points below the first measured score; survivors justified or killed.

## Status
First run and floor calibration **pending in CI** (D-905; nothing unrun
claimed as passed).
