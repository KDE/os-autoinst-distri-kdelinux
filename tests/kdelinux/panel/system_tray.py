from testapi import *
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession


def run(self):
    (
        PlasmaDesktopSession
            .ensure_active()
            .click_plasma_panel_system_tray_icon()
            .expect_plasma_panel_system_tray_default_popup()
    )
