from testapi import *

def run(self):
    # click the partition screen storage device listview
    assert_and_click(
        'installer_partition_screen_storage_device_listview',
        'timeout', 60,
        'button', 'left'
    )

    # select the vdb(qcow2) to install our system
    assert_and_click(
        'installer_partition_screen_storage_device_listview_vdb',
        'timeout', 60,
        'button', 'left'
    )
    
    # select erase disk
    assert_and_click(
        'installer_partition_screen_erasedisk_radio',
        'timeout', 60,
        'button', 'left'
    )

    # click the partition screen next button
    assert_and_click(
        'installer_partition_screen_next_btn',
        'timeout', 60,
        'button', 'left'
    )