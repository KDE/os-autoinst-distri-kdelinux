# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from testapi import *

from lib.openqa.sessions.base import BaseSession
from lib.openqa.sessions.mixins.openable import OpenableSessionMixin


class DiscoverSession(BaseSession, OpenableSessionMixin):
    default_app_name = "discover"
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
        return self.click('discover_updates_page_refresh', timeout=timeout, button=button, dclick=1)

    def check_discover_updates_still_has_pending_updates(self, timeout=60, button='left'):
        if self.check_screen("discover_updates_still_has_pending_updates"):
            self.click("discover_updates_still_has_pending_updates", timeout=timeout, button=button)
        return self.expect_and_click_discover_updates_page_refresh(timeout=300)

    def expect_discover_upgrade_completed(self, timeout=60):
        return self.expect('discover_upgrade_completed', timeout=timeout)
