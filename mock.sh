#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

CASEDIR="$(git rev-parse --show-toplevel)"
cd "$CASEDIR"

exec podman-compose \
    -f mocks/single-instance.yml \
    "${@:-up}"
