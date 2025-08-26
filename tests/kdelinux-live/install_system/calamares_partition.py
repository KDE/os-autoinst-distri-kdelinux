from testapi import *

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from lib.sessions.app.calamares import CalamaresSession


def run(self):
    (
        CalamaresSession
            .ensure_active(launch_app=False)
            .expect_calamares_partition_screen()
            .click_calamares_partition_screen_storage_device_listview()
            .click_calamares_partition_screen_storage_device_listview_vdb()
            .click_calamares_partition_screen_erasedisk_radio()
            .click_calamares_partition_screen_install_button()
    )
