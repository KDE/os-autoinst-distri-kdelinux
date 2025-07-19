from testapi import *

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from lib.utils import type_and_submit


def run(self):
    # check whether booted into desktop screen
    assert_and_click(
        'sddm_password_input',
        'timeout', 60
    )
    type_and_submit('1122334455')
    # check whether booted into desktop screen
    assert_screen('kdelinux_desktop_welcome', timeout=60)
