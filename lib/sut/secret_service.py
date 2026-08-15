# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Helper for interacting with the Secret Service.

import subprocess
import os

SECRETS_BUS_NAME = 'org.freedesktop.secrets'


class SecretServicePidError(Exception):
    """Raised when the Secret Service PID cannot be determined."""


def activate() -> None:
    # The Secret Service is D-Bus activated, bring it up if it isn't already
    subprocess.run(['secret-tool', 'lookup', 'kde-linux-openqa', 'probe'], capture_output=True, text=True)


def pid() -> int:
    out = subprocess.check_output(
        ['busctl', '--user', 'status', SECRETS_BUS_NAME], text=True)
    for line in out.splitlines():
        if line.strip().startswith('PID='):
            return int(line.split('=', 1)[1].strip())
    raise SecretServicePidError(f'could not determine PID owning {SECRETS_BUS_NAME}')


def process_exe() -> str:
    return os.path.basename(os.readlink(f'/proc/{pid()}/exe'))
