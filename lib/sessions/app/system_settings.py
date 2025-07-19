from testapi import *
from lib.sessions.base import BaseSession
from lib.sessions.mixins.openable import OpenableSessionMixin


class SystemSettingsSession(BaseSession, OpenableSessionMixin):
    default_app_name = 'system settings'
    allowed_open_strategies = ['krunner', 'kickoff']

    def expect_ready(self, timeout=30):
        return self.expect('system_settings_quick_settings_page', timeout)

    def click_system_settings_searchbar(self, timeout=30, button='left'):
        return self.click('system_settings_searchbar', timeout=timeout, button=button)

    def expect_system_settings_login_screen_sddm_page_query_result(self, timeout=30):
        return self.expect('system_settings_login_screen_sddm_page_query_result', timeout)

    def click_system_settings_login_screen_sddm_sidebar_item(self, timeout=30, button='left'):
        return self.click('system_settings_login_screen_sddm_sidebar_item', timeout=timeout, button=button)

    def expect_system_settings_initial_login_screen_sddm_page(self, timeout=30):
        return self.expect('system_settings_initial_login_screen_sddm_page', timeout)

    def click_system_settings_login_screen_sddm_page_behavior_button(self, timeout=30, button='left'):
        return self.click('system_settings_login_screen_sddm_page_behavior_button', timeout, button)

    def expect_system_settings_login_screen_sddm_page_initial_behavior_subpage(self, timeout=30):
        return self.expect('system_settings_login_screen_sddm_page_initial_behavior_subpage', timeout)

    def click_system_settings_login_screen_sddm_page_automatically_login_checkbox(self, timeout=30, button='left'):
        return self.click('system_settings_login_screen_sddm_page_automatically_login_checkbox', timeout=timeout,
                          button=button)

    def click_system_settings_login_screen_sddm_page_apply_button(self, timeout=30, button='left'):
        return self.click('system_settings_login_screen_sddm_page_apply_button', timeout=timeout, button=button)

    def query(self, query_text):
        type_string(query_text)
        return self
