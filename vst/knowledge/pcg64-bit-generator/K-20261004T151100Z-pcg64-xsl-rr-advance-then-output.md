---
id: K-20261004T151100Z-pcg64-xsl-rr-advance-then-output
statement: "numpy default_rng's bit generator (PCG64, XSL-RR 128/64) advances its 128-bit LCG state before producing output from the new state, not output-then-advance; verified bit-exact against np.random.default_rng(seed).bit_generator state and first-N-doubles for 7 seeds."
status: current
supersedes: []
tags: [subject:pcg64-bit-generator, tech:numpy, tech:cpp, phase:implementation]
applies_to_version: "numpy 2.4.4"
source: { url: "", doi: "", title: "Reimplemented and verified against numpy ground truth, not a numpy source read", locator: "vst/src/soc_core.cpp Pcg64::nextUint64; vst/tests/cpp/test_core.cpp T_010", accessed: "2026-10-04", tier: 1 }
confidence: verified
derived_from: []
discovered_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:11:00Z
---
The multiplier is 0x2360ED051FC65DA44385DF649FCCF645; output is rotr64(hi^lo, state>>122). Distinguishing advance-then-output from output-then-advance matters: the two differ by exactly one draw's offset, and only advance-then-output reproduced the fixture.
