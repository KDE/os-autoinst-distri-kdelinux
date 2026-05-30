# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import subprocess
from lib.sut.atspi import find_pid_on_atspi_bus


def launch(app_id: str, atspi_name: str, *args: str, timeout: int = 30):
    """Launch a Flatpak app and return (process, pid) once it registers on the a11y bus."""
    process = subprocess.Popen(['flatpak', 'run', app_id, *args])
    pid = find_pid_on_atspi_bus(atspi_name, timeout)
    return process, pid


def kill(app_id: str):
    """Terminate a running Flatpak app."""
    subprocess.run(['flatpak', 'kill', app_id], capture_output=True)
