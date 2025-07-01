from testapi import *

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from lib.sessions.tty import TTYSession

def run(self):
    (
        TTYSession
            .open()
            .expect_not_login()
            .login(username='live')
            .expect_login()
            .register_login()
            .shutdown()
    )
    assert_shutdown(300)
