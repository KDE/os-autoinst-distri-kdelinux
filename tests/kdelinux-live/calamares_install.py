from testapi import *
from lib.openqa import serial_test

def run(self):
    test = serial_test.SerialTest('calamares_install')
    test.run_selenium('/usr/local/bin/calamares /tests/sut/scripts/calamares_install.py')
