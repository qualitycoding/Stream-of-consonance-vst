
## v3.9 addendum (2026-11-02)

1. **D-901** — Source tip `40f3d3a1bfe8917fad3b56bee1190fe7ea1854a2` is the rollout addendum commit, child of audited `d4075852db02391ed0be2a25fd30132728279b99`; implementation descends from it.
2. Root-level planning now also lives under `plan/` so the controller's verifier can run with `--plan-root plan`; root originals are preserved unchanged.
3. **D-905** — git transport blocked; reads via codeload, writes via Git database API; remote SHA verified after every push. No local build/test/mutation runs; CI is the authoritative venue; estimates labelled.
4. **D-906** — no fresh-context reviewer; review substitution recorded with High risk.
5. G-003 lesson/knowledge pushes pending sign-off (do-not-push until then).
