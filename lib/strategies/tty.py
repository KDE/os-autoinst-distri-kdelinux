from testapi import *

from lib.sessions.tty import TTYSession
from lib.strategies.base import OpenStrategy


class TTYOpenStrategy(OpenStrategy):
    def open_app(self, app_name, tty_number=3):
        (
            TTYSession
                .open()
                .type_and_submit(app_name)
        )