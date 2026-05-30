# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
from testapi import *
from lib.openqa import cli_test
from lib import user_manager

def run(self):
    test = cli_test.CliTest('create_file')
    test.run_selenium(user=user_manager.installed())
