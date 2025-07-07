from testapi import *
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from lib.sessions.plasma_desktop import PlasmaDesktopSession

def run(self):
    (
        PlasmaDesktopSession
            .current()
            .right_click_empty_desktop()
            .expect_plasma_desktop_right_click_menu()
            .click_plasma_desktop_right_click_menu_create_new()
            .expect_plasma_desktop_right_click_create_new_menu()
            .click_plasma_desktop_right_click_create_new_menu_text_file()
            .expect_plasma_desktop_create_file_popup()
            .click_plasma_desktop_create_file_popup_ok_btn()
            .expect_plasma_desktop_new_file_created()
    )
