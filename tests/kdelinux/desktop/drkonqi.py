#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>
# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL


from testapi import *
from lib.openqa import cli_test
from lib import paths
from lib import user_manager

def run(self):
    test = cli_test.CliTest('drkonqi')
    test.run_selenium(user=user_manager.installed())
