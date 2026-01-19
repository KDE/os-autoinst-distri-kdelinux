from testapi import *
from lib.sessions.app.calamares import CalamaresSession


def run(self):
    (
        CalamaresSession
            .ensure_active(launch_app=False)
            .expect_timezone_screen()
            .click_calamares_timezone_screen_next_button()
    )
