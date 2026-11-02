
## Addendum v3.9 decisions (2026-11-02)

- **D-900** — Planning-only amendment; product scope, interfaces, frozen test
  behaviour and human gates unchanged except split G-003 store semantics.
- **D-901** — Source tip `40f3d3a1bfe8` is the rollout addendum commit, child of
  audited `d4075852db02`; implementation descends from it.
- **D-902..D-904** — No platform expansion, no release; defaults from evidence.
- **D-905** — No local build/test/mutation execution; CI is the authoritative
  venue (estimates labelled; nothing unrun claimed as passed).
- **D-906** — No fresh-context reviewer available; substitution + High risk.
- **D-980** — Mutation design: `reviews/MUTATION.md` (root) applies to both
  planning roots; priced three-tier triggers, one aggregator, report score gate.
