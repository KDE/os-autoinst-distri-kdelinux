from testapi import *
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession
from lib.openqa import cli_test
from lib import user_manager

def run(self):
    test = cli_test.CliTest('plasma_setup')
    test.run_selenium(user=user_manager.plasma_setup())

    # Make sure at least the kickoff icon on the bottom panel shows up.
    #PlasmaDesktopSession.ensure_active()
