from testapi import *
from lib.sessions.syscore.tty import TTYSession
from lib.strategies.base import OpenStrategy


class TTYOpenStrategy(OpenStrategy):
    def open_app(self, app_name, tty_number=3):
        (
            TTYSession
                .ensure_active(tty_number=3)
                .type_and_submit(app_name)
        )