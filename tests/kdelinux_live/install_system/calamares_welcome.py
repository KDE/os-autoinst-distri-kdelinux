from time import sleep

from testapi import *

import os
import sys# check whether booted into desktop screen

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from lib.sessions.konsole import KonsoleSession

def run(self):
    # It used be able to open calamares via clicking a icon, however right now opening it via pkexec is the only solution
    # assert_and_click(
    #     'installer_icon',
    #     'dclick', True,
    #     'timeout', 60,
    #     'button', 'left'
    # )
    (
        KonsoleSession
            .open_via_krunner()
            .wait_ready()
            .command('sudo pkexec calamares')
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
