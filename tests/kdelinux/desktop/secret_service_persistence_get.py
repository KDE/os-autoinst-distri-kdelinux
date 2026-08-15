# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
from testapi import *
from lib.test import cli_test
from lib.common import user_manager

def run(self):
    test = cli_test.CliTest('secret_service_persistence_set')
    test.run_selenium(user=user_manager.installed())
