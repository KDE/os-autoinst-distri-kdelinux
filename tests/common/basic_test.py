# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
from testapi import *
from lib.openqa import cli_test
from lib import paths

def run(self):
    test = cli_test.CliTest('basic_test')
    test.run_python()
