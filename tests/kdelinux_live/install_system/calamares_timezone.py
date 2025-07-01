from testapi import *

def run(self):
    # check if the timezone screen shows
    assert_screen(
        'calamares_timezone_screen',
        'timeout', 30
    )

    # click the button to go to the next page
    assert_and_click(
        'calamares_timezone_screen_next_btn',
        'timeout', 60,
        'button', 'left'
    )