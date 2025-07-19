from testapi import *
import sys, os

from lib.sessions.app.system_settings import SystemSettingsSession
from lib.sessions.app.konsole import KonsoleSession

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from lib.sessions.syscore.plasma_desktop import PlasmaDesktopSession


def run(self):
    # Open konsole
    (
        KonsoleSession
            .ensure_active()
    )

    # Open system-setting
    (
        SystemSettingsSession
            .ensure_active()
    )

    # Switch between these two apps
    (
        PlasmaDesktopSession
            .ensure_active()
            .switch_windows(fast=False)
    )

    # After switch, konsole should on top, close it
    (
        KonsoleSession
            .ensure_active(launch_app=False)
            .close_window()
    )

    # Close system-setting
    (
        SystemSettingsSession
            .ensure_active(launch_app=False)
            .close_window()
    )
