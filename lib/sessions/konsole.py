from testapi import *

from lib.sessions.base import BaseSession
from lib.sessions.krunner import KRunnerSession

class KonsoleSession(BaseSession):
    default_app_name = 'konsole'
    allowed_strategies = ['krunner']

    def expect_ready(self, timeout=30):
        return self.expect('empty_konsole', timeout=timeout)
