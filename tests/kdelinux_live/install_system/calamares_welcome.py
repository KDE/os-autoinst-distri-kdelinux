from time import sleep

from testapi import *

import os
import sys# check whether booted into desktop screen

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from lib.sessions.konsole import KonsoleSession

def run(self):
    (
        KonsoleSession
            .open_via_krunner()
            .expect_ready()
            .type_and_submit('sudo pkexec calamares')
    )

    # Check if the calamares installer pop up
    assert_screen(
        'calamares_welcome_screen',
        'timeout', 30
    )

    # Click the button to jump to the next page
    # Todo: i18n,
    assert_and_click(
        'calamares_welcome_screen_next_btn',
        'timeout', 60,
        'button', 'left'
    )
