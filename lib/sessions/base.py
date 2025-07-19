from testapi import *


class BaseSession:

    def expect(self, needle, timeout=30):
        assert_screen(needle, 'timeout', timeout)
        return self

    def click(self, needle, timeout=30, button='left'):
        assert_and_click(needle, 'timeout', timeout, 'button', button)
        return self

    def expect_ready(self, timeout=30):
        raise NotImplementedError(f"{self.__class__.__name__} must implement expect_ready()")

    def type_and_submit(self, text, **kwargs):
        needle = kwargs.get('needle')
        timeout = kwargs.get('timeout', 30)
        type_string(text)
        if needle:
            self.expect(needle, timeout)
        send_key('ret')
        return self

    def expect_gui_password_pop_up(self, timeout=30):
        return self.expect('gui_password_pop_up', timeout)

    def submit_gui_password(self):
        return self.type_and_submit('1122334455')

    def close_window(self):
        send_key('alt-f4')
        return self
