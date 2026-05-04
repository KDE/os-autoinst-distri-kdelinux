from testapi import *
from lib.openqa import cli_test
from lib import paths
from lib import user_manager

def run(self):
    test = cli_test.CliTest('calamares_install', timeout=300)
    test.run_selenium(user=user_manager.live())
