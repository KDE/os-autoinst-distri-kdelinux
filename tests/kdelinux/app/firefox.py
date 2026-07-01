# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
from testapi import *
from lib.openqa import cli_test
from lib import user_manager

def run(self):
    # Launches Firefox to trigger the policy-driven add-on install, so it needs the
    # AT-SPI/Selenium harness and enough time for the AMO download to complete.
    test = cli_test.CliTest('firefox', timeout=180)
    test.run_selenium(user=user_manager.installed())
