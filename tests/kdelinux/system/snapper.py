# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Hadi Chokr <hadichokr@icloud.com>
from testapi import *
from lib.test import cli_test

def run(self):
    # Runs as root because it creates and deletes accounts and home subvolumes.
    # The timeout covers waiting on the passwd watcher, a timeline run and a
    # cleanup run.
    test = cli_test.CliTest('snapper', timeout=420)
    test.run_python()
