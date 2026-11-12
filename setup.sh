#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

CASEDIR="$(git rev-parse --show-toplevel)"
cd "$CASEDIR"

if [[ -n "${MOCK_MODE:-}" ]]; then
    zypper --non-interactive --gpg-auto-import-keys install python3-uv
fi

export UV_PROJECT_ENVIRONMENT=/var/lib/kde-linux-openqa/worker-venv
uv sync -qq
source "$UV_PROJECT_ENVIRONMENT/bin/activate"

if (( $# )); then
    exec "$@"
fi
