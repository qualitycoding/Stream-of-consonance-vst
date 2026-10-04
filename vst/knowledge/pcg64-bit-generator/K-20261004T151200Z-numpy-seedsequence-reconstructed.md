---
id: K-20261004T151200Z-numpy-seedsequence-reconstructed
statement: "numpy's SeedSequence entropy-mixing algorithm (hashmix/mix functions over a 4-word uint32 pool, generate_state producing 8 uint32 words = 4 uint64 for PCG64's initstate/initseq) was reverse-engineered from scratch, with no authoritative spec consulted, and verified bit-exact against np.random.default_rng(seed).bit_generator.state for 7 seeds, for integer seeds under 2^32."
status: current
supersedes: []
tags: [subject:pcg64-bit-generator, tech:numpy, tech:cpp, phase:implementation]
applies_to_version: "numpy 2.4.4"
source: { url: "", doi: "", title: "Reimplemented and verified against numpy ground truth", locator: "vst/src/soc_core.cpp (hashmix, mix32, mixEntropy, generateStateU32); vst/research/spikes/spike_04_seedsequence.py", accessed: "2026-10-04", tier: 1 }
confidence: verified
derived_from: []
discovered_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:12:00Z
---
Constants: XSHIFT=16, INIT_A=0x43b0d7e5, MULT_A=0x931e8875, INIT_B=0x8b51f9dd, MULT_B=0x58f38ded, MIX_MULT_L=0xca01f9dd, MIX_MULT_R=0x4973f715. PCG64 seeding then applies pcg_setseq_128_srandom_r: inc=(initseq<<1)|1, state=0, state=state*mult+inc, state+=initstate, state=state*mult+inc.
