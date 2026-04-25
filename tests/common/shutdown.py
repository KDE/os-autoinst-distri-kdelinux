# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib.openqa import serial_test
from lib import user_manager

def run(self):
    serial_test.session.run('systemctl poweroff', user_manager.root(), wait_result=False)
    assert_shutdown()
    serial_test.session.reset()
