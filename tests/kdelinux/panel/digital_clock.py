from testapi import *
from lib.sessions.syscore.plasma_desktop import PlasmaDesktopSession


def run(self):
    (
        PlasmaDesktopSession
            .ensure_active()
            .click_plasma_panel_digital_clock_icon()
            .expect_plasma_panel_digital_clock_default_popup()
    )
