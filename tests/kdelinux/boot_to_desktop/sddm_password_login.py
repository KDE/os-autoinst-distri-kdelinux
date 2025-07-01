from testapi import *

def run(self):
    # check whether booted into desktop screen
    assert_and_click(
        'sddm_password_input',
        'timeout', 60
    )
    type_string('1122334455')
    send_key('ret')
    # check whether booted into desktop screen
    assert_screen('kdelinux_desktop_welcome', timeout=60)