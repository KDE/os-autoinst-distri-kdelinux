from testapi import *
from lib import bootstrap_sut
from lib import user_manager

def run(self):
    bootstrap_sut.bootstrap(user_manager.installed())

def test_flags(self):
    return {'fatal': 1}
