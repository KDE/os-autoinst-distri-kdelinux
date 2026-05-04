from testapi import *
from lib.openqa import cli_test
from lib import paths

def run(self):
    test = cli_test.CliTest('basic_test')
    test.run_python()
