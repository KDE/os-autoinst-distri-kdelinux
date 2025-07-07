from testapi import *
import sys, os

from lib.sessions.app.system_settings import SystemSettingsSession
from lib.sessions.konsole import KonsoleSession

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from lib.sessions.plasma_desktop import PlasmaDesktopSession


def run(self):
    (
        KonsoleSession
            .open()
    )
    (
        SystemSettingsSession
            .open()
    )
    (
        PlasmaDesktopSession
            .current()
            .switch_windows(fast=False)
    )
    (
        KonsoleSession
            .current()
            .expect_ready()
            .close_window()
    )
    (
        SystemSettingsSession
            .current()
            .close_window()
    )
