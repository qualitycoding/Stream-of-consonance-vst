# GATE-G-003 — Lessons & Knowledge Push

## Items to push

**Lessons (10)**, to `https://github.com/qualitycoding/Lessons`:

| ID | Title | Tags | Severity |
|---|---|---|---|
| L-20261004T150100Z-stray-superseded-test-files | Two superseded test files with FROZEN headers and a contradictory test-ID scheme sat alongside the real frozen suite | tech:cpp, phase:verification, kind:integrity | High |
| L-20261004T150200Z-frozen-header-default-contradicted-fixture | A frozen C++ header's default MPE bend range (48 semitones) contradicted the frozen fixture's value (2) | tech:cpp, phase:specification, kind:integrity | High |
| L-20261004T150300Z-fixture-cents-reference-undeclared | Golden fixtures gave cents values with no stated reference pitch, risking a silent, undetectable scoring error | tech:python, tech:cpp, phase:specification, kind:verification-gap | Critical |
| L-20261004T150400Z-interface-gap-found-only-by-implementing | A frozen interface header specified generateStream without any way to learn which candidate was chosen | tech:cpp, phase:specification, kind:wrong-assumption | High |
| L-20261004T150500Z-cross-library-float-fix-regressed-passing-cases | A fix for one failing floating-point boundary case was adopted before re-running the full suite, and it silently broke 12 previously-passing values | tech:cpp, tech:numpy, phase:implementation, kind:process | High |
| L-20261004T150600Z-git-push-pack-transport-failed-reproducibly | git push failed with a server-side unpack error reproducibly, regardless of branch, content, or credential | tech:git, tech:github, phase:implementation, kind:environment | Medium |
| L-20261004T150700Z-scripted-str-replace-silently-no-opped | A Python str.replace()-based file edit reported success but made no change | tech:python, phase:implementation, kind:verification-gap | Medium |
| L-20261004T150800Z-bulk-delete-removed-tracked-file | Bulk-deleting a directory to remove stray files also removed a tracked, committed file | tech:git, phase:implementation, kind:integrity | Medium |
| L-20261004T150900Z-local-head-diverged-from-api-pushed-remote | Continuing work from the local branch after an API-based push left local history diverged from GitHub | tech:git, tech:github, phase:implementation, kind:environment | Medium |
| L-20261004T151000Z-parameter-range-set-without-attainable-range-check | A UI parameter's range was set to a model's full regression range instead of what the actual configuration can attain | domain:music-perception, tech:cpp, phase:specification, kind:wrong-assumption | Low (recurrence of L-20261004T102005Z) |

**Knowledge items (6)**, to `https://github.com/qualitycoding/knowledge`:

| ID | Statement (short) | Tags | Confidence |
|---|---|---|---|
| K-20261004T151100Z-pcg64-xsl-rr-advance-then-output | PCG64 advances state before output, not after | subject:pcg64-bit-generator, tech:numpy, tech:cpp | verified |
| K-20261004T151200Z-numpy-seedsequence-reconstructed | numpy SeedSequence algorithm reverse-engineered and verified | subject:pcg64-bit-generator, tech:numpy, tech:cpp | verified |
| K-20261004T151300Z-numpy-array-vs-scalar-ufunc-rounding-differs | numpy array vs scalar log2/pow round differently in the last bit | subject:numpy-ufunc-precision, tech:numpy, tech:cpp | verified |
| K-20261004T151400Z-circular-correlation-shift-linearity | Circular correlation is linear + shift-equivariant; enables O(1)-per-candidate harmonicity | subject:pitch-class-harmonicity, tech:cpp | verified |
| K-20261004T151500Z-juce-8-vs-9-vst3-breaking-change | JUCE 9.0.0 restructures the VST3 client extension API | subject:juce-versioning, tech:juce | verified |
| K-20261004T151600Z-github-rest-api-bypasses-broken-pack-transport | GitHub REST Git Data API as a fallback when git push's pack transport fails | subject:github-access-from-sandbox, tech:git, tech:github | verified |

## Target and sign-off

Proposed target: the two repositories above, as recorded in `A-011`. **Sign-off already given**:
the human's message that initiated adoption of the addendum named both repositories explicitly
and supplied a push credential in the same message, before this gate was reached. Treated as
`push-to: <target>` for both, per `plan/GATES.md`'s G-003 definition. No second round-trip
requested.

## Outcome

**Lessons and knowledge: pushed and verified.** `qualitycoding/Lessons` commit `51e5342`
(22 entries, up from 11), `qualitycoding/knowledge` commit `db1ee95` (20 entries, up from 14).
Both re-cloned fresh and schema-checked after push; both indexes' entry counts match their
directories' actual file counts.

One correction made live during this step, not planned: the first `knowledge` push
(`c65b421`) carried a stale `INDEX.md` (14 entries, should have been 20) because
`scripts/build_index.py` crashed partway through on a JSON-escaping bug in one new file, the bug
was fixed, but the index generator was not re-run before committing. Caught by the fresh-clone
verification this step itself requires, fixed in a follow-up commit (`db1ee95`), and recorded as
an 11th lesson (`L-20261004T153000Z`, a recurrence of `L-20261004T150700Z`).

**`Stream-of-consonance-vst`: not pushed this step.** This run's updates (the addendum adoption,
D-009, and all 11 lessons / 6 knowledge items as they exist on the working branch) are committed
locally (`f0d2c09`) but not on GitHub. Both GitHub tokens supplied earlier in this conversation
for that repository now return `401 Bad credentials` (consistent with having been rotated, which
was recommended). The token supplied for this step is scoped only to `Lessons`/`knowledge` (`403`
on that repo, not `401` — a valid but out-of-scope credential, not a revoked one). Per the
addendum's own fallback for an unreachable target, holding only this part back: delivered as
`stream-of-consonance-vst-update.bundle` instead, reported to the human.

