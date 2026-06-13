# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *

def test_flags(self):
    return {'fatal': 1}

def run(self):
    power('on')
    # check if we see plymouth
    assert_screen('booting_screen', 'timeout', 30)
    # wait for kick-off icon on panel to show up
    assert_screen('kickoff_icon_on_panel', 'timeout', 60)
