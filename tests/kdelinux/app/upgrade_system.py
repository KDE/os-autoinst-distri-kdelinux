from testapi import *
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))
from lib.sessions.app.discover import DiscoverSession


def run(self):
    (
        DiscoverSession
            .ensure_active()
            .expect_and_click_discover_sidebar_updates()
            .expect_discover_updates_page()
            .click_discover_updates_page_updates_all_button()
            .expect_discover_tasks_running()
            .expect_and_click_discover_updates_page_refresh(timeout=300)
            .expect_discover_upgrade_completed()
    )

