from testapi import *
from lib.openqa import serial_test

def run(self):
    test = serial_test.SerialTest('basic_test')
    test.run_cmd('/tests/venv/bin/python /tests/sut/scripts/basic_test.py')
