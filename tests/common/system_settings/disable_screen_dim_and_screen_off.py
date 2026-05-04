# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib.openqa import cli_test
from lib import paths

def run(self):
    test = cli_test.CliTest('disable_screen_dim_and_screen_off')
    # TODO doesn't work because it doesn't know its own coordinates
    # test.run_selenium(f'{paths.LIB_DIR}/tests/disable_screen_dim_and_screen_off.py')
    test.run_script()
