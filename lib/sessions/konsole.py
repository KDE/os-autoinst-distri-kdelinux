from testapi import *

from lib.sessions.base import BaseSession
from lib.sessions.krunner import KRunnerSession

class KonsoleSession(BaseSession):
    @classmethod
    def open_via_krunner(cls):
        (
            KRunnerSession
                .open()
                .expect_ready()
                .type_and_submit('konsole')
        )
        return cls()

    def expect_ready(self, timeout=30):
        return self.expect("empty_konsole")
