from testapi import *

def run(self):
    power('on')
    DO_INSTALL = get_var("DO_INSTALL")
    assert_screen('uefi_screen', 'timeout', 30)
    send_key('ret')
    assert_screen('booting_screen', 'timeout', 30)
    if DO_INSTALL == '1':
        assert_screen('welcome_desktop_screen', 'timeout', 60)
