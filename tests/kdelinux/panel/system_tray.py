from testapi import *
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.app.plasma_panel import PlasmaPanelSession


def run(self):
    (
        PlasmaPanelSession
            .open()
            .click_plasma_panel_system_tray_icon()
            .expect_plasma_panel_system_tray_default_popup()
    )
