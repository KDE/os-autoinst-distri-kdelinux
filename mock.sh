#!/usr/bin/env bash
set -euo pipefail

CASEDIR="$(git rev-parse --show-toplevel)"
cd "$CASEDIR"

exec podman-compose \
    -f mocks/single-instance.yml \
    "${@:-up}"
