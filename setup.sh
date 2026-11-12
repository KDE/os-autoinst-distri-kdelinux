#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

CASEDIR="$(git rev-parse --show-toplevel)"
cd "$CASEDIR"

if [[ -n "${MOCK_MODE:-}" ]]; then
    zypper --non-interactive install awk >/dev/null 2>&1 || true
    curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL=/usr/local/bin sh >/dev/null 2>&1
fi

export UV_PROJECT_ENVIRONMENT=/var/lib/kde-linux-openqa/worker-venv
uv sync -qq
source "$UV_PROJECT_ENVIRONMENT/bin/activate"

# mkfs.erofs is in the /usr/sbin in openSUSE
export PATH=/usr/sbin:$PATH

if (( $# )); then
    exec "$@"
fi
