---
id: K-20261004T151600Z-github-rest-api-bypasses-broken-pack-transport
statement: "When git push (smart-HTTP pack transfer) to a GitHub repository fails reproducibly with a server-side index-pack/unpack error regardless of branch, content size, or credential, GitHub's REST Git Data API (POST .../git/blobs for each file's base64 content, POST .../git/trees referencing the blob shas by full path, POST .../git/commits referencing the tree and a parent sha, PATCH .../git/refs/heads/<branch> to move the ref) succeeds via ordinary JSON-over-HTTPS requests, bypassing the pack-negotiation protocol entirely. GitHub's create-tree endpoint accepts full nested paths (e.g. vst/plan/PLAN.md) directly, so no manual nested-tree construction is needed for a flat list of files."
status: current
supersedes: []
tags: [subject:github-access-from-sandbox, tech:git, tech:github, phase:implementation]
applies_to_version: "observed 2026-10-04, GitHub REST API v3 (application/vnd.github+json)"
source: { url: "", doi: "", title: "Observed and verified in this run", locator: "/home/claude/push_via_api.py; verified by cloning the pushed result fresh and confirming the tree, freeze manifest and test suite all matched", accessed: "2026-10-04", tier: 1 }
confidence: verified
derived_from: []
discovered_by: implementer
run: gen-20260920T202705Z-stream-of-consonance-vst
recorded_at: 2026-10-04T15:16:00Z
---
Supersedes nothing in the existing K-20261004T102023Z-github-access-from-sandbox item (that item covers unauthenticated access and token-header hygiene; this adds the push-path fallback it did not cover). A walk of the local filesystem for the files to push must explicitly skip .gitignore'd paths (e.g. __pycache__) since os.walk does not consult .gitignore the way git itself does -- the first run of this method accidentally included 32 stray .pyc files for exactly this reason.
