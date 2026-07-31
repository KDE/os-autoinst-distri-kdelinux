# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
from testapi import *
from lib.test.sessions.syscore.plasma_desktop import PlasmaDesktopSession
from lib.test.cli_session import session
from lib.test import cli_test
from lib.common import paths
from lib.common import user_manager

def test_flags(self):
    return {'fatal': 1}

def run(self):
    test = cli_test.CliTest('plasma_setup')
    test.run_selenium(user=user_manager.plasma_setup())

