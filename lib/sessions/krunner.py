from testapi import *
from lib.sessions.base import BaseSession

class KRunnerSession(BaseSession):

    def expect_ready(self, timeout=30):
        return self.expect("empty_krunner", timeout=timeout)