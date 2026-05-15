#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>
# SPDX-License-Identifier: MIT

from testapi import *
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession
from lib.openqa import cli_test
from lib import paths
from lib import user_manager

def run(self):
    test = cli_test.CliTest('configure_automatic_login')
    test.run_selenium(user=user_manager.installed())
