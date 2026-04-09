from testapi import *
from lib import serial_test

def run(self):
    serial_test.run('/tests/venv/bin/python /tests/sut/scripts/basic_test.py')
