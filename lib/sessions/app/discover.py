from testapi import *

from lib.sessions.base import BaseSession
from lib.sessions.mixins.openable import OpenableSessionMixin


class DiscoverSession(BaseSession, OpenableSessionMixin):
    default_app_name = "Discover"
    allowed_open_strategies = ['krunner', 'kickoff', 'konsole']

    def expect_ready(self, timeout=30):
        return self.expect('discover_home_page', timeout=timeout)

    def expect_and_click_discover_sidebar_updates(self, timeout=60, button='left'):
        return self.click('discover_sidebar_updates', timeout=timeout, button=button)

    def expect_discover_updates_page(self, timeout=60):
        return self.expect('discover_updates_page', timeout=timeout)

    def click_discover_updates_page_updates_all_button(self, timeout=60, button='left'):
        return self.click('discover_updates_page_updates_all_button', timeout=timeout, button=button)

    def expect_discover_tasks_running(self, timeout=60):
        return self.expect('discover_tasks_running', timeout=timeout)

    def expect_and_click_discover_updates_page_refresh(self, timeout=60, button='left'):
        return self.click('discover_updates_page_refresh', timeout=timeout, button=button)

    def expect_discover_upgrade_completed(self, timeout=60):
        return self.expect('discover_upgrade_completed', timeout=timeout)
