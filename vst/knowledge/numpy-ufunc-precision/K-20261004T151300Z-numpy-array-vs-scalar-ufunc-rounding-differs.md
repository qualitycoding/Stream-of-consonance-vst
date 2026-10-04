---
id: K-20261004T151300Z-numpy-array-vs-scalar-ufunc-rounding-differs
statement: "On the same numpy version and machine, numpy's array-vectorized (SIMD-dispatched) log2/power ufuncs round the last bit differently from numpy's own scalar-path evaluation of the mathematically identical operation on the identical input; e.g. 220*2**(930/1200) then 1200*log2(f/261.6255653005986) gives exactly 630.0 via the array path but 630.00000000000034 via the scalar path. numpy's own 2.0**x and np.exp2(x) also disagree with each other in the last bit on the same input."
status: current
supersedes: []
tags: [subject:numpy-ufunc-precision, tech:numpy, tech:cpp, phase:implementation]
applies_to_version: "numpy 2.4.4"
source: { url: "", doi: "", title: "Observed directly in this run", locator: "vst/research/spikes/spike_05_familiarity_offset.py; vst/TEST_CHALLENGE.md", accessed: "2026-10-04", tier: 1 }
confidence: verified
derived_from: []
discovered_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:13:00Z
---
Consequence: a reference dataset generated via numpy array operations cannot be reliably reproduced bit-for-bit by a from-scratch C++ port using standard system libm (glibc), for any input landing within about 1 ULP of a discrete threshold in the algorithm. This is a fundamental cross-implementation hazard, not a port defect -- it would require replicating numpy's specific, unversioned, CPU-feature-dependent internal SIMD kernels.
