from testapi import *
from lib.openqa.sessions.app.system_settings import SystemSettingsSession


def run(self):
    # todo: add `DO_INSTALL` check
    (
        SystemSettingsSession
            .ensure_active(open_strategy='kickoff', needle='kickoff_system_settings_query_result', timeout=30)
            .click_system_settings_searchbar()
            .query('Login Screen ')  # Empty Space needed.
            .expect_system_settings_login_screen_sddm_page_query_result()
            .click_system_settings_login_screen_sddm_sidebar_item()
            .expect_system_settings_initial_login_screen_sddm_page()
            .click_system_settings_login_screen_sddm_page_behavior_button()
            .expect_system_settings_login_screen_sddm_page_initial_behavior_subpage()
            .click_system_settings_login_screen_sddm_page_automatically_login_checkbox()
            .click_system_settings_login_screen_sddm_page_apply_button()
            .expect_gui_password_pop_up()
            .submit_gui_password()
            .expect_system_settings_login_screen_sddm_page_configure_completed()
            .close_window()
    )
