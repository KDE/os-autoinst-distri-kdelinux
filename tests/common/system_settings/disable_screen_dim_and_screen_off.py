from testapi import *
from lib.sessions.app.system_settings import SystemSettingsSession


def run(self):
    (
        SystemSettingsSession
            .ensure_active(open_strategy='kickoff', needle='kickoff_system_settings_query_result', timeout=30)
            .click_system_settings_searchbar()
            .query('Power Manageme') # Intentionally keep it partial
            .expect_and_click_system_settings_power_management_query_result()
            .expect_system_settings_power_management_default_page()
            .expect_and_click_system_settings_power_management_dim_listview()
            .expect_and_click_system_settings_power_management_dim_listview_option_never()
            .expect_and_click_system_settings_power_management_turnoffscreen_listview()
            .expect_and_click_system_settings_power_management_turnoffscreen_listview_option_never()
            .expect_system_settings_power_management_dim_and_turnoff_disabled()
            .click_system_settings_power_management_apply_button()
            .close_window()
    )
