from testapi import *
from lib.sessions.base import BaseSession

class KRunnerSession(BaseSession):
    default_app_name = 'krunner'
    allowed_open_strategies = []

    @classmethod
    def open(cls, method=None):
        """
        krunner cannot open itself. So the open function must be overridden.
        :param method:
        :return:
        """
        send_key("alt-spc")
        instance = cls()
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=30):
        return self.expect("empty_krunner", timeout=timeout)