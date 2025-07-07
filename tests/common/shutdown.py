from testapi import *
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from lib.sessions.tty import TTYSession
from lib.utils import get_username_and_password

def run(self):
    username, password = get_username_and_password()
    (
        TTYSession
            .open(tty_number=3)
            .shutdown(username=username, password=password)
    )
