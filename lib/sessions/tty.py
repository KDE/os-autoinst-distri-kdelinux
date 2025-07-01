from testapi import *
from lib.sessions.base import BaseSession

class TTYSession(BaseSession):
    _ttys_logged_in = set()

    @classmethod
    def open(cls, tty_number=3):
        send_key(f'ctrl-alt-f{tty_number}')
        return cls()

    def login(self, tty_number=3, username='root', password=None):
        if tty_number not in self._ttys_logged_in:
            type_string(username)
            send_key('ret')
            if username != 'root' or password:
                type_string(password)
            send_key('ret')
        return self

    def register_login(self, tty_number=3):
        TTYSession._ttys_logged_in.add(tty_number)
        return self

    def shutdown(self, tty_number=3, username='root', password=None):
        if tty_number not in self._ttys_logged_in:
            self.login(tty_number, username, password).expect_login().register_login()
        self.command('poweroff')
        return self

    def expect_not_login(self):
        return self.expect('not_login_tty')

    def expect_login(self):
        return self.expect('login_tty')
