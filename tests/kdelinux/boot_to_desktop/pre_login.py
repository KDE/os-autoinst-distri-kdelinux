from testapi import *


def run(self):
    send_key('ret')
    # wait for bootloader to appear
    assert_screen('uefi_screen', timeout=30)

    # press enter to boot right away
    send_key('ret')

    # check if kde is booting
    assert_screen('booting_screen', timeout=30)
