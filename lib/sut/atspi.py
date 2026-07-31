# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import time
import pyatspi


def find_pid_on_atspi_bus(app_name: str, timeout: int = 10) -> int:
    """Return the PID of the named app as registered on the AT-SPI bus, waiting for it to appear with a set timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for i in range(pyatspi.Registry.getDesktopCount()):
            desktop = pyatspi.Registry.getDesktop(i)
            for app in desktop:
                try:
                    if app.name == app_name:
                        return app.get_process_id()
                except Exception:
                    pass
        time.sleep(0.5)
    raise RuntimeError(f'"{app_name}" did not appear on the AT-SPI bus within {timeout}s')
