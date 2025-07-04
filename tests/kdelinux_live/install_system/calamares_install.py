from testapi import *

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.app.calamares import CalamaresSession

def run(self):
    (
        CalamaresSession
            .current()
            .expect_calamares_installing()
            .expect_calamares_install_completed()
    )
