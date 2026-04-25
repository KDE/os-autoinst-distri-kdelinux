from testapi import *
from lib.sessions.syscore.plasma_desktop import PlasmaDesktopSession
from lib import serial_test

def run(self):
    serial_test.run('/tests/sut/openqa-selenium-webdriver-at-spi-run $(pgrep -n plasma-setup) /tests/sut/scripts/plasma_setup.py') # TODO
    # Make sure at least the kickoff icon on the bottom panel shows up.
    PlasmaDesktopSession.ensure_active()


