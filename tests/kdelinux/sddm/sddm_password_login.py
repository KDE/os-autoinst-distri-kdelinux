from testapi import *

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.syscore.plasma_desktop import PlasmaDesktopSession

from lib.utils import type_and_submit


def run(self):
    # check whether booted into desktop screen
    assert_and_click(
        'sddm_password_input',
        'timeout', 60
    )
    type_and_submit('1122334455')

    # DO_INSTALL = 0 indicates the full system boot up for the first time after installing from live.
    # Check if welcome exists
    do_install = get_var('DO_INSTALL')
    if do_install == '0':
        assert_screen('kdelinux_desktop_welcome', timeout=60)
    PlasmaDesktopSession.ensure_active()
