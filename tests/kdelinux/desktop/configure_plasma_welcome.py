from testapi import *
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from lib.sessions.syscore.plasma_welcome_settings import PlasmaWelcomeSettingsSession
from lib.sessions.syscore.plasma_desktop import PlasmaDesktopSession

def run(self):
    (
        PlasmaWelcomeSettingsSession
            .ensure_active()
            .click_plasma_welcome_settings_begin_setup_button()
            .expect_plasma_welcome_settings_language_settings_initial_page()
            .click_plasma_welcome_settings_language_settings_next_button()
            .expect_plasma_welcome_settings_keyboard_layout_initial_page()
            .click_plasma_welcome_settings_keyboard_layout_next_button()
            .expect_plasma_welcome_settings_before_we_get_started_initial_page()
            .click_plasma_welcome_settings_before_we_get_started_next_button()
            .expect_plasma_welcome_settings_about_you_initial_page()
            .click_plasma_welcome_settings_about_you_fullname_input()
            .plasma_welcome_settings_about_you_enter_username()
            .click_plasma_welcome_settings_about_you_next_button()
            .expect_plasma_welcome_settings_set_a_password_initial_page()
            .click_plasma_welcome_settings_set_a_password_first_time_input()
            .plasma_welcome_settings_set_a_password_enter_password()
            .click_plasma_welcome_settings_set_a_password_second_time_input()
            .plasma_welcome_settings_set_a_password_enter_password()
            .click_plasma_welcome_settings_set_a_password_next_button()
            .expect_plasma_welcome_settings_time_and_date_initial_page()
            .click_plasma_welcome_settings_time_and_date_next_button()
            .expect_plasma_welcome_settings_completed()
            .click_plasma_welcome_settings_completed_finish_button()
    )
    # Make sure at least the kickoff icon on the bottom panel shows up.
    PlasmaDesktopSession.ensure_active()


