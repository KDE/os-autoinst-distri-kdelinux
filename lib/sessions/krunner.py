from testapi import *
from lib.sessions.base import BaseSession

class KRunnerSession(BaseSession):
    @classmethod
    def open(cls):
        send_key('alt-spc')
        return cls()

    def wait_ready(self):
        return self.expect("empty_krunner")