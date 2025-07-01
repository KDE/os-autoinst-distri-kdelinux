from testapi import *

def run(self):
    # check if the keyboard screen shows
    assert_screen(
        'calamares_keyboard_screen',
        'timeout', 30
    )

    # click the keyboard screen next button
    assert_and_click(
        'calamares_keyboard_screen_next_btn',
        'timeout', 60,
        'button', 'left'
    )