from testapi import *

def run(self):
    power('on')
    DO_INSTALL = get_var("DO_INSTALL")
    if DO_INSTALL == '1':
        assert_screen('uefi_screen', 'timeout', 30)
        send_key('ret')
    assert_screen('booting_screen', 'timeout', 30)
    if DO_INSTALL == '1':
        assert_screen('welcome_desktop_screen', 'timeout', 60)
    else:
        assert_screen('plasma_welcome', 'timeout', 60)
