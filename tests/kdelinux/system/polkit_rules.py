# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Hadi Chokr <hadichokr@icloud.com>
from testapi import *
from lib.test import cli_test

def run(self):
    # Runs as root because it creates and deletes an account.
    test = cli_test.CliTest('polkit_rules')
    test.run_python()
