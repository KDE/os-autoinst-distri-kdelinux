from testapi import *
from lib.openqa.sessions.app.system_settings import SystemSettingsSession
from lib.openqa.sessions.app.konsole import KonsoleSession
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession


def run(self):
    # Open konsole
    (
        KonsoleSession
            .ensure_active(open_strategy='krunner', needle="krunner_text_konsole")
    )

    # Open system-setting
    (
        SystemSettingsSession
            .ensure_active(open_strategy='krunner', needle="krunner_text_systemsettings")
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
