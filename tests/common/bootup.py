from testapi import *

def run(self):
    # '0': full system, '1': live system
    DO_INSTALL = get_var("DO_INSTALL")

    # wait for bootloader to appear
    assert_screen('uefi_screen', timeout=30)

    # press enter to boot right away
    send_key('ret')

    # check if kde is booting
    assert_screen('booting_screen', timeout=30)

    # For Live System, it will automatically enter the desktop without entering password
    if DO_INSTALL == '1':
        assert_screen('welcome_desktop_screen', timeout=60)