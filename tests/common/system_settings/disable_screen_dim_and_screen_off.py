# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib import serial_test

def run(self):
    # TODO doesn't work because it doesn't know it's own coordinates
    #serial_test.run('/tests/sut/openqa-selenium-webdriver-at-spi-run systemsettings /tests/sut/scripts/disable_screen_dim_and_screen_off.py')
    serial_test.run('/tests/sut/scripts/disable_screen_dim_and_screen_off.sh')
