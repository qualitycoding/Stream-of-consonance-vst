#!/bin/sh
# Fails if any frozen test file was modified. Run from the repo root before pytest.
set -e
sha256sum -c tests/FROZEN.sha256
