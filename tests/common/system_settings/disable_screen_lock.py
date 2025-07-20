from testapi import *
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from lib.sessions.app.system_settings import SystemSettingsSession


def run(self):
    (
        SystemSettingsSession
            .ensure_active(open_strategy='kickoff', needle='kickoff_system_settings_query_result', timeout=30)
            .click_system_settings_searchbar()
            .query('Screen Locking')
            .expect_system_settings_screen_locking_query_result()
            .click_system_settings_screen_locking_sidebar_item()
            .expect_system_settings_screen_locking_default_page()
            .expect_and_click_system_settings_screen_locking_default_page_lockscreen_listview()
            .click_system_settings_screen_locking_default_page_lockscreen_listview_option_never()
            .click_system_settings_screen_locking_default_page_apply_button()
            .close_window()
        # todo: verify the password prompt will pop up if running this under full system
    )
