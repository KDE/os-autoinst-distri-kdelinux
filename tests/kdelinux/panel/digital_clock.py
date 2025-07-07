from testapi import *
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from lib.sessions.plasma_desktop import PlasmaDesktopSession

def run(self):
    (
        PlasmaDesktopSession
            .current()
            .click_plasma_panel_digital_clock_icon()
            .expect_plasma_panel_digital_clock_default_popup()
    )