from testapi import *
from lib.sessions.syscore.tty import TTYSession
from lib.utils import get_username_and_password


def run(self):
    username, password = get_username_and_password()
    (
        TTYSession
            .ensure_active(tty_number=3)
            .shutdown(username=username, password=password)
    )
