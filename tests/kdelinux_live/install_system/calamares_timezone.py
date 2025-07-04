from testapi import *

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.app.calamares import CalamaresSession


def run(self):
    (
        CalamaresSession
            .current()
            .expect_timezone_screen()
            .click_calamares_timezone_screen_next_button()
    )