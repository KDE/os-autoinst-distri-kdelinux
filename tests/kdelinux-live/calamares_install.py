from testapi import *
from lib import serial_test

def run(self):
    serial_test.session.run('/tests/sut/openqa-selenium-webdriver-at-spi-run /usr/local/bin/calamares /tests/sut/scripts/calamares_install.py')
