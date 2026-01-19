from testapi import *
from lib.sessions.app.calamares import CalamaresSession


def run(self):
    (
        CalamaresSession
            .ensure_active(open_strategy='konsole', needle="krunner_text_konsole")
            .click_welcome_screen_next_button()
    )
