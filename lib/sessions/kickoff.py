from testapi import *
from lib.sessions.base import BaseSession

class KickOffSession(BaseSession):
    default_app_name = 'kickoff'
    allowed_open_strategies = []

    @classmethod
    def open(cls, method=None):
        send_key('meta')
        instance = cls()
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=30):
        return self.expect('empty_kickoff', timeout=timeout)

    def click_kickoff_searchbar(self, timeout=30, button='left'):
        return self.click('kickoff_searchbar', timeout=timeout, button=button)

    def click_kickoff_icon_on_panel(self, timeout=30, button='left'):
        return self.click('kickoff-icon-on-panel', timeout, button)