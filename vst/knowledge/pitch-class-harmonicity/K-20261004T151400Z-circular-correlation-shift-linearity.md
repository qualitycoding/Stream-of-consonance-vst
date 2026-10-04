---
id: K-20261004T151400Z-circular-correlation-shift-linearity
statement: "Circular cross-correlation is linear in its first operand (correlate(A+B, T) = correlate(A, T) + correlate(B, T)), and circularly rotating one operand by k rotates the correlation output by k: correlate(roll(T0, k), template)[b] = correlate(T0, template)[(b - k) mod B]. For Milne/Harrison-Pearce pitch-class harmonicity scored over many integer-cent candidates against the same held notes, this means the full per-candidate correlation vector can be obtained by precomputing two length-B vectors once (correlate(heldSpectrum, template) and correlate(noteSpectrumAtZero, template)) and combining them with an O(1) index shift per candidate, with no per-candidate FFT at all."
status: current
supersedes: []
tags: [subject:pitch-class-harmonicity, tech:cpp, phase:implementation]
applies_to_version: "version-independent (a DSP identity)"
source: { url: "", doi: "", title: "Derived and verified numerically in this run", locator: "vst/src/soc_core.cpp CandidateScorer::score() harmonicity block; verified via np.roll equivalence before porting", accessed: "2026-10-04", tier: 1 }
confidence: verified
derived_from: []
discovered_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:14:00Z
---
A stronger optimization than the plan's own D-004 called for (which only specified the spectrum-rotation half of this, still implying a per-candidate FFT for the correlation/KL step). Brought the harmonicity term's cost for 2401 candidates from the Python reference's ~86ms (post spectrum-rotation) down to a small fraction of the C++ port's total ~50ms score() call.
