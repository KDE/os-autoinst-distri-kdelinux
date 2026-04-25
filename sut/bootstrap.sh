#!/usr/bin/env bash
# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

set -euo pipefail

cd "$(dirname "$0")"

python3 -m venv --system-site-packages --upgrade-deps /tests/venv
source /tests/venv/bin/activate
/tests/venv/bin/pip3 install -r /tests/sut/requirements.txt
SITE_PACKAGES=$(/tests/venv/bin/python3 -c "import site; print(site.getsitepackages()[0])")
echo "/tests" >> "$SITE_PACKAGES/tests.pth"
