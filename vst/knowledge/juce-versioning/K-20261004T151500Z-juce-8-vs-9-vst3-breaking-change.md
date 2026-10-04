---
id: K-20261004T151500Z-juce-8-vs-9-vst3-breaking-change
statement: "JUCE's 8.x line runs through tag 8.0.15; the 9.x line (9.0.0, 2026-07-21, through 9.0.2, 2026-09-07) restructures the VST3 client extension API, moving functionality out of VST3ClientExtensions into a new VST3Interface struct behind a JUCE_VST3_COMPATIBLE_CLASSES define, among 35+ other breaking changes listed in JUCE's own BREAKING_CHANGES.md."
status: current
supersedes: []
tags: [subject:juce-versioning, tech:juce, phase:specification]
applies_to_version: "JUCE 8.0.15 and 9.0.0-9.0.2"
source: { url: "https://raw.githubusercontent.com/juce-framework/JUCE/9.0.2/BREAKING_CHANGES.md (version 9.0.0 section); https://github.com/juce-framework/JUCE tag list", doi: "", title: "JUCE BREAKING_CHANGES.md at tag 9.0.2; git ls-remote --tags on the official repository", locator: "https://raw.githubusercontent.com/juce-framework/JUCE/9.0.2/BREAKING_CHANGES.md (version 9.0.0 section); https://github.com/juce-framework/JUCE tag list", accessed: "2026-10-04", tier: 1 }
confidence: verified
derived_from: []
discovered_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:15:00Z
---
Informs D-001 (pin 8.0.15, forbid a silent upgrade to 9.x). Checked directly against the source rather than secondary coverage, since JUCE version choice is load-bearing for every later plugin step.
