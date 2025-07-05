from testapi import *

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.app.system_settings import SystemSettingsSession


def run(self):
    (
        SystemSettingsSession
            .open(method='kickoff')
            .click_system_settings_searchbar()
            .query('Login Screen ')  # Empty Space needed.
            .expect_system_settings_login_screen_sddm_page_query_result()
            .click_system_settings_login_screen_sddm_sidebar_item()
            .expect_system_settings_initial_login_screen_sddm_page()
            .click_system_settings_login_screen_sddm_page_behavior_button()
            .expect_system_settings_login_screen_sddm_page_initial_behavior_subpage()
            .click_system_settings_login_screen_sddm_page_automatically_login_checkbox()
            .click_system_settings_login_screen_sddm_page_apply_button()
            .submit_gui_password()
    )

def post_run_hook():
    (
        SystemSettingsSession
            .current()
            .close_window()
    )