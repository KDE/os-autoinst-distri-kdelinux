from testapi import *

def run(self):
    assert_screen(
        'calamares_installing',
        'timeout', 60
    )

    # assert completed
    assert_screen(
        'calamares_install_completed',
        'timeout', 1000
    )