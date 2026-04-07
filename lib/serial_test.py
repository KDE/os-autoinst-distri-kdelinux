# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *

def run(script):
    # Ensure we're in the terminal
    select_console('virtio-terminal')
    assert_script_run(
        f'~/tests/venv/bin/python ~/tests/sut/scripts/{script}',
    )
    # Then switch back to the GUI to avoid breaking needle tests
    select_console('desktop')
