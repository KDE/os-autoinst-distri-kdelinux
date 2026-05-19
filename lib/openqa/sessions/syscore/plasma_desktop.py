from testapi import *
from lib.openqa.sessions.base import BaseSession


class PlasmaDesktopSession(BaseSession):

    @classmethod
    def ensure_active(cls):
        instance = cls()
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=100):
        """
        Use the bottom panel as an indicator of desktop readiness.

        This may not be entirely accurate, but based on my observation, the bottom panel tends to load last.
        So if it's visible, the entire desktop environment is likely ready.
        """
        self.expect('kickoff_icon_on_panel', timeout)

    def switch_windows(self, fast=True, timeout=30):
        '''
        hold the `alt` key and press tab to ensure the `task switcher` overview shows up, then release the `alt` key.

        :param fast:
        :param timeout:
        :return:
        '''
        if fast:
            send_key('alt-tab')
        else:
            hold_key('alt')
            send_key('tab')
            self.expect("windows_switcher_two_windows", timeout)
            release_key('alt')
        return self
