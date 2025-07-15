from testapi import *
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.plasma_desktop import PlasmaDesktopSession


def run(self):
    (
        PlasmaDesktopSession
            .open()
            .click_plasma_panel_system_tray_icon()
            .expect_plasma_panel_system_tray_default_popup()
    )
