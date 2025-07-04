from testapi import *
from lib.sessions.base import BaseSession


class TTYSession(BaseSession):
    _ttys_logged_in_set = set()
    default_app_name = 'tty'
    allowed_open_strategies = []

    def __init__(self, tty_number):
        self.tty_number = tty_number

    @classmethod
    def open(cls, method=None, tty_number=3):
        send_key(f'ctrl-alt-f{tty_number}')
        instance = cls(tty_number)
        instance.expect_ready()
        return instance

    @classmethod
    def is_logged_in(cls, tty_number):
        return tty_number in cls._ttys_logged_in_set

    @classmethod
    def mark_logged_in(cls, tty_number):
        cls._ttys_logged_in_set.add(tty_number)

    def login(self, username='root', password=None):
        if not self.is_logged_in(self.tty_number):
            self.expect_not_login()
            self.type_and_submit(username)
            if username != 'root' or password:
                self.type_and_submit(password)
            self.expect_login()
            self.mark_logged_in(self.tty_number)
        else:
            self.expect_login()
        return self

    def shutdown(self, username='root', password=None):
        if not self.is_logged_in(self.tty_number):
            self.login(username, password)
        self.type_and_submit('poweroff')
        assert_shutdown(300)
        return self

    def expect_ready(self, timeout=30):
        if TTYSession.is_logged_in(self.tty_number):
            self.expect_login()
        else:
            self.expect_not_login()

    def expect_not_login(self, timeout=30):
        return self.expect('not_login_tty')

    def expect_login(self, timeout=30):
        return self.expect('login_tty')
