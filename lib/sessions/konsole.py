from testapi import *

from lib.sessions.base import BaseSession
from lib.sessions.krunner import KRunnerSession

class KonsoleSession(BaseSession):
    @classmethod
    def open_via_krunner(cls):
        (
            KRunnerSession
                .open()
                .wait_ready()
                .command('konsole')
        )
        return cls()

    def wait_ready(self):
        return self.expect("empty_konsole")
