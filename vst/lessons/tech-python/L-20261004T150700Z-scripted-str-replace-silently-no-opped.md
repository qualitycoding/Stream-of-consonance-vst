---
id: L-20261004T150700Z-scripted-str-replace-silently-no-opped
title: "A Python str.replace()-based file edit reported success but made no change, because the search pattern did not match"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:python, phase:implementation, kind:verification-gap]
recorded_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:07:00Z
---
## Trigger
Editing a file via a scripted, non-interactive search-and-replace (Python's str.replace, or equivalent) run inside a bash tool call, where the script prints a success message unconditionally.
## What went wrong
A script intended to append an implementation-status note to plan/TRACEABILITY.md called s.replace(old, new) and then wrote the file and printed "updated", regardless of whether old actually matched anything in s. It did not match (the file's actual text differed slightly from what was assumed), so replace() returned the string unchanged, the file was rewritten byte-for-byte identical to before, and the script still printed "updated". The omission was only caught later by diffing git history and finding the expected content absent.
## Correction
Re-did the edit using the str_replace tool, which fails loudly (rejects the edit) rather than silently no-opping when old_str does not match -- and confirmed the change with a git diff before committing.
## Prevention rule
After any non-interactive search-and-replace edit, immediately diff or grep the target file to confirm the expected change landed, rather than trusting a script's own completion message; prefer a replace primitive that fails loudly on a non-match over one (like Python's str.replace) that silently returns the input unchanged.
## Detection check
git diff --stat <path> after the edit must show the file as changed; a str.replace()-based script with no post-edit diff/grep check is itself the anti-pattern to flag in review.
## Evidence
Commit "plan/TRACEABILITY.md: record actual implementation status (prior edit silently no-op'd)"; the preceding commit where the intended TRACEABILITY.md change is absent despite "updated" having been printed. Recorded during S-RETRO.
