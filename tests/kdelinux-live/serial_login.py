from testapi import *
from lib import serial_test
from lib import user_manager

def run(self):
    serial_test.session.login(user_manager.live())

def test_flags(self):
    return {'fatal': 1}
