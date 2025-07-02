from testapi import *

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from lib.sessions.tty import TTYSession

def run(self):
    (
        TTYSession
            .open()
            .login(username='kdelinuxtester', password='1122334455')
            .shutdown()
    )