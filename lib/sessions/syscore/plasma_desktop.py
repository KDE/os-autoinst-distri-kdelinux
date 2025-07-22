from lib.sessions.base import BaseSession
from testapi import *


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

    def click_plasma_panel_system_tray_icon(self, timeout=30, button='left'):
        return self.click('plasma_panel_system_tray_icon', timeout=timeout, button=button)

    def expect_plasma_panel_system_tray_default_popup(self, timeout=30):
        return self.expect('plasma_panel_system_tray_default_popup', timeout=timeout)

    def click_plasma_panel_digital_clock_icon(self, timeout=30, button='left'):
        mouse_set(935, 730)
        mouse_click('left')
        return self

    def expect_plasma_panel_digital_clock_default_popup(self, timeout=30):
        return self.expect('plasma_panel_digital_clock_default_popup', timeout=timeout)

    def right_click_empty_desktop(self, timeout=30):
        mouse_set(0, 0)
        mouse_click('right')
        return self

    def expect_plasma_desktop_right_click_menu(self, timeout=30):
        return self.expect('plasma_desktop_right_click_menu', timeout=timeout)

    def click_plasma_desktop_right_click_menu_create_new(self, timeout=30, button='left'):
        return self.click('plasma_desktop_right_click_menu_create_new', timeout, button)

    def expect_plasma_desktop_right_click_create_new_menu(self, timeout=30):
        return self.expect('plasma_desktop_right_click_create_new_menu', timeout=timeout)

    def click_plasma_desktop_right_click_create_new_menu_text_file(self, timeout=30, button='left'):
        return self.click('plasma_desktop_right_click_create_new_menu_text_file', timeout, button)

    def expect_plasma_desktop_create_file_popup(self, timeout=30):
        return self.expect('plasma_desktop_create_file_popup', timeout=timeout)

    def click_plasma_desktop_create_file_popup_ok_btn(self, timeout=30, button='left'):
        return self.click('plasma_desktop_create_file_popup_ok_btn', timeout, button)

    def expect_plasma_desktop_new_file_created(self, timeout=30):
        return self.expect('plasma_desktop_new_file_created', timeout=timeout)

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
