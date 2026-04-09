from testapi import *
from lib import serial_test

def run(self):
    serial_test.run('selenium-webdriver-at-spi-run /tests/venv/bin/python /tests/sut/scripts/calamares_install.py')
