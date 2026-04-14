# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib import serial_test

def run(self):
    select_console('virtio-terminal')
    type_string('poweroff\n')
    assert_shutdown()
