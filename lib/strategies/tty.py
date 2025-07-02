from testapi import *
from lib.strategies.base import OpenStrategy


class TTYOpenStrategy(OpenStrategy):
    def open_app(self, app_name, tty_number=3):
        send_key(f'ctrl-alt-f{tty_number}')
