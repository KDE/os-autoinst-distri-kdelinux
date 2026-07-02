# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import subprocess
from lib.sut.atspi import find_pid_on_atspi_bus


def launch(app_id: str, atspi_name: str, *args: str, timeout: int = 30):
    """Launch a Flatpak app and return (process, pid) once it registers on the a11y bus."""
    process = subprocess.Popen(['flatpak', 'run', app_id, *args])
    pid = find_pid_on_atspi_bus(atspi_name, timeout)
    return process, pid


def quit(app_id: str):
    """Send SIGTERM to a Flatpak, gracefully quitting it."""
    ps = subprocess.run(['flatpak', 'ps', '--columns=application,child-pid'],
                        capture_output=True, text=True)
    for line in ps.stdout.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0] == app_id:
            # Flatpak is weird. child-pid is the host PID of the sandbox's init
            # and the kernel drops SIGTERM sent to a namespace's init
            # from outside it. So we SIGTERM its children instead which should
            # kill the actual app that's running.
            subprocess.run(['pkill', '-TERM', '-P', fields[1]])


def kill(app_id: str):
    """Send SIGKILL to a Flatpak, forcibly quitting it."""
    subprocess.run(['flatpak', 'kill', app_id], capture_output=True)
