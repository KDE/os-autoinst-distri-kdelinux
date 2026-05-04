from testapi import *
from lib.openqa.sessions.base import BaseSession
from lib.openqa.sessions.mixins.openable import OpenableSessionMixin


class CalamaresSession(BaseSession, OpenableSessionMixin):
    default_app_name = 'calamares'
    allowed_open_strategies = ['krunner', 'konsole']

    def expect_ready(self, timeout=30):
        return self.expect('calamares_welcome_screen')

    def click_welcome_screen_next_button(self, timeout=60, button='left'):
        return self.click('calamares_welcome_screen_next_btn', timeout, button)

    def expect_timezone_screen(self, timeout=30):
        return self.expect('calamares_timezone_screen', timeout)

    def click_calamares_timezone_screen_next_button(self, timeout=60, button='left'):
        return self.click('calamares_timezone_screen_next_btn', timeout, button)

    def expect_calamares_keyboard_screen(self, timeout=30):
        return self.expect('calamares_keyboard_screen', timeout)

    def click_calamares_keyboard_screen_next_button(self, timeout=60, button='left'):
        return self.click('calamares_keyboard_screen_next_btn', timeout, button)

    def expect_calamares_partition_screen(self, timeout=30):
        # idk why the needle of entire disk-partitioning page is missing, will label it and implement later.
        return self.expect('calamares_partition_screen', timeout)

    def click_calamares_partition_screen_storage_device_listview(self, timeout=60, button='left'):
        return self.click('calamares_partition_screen_storage_device_listview', timeout, button)

    def click_calamares_partition_screen_storage_device_listview_vdb(self, timeout=60, button='left'):
        return self.click('calamares_partition_screen_storage_device_listview_vdb', timeout, button)

    def click_calamares_partition_screen_erasedisk_radio(self, timeout=60, button='left'):
        return self.click('calamares_partition_screen_erasedisk_radio', timeout, button)

    def click_calamares_partition_screen_next_btn(self, timeout=60, button='left'):
        return self.click('calamares_partition_screen_next_btn', timeout, button)

    def expect_calamares_usersetting_screen(self, timeout=60):
        return self.expect('calamares_usersetting_screen', timeout)

    def click_calamares_usersetting_username_input(self, timeout=60, button='left'):
        return self.click('calamares_usersetting_username_input', timeout, button)

    def type_calamares_usersetting_username(self):
        type_string('kdelinuxtester')
        return self

    def click_calamares_usersetting_password_input(self, timeout=60, button='left'):
        return self.click('calamares_usersetting_password_input', timeout, button)

    def type_calamares_usersetting_password(self):
        type_string('1122334455')  # not sure if it is good here to hardcode username and password.
        return self

    def click_calamares_usersetting_password_repeat_input(self, timeout=60, button='left'):
        return self.click('calamares_usersetting_password_repeat_input', timeout, button)

    def type_calamares_usersetting_password_repeat(self):
        type_string('1122334455')
        return self

    def click_calamares_usersetting_next_btn(self, timeout=15, button='left'):
        return self.click('calamares_usersetting_next_btn', timeout, button)

    def expect_calamares_installing(self, timeout=60):
        return self.expect('calamares_installing', timeout)

    def expect_calamares_install_completed(self, timeout=1000):
        return self.expect('calamares_install_completed', timeout)

    def click_calamares_partition_screen_install_button(self, timeout=60, button='left'):
        return self.click('calamares_partition_screen_install_button', timeout, button)
