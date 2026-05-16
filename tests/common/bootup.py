from testapi import *

def run(self):
    power('on')
    # check if we see plymouth
    assert_screen('booting_screen', 'timeout', 30)
    # wait for kick-off icon on panel to show up
    assert_screen('kickoff_icon_on_panel', 'timeout', 60)
