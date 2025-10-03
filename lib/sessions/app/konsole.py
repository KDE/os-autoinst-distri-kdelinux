from testapi import *

from lib.sessions.base import BaseSession
from lib.sessions.mixins.openable import OpenableSessionMixin


class KonsoleSession(BaseSession, OpenableSessionMixin):
    default_app_name = 'konsole'
    allowed_strategies = ['krunner']

    def expect_ready(self, timeout=30):
        if self.check_screen("zsh_startup_file_missing", timeout=10):
            self.type_and_submit('0')
        return self.expect('empty_konsole', timeout=timeout)
