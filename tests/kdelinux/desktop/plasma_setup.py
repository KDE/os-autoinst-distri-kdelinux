from testapi import *
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession
from lib.openqa import serial_test

def run(self):
    test = serial_test.SerialTest('plasma_setup')
    test.run_selenium('$(pgrep -n plasma-setup) /tests/sut/scripts/plasma_setup.py')

    # Make sure at least the kickoff icon on the bottom panel shows up.
    PlasmaDesktopSession.ensure_active()
