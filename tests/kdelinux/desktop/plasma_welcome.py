# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

from testapi import *
from lib.openqa import cli_test
from lib import paths
from lib import user_manager

def run(self):
    test = cli_test.CliTest('plasma_welcome', timeout=300)
    test.run_selenium(user=user_manager.installed())
