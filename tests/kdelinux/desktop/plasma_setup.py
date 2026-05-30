# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
from testapi import *
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession
from lib.openqa import cli_test
from lib import paths
from lib import user_manager

def test_flags(self):
    return {'fatal': 1}

def run(self):
    test = cli_test.CliTest('plasma_setup')
    test.run_selenium(user=user_manager.plasma_setup())

    # Make sure at least the kickoff icon on the bottom panel shows up.
    #PlasmaDesktopSession.ensure_active()
