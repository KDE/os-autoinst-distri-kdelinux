from testapi import *

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.app.calamares import CalamaresSession


def run(self):
    (
        CalamaresSession
            .ensure_active(open_strategy='konsole')
            .click_welcome_screen_next_button()
    )
