---
id: L-20261004T150800Z-bulk-delete-removed-tracked-file
title: "Bulk-deleting a directory to remove stray untracked files also removed a file that was actually tracked and committed"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:git, phase:implementation, kind:integrity]
recorded_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:08:00Z
---
## Trigger
Cleaning up unexpected or stray-looking files/directories found in a git working tree, where the directory in question contains a mix of untracked stray content and legitimately tracked content.
## What went wrong
Stray plan/ and research/ directories (containing a different draft's content) were found at the repository root, outside the intended vst/ subtree. Both were removed with `rm -rf plan research` without first checking git status on those paths. research/RESEARCH_LOG.md, part of the original repository's own tracked, committed content, was inside research/ and was deleted along with the genuinely stray files.
## Correction
git status --short immediately after showed the file as deleted (tracked), and it was restored with git checkout -- research/RESEARCH_LOG.md before continuing.
## Prevention rule
Before bulk-deleting any directory in a git working tree to clean up stray files, run git status --short on that path first and delete only what shows as untracked (??); never rm -rf a directory that might contain tracked content without checking first.
## Detection check
git status --short <path> before any rm -rf <path>; if any line does not start with '??', stop and delete file-by-file instead.
## Evidence
This turn's tool history: rm -rf plan research followed immediately by git status --short showing "D research/RESEARCH_LOG.md", then git checkout -- research/RESEARCH_LOG.md. Recorded during S-RETRO.
