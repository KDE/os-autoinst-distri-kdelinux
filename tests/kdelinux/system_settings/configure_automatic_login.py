#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>
# SPDX-License-Identifier: MIT

from testapi import *
from lib.test.sessions.syscore.plasma_desktop import PlasmaDesktopSession
from lib.test import cli_test
from lib.common import paths
from lib.common import user_manager

def test_flags(self):
    return {'fatal': 1}

def run(self):
    test = cli_test.CliTest('configure_automatic_login')
    test.run_selenium(user=user_manager.installed())
