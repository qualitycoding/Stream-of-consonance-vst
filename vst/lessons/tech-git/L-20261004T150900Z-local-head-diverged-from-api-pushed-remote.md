---
id: L-20261004T150900Z-local-head-diverged-from-api-pushed-remote
title: "Continuing work from the local branch after an API-based push left local history diverged from what was actually on GitHub"
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:git, tech:github, phase:implementation, kind:environment]
recorded_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:09:00Z
---
## Trigger
A push was made via the GitHub REST API (blob/tree/commit/ref) rather than git push, and a later turn continues work by cd-ing into the same local clone and committing on top of its existing local HEAD.
## What went wrong
The API push created a new commit directly on GitHub as a child of the remote's existing tip, built from the working tree's current file contents -- it did not know about, or extend, the local repository's own commit graph (a local merge commit created moments earlier, joining the target repo's initial LICENSE commit with this run's history, was bypassed entirely). The local branch's HEAD and the remote's main pointed at different, unrelated commits with identical trees. Starting a later turn's work from the stale local HEAD risked quietly reintroducing the local-only merge commit's lineage instead of continuing from what was actually published.
## Correction
Before continuing work in this turn, fetched the remote and reset the local branch to it (git checkout -B <branch> <remote>/main) rather than assuming the local HEAD from the prior turn was still authoritative.
## Prevention rule
After any push performed via a non-git-push mechanism (the GitHub API, a bundle import, etc.), treat the local branch as stale: fetch and reset to the remote tip before making further commits, rather than continuing to build on the pre-push local HEAD.
## Detection check
git fetch <remote> && git diff --stat <local-HEAD> <remote>/main; a non-empty, non-cosmetic diff (or a diverged, non-fast-forward graph) means the local branch must be reset before continuing.
## Evidence
This turn's tool history: git log --oneline showing local HEAD at the merge commit while vst-target/main pointed at the API-created commit; the reconciling git checkout -B. Recorded during S-RETRO.
