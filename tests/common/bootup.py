# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

from testapi import *
from lib import user_manager

def test_flags(self):
    return {'fatal': 1}

def run(self):

    # Turn on the power, in practice if we did reboot,
    # this does nothing
    power('on')

    # Verify that KDE Linux UEFI screen is visible
    assert_screen('uefi_screen', 'timeout', 30)

    # If we are asked to boot into previous boot by upgrade testcase
    # press "down", wait for 1 second
    boot_prev = get_var('BOOT_PREVIOUS', '0')
    if boot_prev == '1':
        send_key('down')
        time.sleep(1)

    # Start the selected image.
    send_key('ret')

    # FDE_INSTALL=1 indicates full-disk-encryption
    encrypted = get_var('FDE_INSTALL', '0')
    do_install = get_var('DO_INSTALL', '0')
    first_boot = get_var('FIRST_BOOT', '0')

    if encrypted == '1' and (first_boot == '1' or do_install == '0'):
        # Enter password for the FDE
        assert_screen('bootup_fde', timeout=30)
        type_string(user_manager.installed().pw, "max_interval", 250)
        send_key('ret')

    # check if we see plymouth
    assert_screen('booting_screen', 'timeout', 30)

    if first_boot == '1':
        # Check if we boot into plasma-welcome
        assert_screen('plasma_welcome', 'timeout', 60)
    else:
        # wait for kick-off icon on panel to show up
        assert_screen('kickoff_icon_on_panel', 'timeout', 60)
