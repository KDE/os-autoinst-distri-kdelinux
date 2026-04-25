# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib.openqa import serial_test

def run(self):
    test = serial_test.SerialTest('disable_screen_dim')
    # TODO doesn't work because it doesn't know its own coordinates
    # test.run_selenium('/tests/sut/scripts/disable_screen_dim_and_screen_off.py')
    test.run_cmd('/tests/sut/scripts/disable_screen_dim_and_screen_off.sh')
