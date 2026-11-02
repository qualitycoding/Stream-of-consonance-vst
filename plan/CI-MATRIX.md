# CI platform matrix (v3.9, intake-derived)

**Repository:** `qualitycoding/Stream-of-consonance-vst` — primary language: Python; VST plugin (C++/JUCE-style toolchain) with Python test harness.

| Platform bound | CI job | Waiver |
|---|---|---|
| ubuntu-24.04 x86_64 | `build-test` (pinned `ubuntu-24.04`) | — |
| oldest supported toolchain | `oldest-toolchain` (pinned) | — |
| ARM64 | `linux-arm64` | — |
| libc variant | `musl` container | — |

No platform expansion (D-902); fail-fast disabled; long builds and mutation
runs execute in CI only (D-905).
