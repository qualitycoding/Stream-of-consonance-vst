#!/bin/sh
# Verifies the VST freeze manifest. Exits non-zero if any frozen file has changed.
# Run from the repository root:  sh vst/tests/verify_frozen.sh
set -e
cd "$(dirname "$0")"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c FROZEN_MANIFEST.sha256
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 -c FROZEN_MANIFEST.sha256
else
  echo "no sha256sum or shasum available" >&2
  exit 2
fi
echo "FROZEN OK"
