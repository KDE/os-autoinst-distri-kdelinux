# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

from testapi import *
from lib.openqa import cli_test
from lib import paths
from lib import user_manager

def test_flags(self):
    return {'fatal': 1}

def run(self):
    encrypted = get_var('FDE_INSTALL', '0')
    install_mode = '--encrypted' if encrypted == '1' else '--default'

    test = cli_test.CliTest('calamares_install', artifacts=['/tmp/calamares-session.log'], timeout=300)
    test.run_selenium(user=user_manager.live(), args=install_mode)
    # After install is run we set FIRST_BOOT so follow up code
    # knows that this is first boot
    set_var('FIRST_BOOT', '1')
