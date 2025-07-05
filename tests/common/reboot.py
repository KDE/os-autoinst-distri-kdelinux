from testapi import *

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from lib.sessions.tty import TTYSession

def run(self):
    do_install = get_var('DO_INSTALL')
    username = 'kdelinuxtester' if do_install == '0' else 'live'

    (
        TTYSession
            .open(tty_number=3)
            .login(username=username, password='1122334455' if do_install == '0' else None)
            .type_and_submit('reboot')
    )

def post_run_hook(self):
    assert_screen('bottom_panel_left_part', timeout, 30)
