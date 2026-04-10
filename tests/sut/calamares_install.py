from testapi import *
from lib import serial_test

def run(self):
    serial_test.run('TEST_WITH_KWIN_WAYLAND=0 selenium-webdriver-at-spi-run /tests/venv/bin/python /tests/sut/scripts/calamares_install.py')
