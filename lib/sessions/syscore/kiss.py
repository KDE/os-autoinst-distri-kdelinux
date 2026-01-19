from testapi import *
from lib.sessions.base import BaseSession

class KISSSession(BaseSession):

    @classmethod
    def ensure_active(cls):
        instance = cls()
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=30):
        """
        Just the "Welcome to Plasma Desktop Page", with a low match level value due to the volatile background.
        :return:
        """
        return self.expect('kiss_welcome_page', timeout=timeout)

    def click_kiss_begin_setup_button(self, timeout=30, button='left'):
        return self.click('kiss_begin_setup_button', timeout=timeout, button=button)

    def expect_kiss_language_settings_initial_page(self, timeout=30):
        return self.expect('kiss_language_settings_initial_page', timeout=timeout)

    def click_kiss_language_settings_next_button(self, timeout=30, button='left'):
        return self.click('kiss_language_settings_next_button', timeout=timeout, button=button)

    def expect_kiss_keyboard_layout_initial_page(self, timeout=30):
        return self.expect('kiss_keyboard_layout_initial_page', timeout=timeout)

    def click_kiss_keyboard_layout_next_button(self, timeout=30, button='left'):
        return self.click('kiss_keyboard_layout_next_button', timeout=timeout, button=button)

    def expect_kiss_before_we_get_started_initial_page(self, timeout=30):
        return self.expect('kiss_before_we_get_started_initial_page', timeout=timeout)

    def click_kiss_before_we_get_started_next_button(self, timeout=30, button='left'):
        return self.click('kiss_before_we_get_started_next_button', timeout=timeout, button=button)

    def expect_kiss_about_you_initial_page(self, timeout=30):
        return self.expect('kiss_about_you_initial_page', timeout=timeout)

    def click_kiss_about_you_fullname_input(self, timeout=30, button='left'):
        return self.click('kiss_about_you_fullname_input', timeout=timeout, button=button)

    def kiss_about_you_enter_username(self, username='kdelinuxtester'):
        type_string(username)
        return self

    def click_kiss_about_you_next_button(self, timeout=30, button='left'):
        return self.click('kiss_about_you_next_button', timeout=timeout, button=button)

    def expect_kiss_set_a_password_initial_page(self, timeout=30):
        return self.expect('kiss_set_a_password_initial_page', timeout=timeout)

    def click_kiss_set_a_password_first_time_input(self, timeout=30, button='left'):
        return self.click('kiss_set_a_password_first_time_input', timeout=timeout, button=button)

    def kiss_set_a_password_enter_password(self, password='1122334455'):
        type_string(password)
        return self

    def click_kiss_set_a_password_second_time_input(self, timeout=30, button='left'):
        return self.click('kiss_set_a_password_second_time_input', timeout=timeout, button=button)

    def click_kiss_set_a_password_next_button(self, timeout=30, button='left'):
        return self.click('kiss_set_a_password_next_button', timeout=timeout, button=button)

    def expect_kiss_time_and_date_initial_page(self, timeout=30):
        return self.expect('kiss_time_and_date_initial_page', timeout=timeout)

    def click_kiss_time_and_date_next_button(self, timeout=30, button='left'):
        return self.click('kiss_time_and_date_next_button', timeout=timeout, button=button)

    def expect_kiss_completed(self, timeout=30):
        return self.expect('kiss_completed', timeout=timeout)

    def click_kiss_completed_finish_button(self, timeout=30, button='left'):
        return self.click('kiss_completed_finish_button', timeout=timeout, button=button)