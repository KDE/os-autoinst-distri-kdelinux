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
        '''
            Same issue with click_system_settings_screen_locking_sidebar_item()
        '''
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

    def expect_system_settings_screen_locking_query_result(self, timeout=30):
        return self.expect('system_settings_screen_locking_query_result', timeout)

    def click_system_settings_screen_locking_sidebar_item(self, timeout=30, button='left'):
        '''
        Maybe this can be merged with expect_system_settings_screen_locking_query_result.
        Just like what we did in expect_and_click_system_settings_power_management_query_result().
        '''
        return self.click('system_settings_screen_locking_sidebar_item', timeout=timeout, button=button)

    def expect_system_settings_screen_locking_default_page(self, timeout=30):
        return self.expect('system_settings_screen_locking_default_page', timeout)

    def expect_and_click_system_settings_screen_locking_default_page_lockscreen_listview(self, timeout=30, button='left'):
        return self.click('system_settings_screen_locking_default_page_lockscreen_listview', timeout=timeout, button=button)

    def click_system_settings_screen_locking_default_page_lockscreen_listview_option_never(self, timeout=30, button='left'):
        return self.click('system_settings_screen_locking_default_page_lockscreen_listview_option_never', timeout=timeout, button=button)

    def click_system_settings_screen_locking_default_page_apply_button(self, timeout=30, button='left'):
        return self.click('system_settings_screen_locking_default_page_apply_button', timeout=timeout, button=button)

    def expect_and_click_system_settings_power_management_query_result(self, timeout=30, button='left'):
        return self.click('system_settings_power_management_query_result', timeout=timeout, button=button)

    def expect_system_settings_power_management_default_page(self, timeout=30):
        return self.expect('system_settings_power_management_default_page', timeout)

    def expect_and_click_system_settings_power_management_dim_listview(self, timeout=30, button='left'):
        return self.click('system_settings_power_management_dim_listview', timeout=timeout, button=button)

    def expect_and_click_system_settings_power_management_dim_listview_option_never(self, timeout=30, button='left'):
        return self.click('system_settings_power_management_dim_listview_option_never', timeout=timeout, button=button)

    def expect_and_click_system_settings_power_management_turnoffscreen_listview(self, timeout=30, button='left'):
        return self.click('system_settings_power_management_turnoffscreen_listview', timeout=timeout, button=button)

    def expect_and_click_system_settings_power_management_turnoffscreen_listview_option_never(self, timeout=30, button='left'):
        return self.click('system_settings_power_management_turnoffscreen_listview_option_never', timeout=timeout, button=button)

    def expect_system_settings_power_management_dim_and_turnoff_disabled(self, timeout=30):
        return self.expect('system_settings_power_management_dim_and_turnoff_disabled', timeout)

    def click_system_settings_power_management_apply_button(self, timeout=30, button='left'):
        return self.click('system_settings_power_management_apply_button', timeout=timeout, button=button)

    def query(self, query_text):
        type_string(query_text)
        return self
