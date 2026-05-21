# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *

def run(self):
    power('on')
    assert_screen('uefi_screen', 'timeout', 30)
    send_key('ret')
    assert_screen('booting_screen', 'timeout', 30)
    assert_screen('welcome_desktop_screen', 'timeout', 60)
