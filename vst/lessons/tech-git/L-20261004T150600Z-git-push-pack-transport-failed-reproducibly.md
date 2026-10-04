---
id: L-20261004T150600Z-git-push-pack-transport-failed-reproducibly
title: "git push failed with a server-side unpack error reproducibly, regardless of branch, content, or credential; the GitHub REST Git Data API succeeded immediately"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:git, tech:github, phase:implementation, kind:environment]
recorded_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:06:00Z
---
## Trigger
git push (smart-HTTP) to a GitHub repository fails with a server-side "did not receive expected object <hash>" / "remote unpack failed: index-pack failed" error.
## What went wrong
Assumed the failure was content- or credential-related and spent several retries on that theory: different branch names, --no-thin, a much larger http.postBuffer, a second (freshly issued) PAT, and stripping large files from the push -- all failed with the exact same error and the exact same phantom object hash, which does not appear anywhere in the local repository's object graph. A tiny test push (a few KB) succeeded immediately with the same token, proving credentials were never the problem.
## Correction
Switched to GitHub's REST Git Data API (create blob -> create tree -> create commit -> update ref), which bypasses git's pack-negotiation protocol entirely and succeeded on the first attempt for the full ~1.7MB, 120-file tree. Verified by cloning the result fresh and confirming it matched.
## Prevention rule
If git push fails with a server-side unpack/index-pack error that persists across retries with different refs, content, and credentials, stop retrying the pack-transport path (it is very likely a sandbox/proxy transport issue, not a repository or permissions problem) and fall back to the GitHub REST Git Data API for the push.
## Detection check
A minimal test push (a few KB, unrelated content) succeeding while the real push fails identically across >=2 varied retries is the signal to stop retrying git push and switch to the API.
## Evidence
This turn's tool-call history (git push attempts to push-test, push-test2, mini-test, mid-test, orig-tip-test, no-wav-test branches, all failing identically; /home/claude/push_via_api.py and its successful run). Recorded during S-RETRO.
