from testapi import *
from lib.sessions.base import BaseSession


class TTYSession(BaseSession):
    _ttys_logged_in_set = set()

    def __init__(self, tty_number):
        self.tty_number = tty_number

    @classmethod
    def ensure_active(cls, tty_number=3):
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

    def ensure_logged_in(self, username='kdelinuxtestuser', password=None):
        """Ensure user is logged in before executing sensitive commands"""
        if not TTYSession.is_logged_in(self.tty_number):
            self.expect_not_login()
            self.type_and_submit(username)
            sleep(5)
            if password:
                self.type_and_submit(password)
            self.expect_login()
            TTYSession.mark_logged_in(self.tty_number)
        else:
            self.expect_login()

    def login(self, username='kdelinuxtestuser', password=None):
        self.ensure_logged_in(username, password)
        return self

    def shutdown(self, username='kdelinuxtestuser', password=None):
        self.ensure_logged_in(username, password)
        self.type_and_submit('poweroff')
        assert_shutdown(300)
        TTYSession._ttys_logged_in_set.remove(self.tty_number)
        return self

    def reboot(self, username='kdelinuxtestuser', password=None, automatic_login=False):
        self.ensure_logged_in(username, password)
        self.type_and_submit('reboot')
        TTYSession._ttys_logged_in_set.remove(self.tty_number)
        return self

    def expect_ready(self, timeout=30):
        if self.is_logged_in(self.tty_number):
            self.expect_login()
        else:
            self.expect_not_login()

    def expect_not_login(self, timeout=30):
        return self.expect('not_login_tty')

    def expect_login(self, timeout=30):
        return self.expect('login_tty')
