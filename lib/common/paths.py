# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import subprocess
from pathlib import Path

VAR_DIR      = '/var/lib/kde-linux-openqa'
VENV_DIR     = f'{VAR_DIR}/venv'
LIB_DIR      = '/usr/lib/kde-linux-openqa'
RESULTS_DIR  = '/var/log/kde-linux-openqa'
OPENQA_SSH_PRIVATE_KEY = '/tmp/kde-linux-openqa-root-key'


def git_root() -> Path:
    return Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
