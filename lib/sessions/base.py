from testapi import *

class BaseSession:
    def expect(self, needle, timeout=30):
        assert_screen(needle, 'timeout', timeout)
        return self

    def command(self, text):
        type_string(text)
        send_key('ret')
        return self
