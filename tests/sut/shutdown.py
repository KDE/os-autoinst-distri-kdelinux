from testapi import *
from lib import serial_test

def run(self):
    serial_test.run('shutdown.py')

def test_flags(self):
    return {'fatal': 1}
