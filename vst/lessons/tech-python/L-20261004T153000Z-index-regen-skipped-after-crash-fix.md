---
id: L-20261004T153000Z-index-regen-skipped-after-crash-fix
title: "An index-generator script crashed partway through, and its root cause was fixed without re-running it to confirm the generated file was actually regenerated"
status: active
supersedes: []
recurrence_of: L-20261004T150700Z-scripted-str-replace-silently-no-opped
occurrences: 1
severity: Medium
tags: [tech:python, phase:implementation, kind:verification-gap]
recorded_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:30:00Z
---
## Trigger
A generated index/summary file is rebuilt by a script that processes several source files in a
loop and writes its output only at the end (or only for a given section) once the loop completes
without raising.
## What went wrong
scripts/build_index.py crashed with a JSONDecodeError partway through building the knowledge
store's index, caused by an unescaped quote in one new entry's statement field. The quote bug was
found and fixed in the offending file. The schema-check script was then run and passed. But
build_index.py itself was not re-run, so knowledge/INDEX.md was left at its pre-crash content (14
entries) while the directory it was supposedly indexing now held 20 files. This was committed and
pushed with the stale index, and only caught by re-cloning the pushed repository fresh and
checking the entry count against the actual file count, rather than trusting the local commit.
## Correction
Re-ran scripts/build_index.py after the fix, confirmed it produced 20 entries, committed and
pushed the corrected index as a separate, clearly-labelled fix commit.
## Prevention rule
After fixing the root cause of a script crash, re-run that exact script to completion (not just a
different validator) before committing its output, and verify any generated/derived file's basic
invariant (e.g. entry count matches source file count) against a fresh clone, not the local
working copy, before considering a push complete.
## Detection check
`git clone` the just-pushed repository fresh into a new directory and recompute the invariant
(e.g. `find knowledge -name 'K-*.md' | wc -l` vs the INDEX.md's own "Entries:" line) there, not in
the working copy that produced the push.
## Evidence
qualitycoding/knowledge commits c65b421 (stale index, 14 entries) and db1ee95 (fix, 20 entries);
this turn's verification clone at /tmp/verify_K. Recorded during S-KNOW, the moment the mistake
was found.
