from testapi import *
from lib.openqa.sessions.base import BaseSession


class KickOffSession(BaseSession):

    @classmethod
    def ensure_active(cls):
        send_key('super')
        instance = cls()
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=30):
        return self.expect('empty_kickoff', timeout=timeout)

    def click_kickoff_searchbar(self, timeout=30, button='left'):
        return self.click('kickoff_searchbar', timeout=timeout, button=button)

    def click_kickoff_icon_on_panel(self, timeout=30, button='left'):
        return self.click('kickoff_icon_on_panel', timeout, button)
