from testapi import *

def run(self):
    assert_screen(
        'calamares_usersetting_screen',
        'timeout', 60
    )
    
    assert_and_click('calamares_usersetting_username_input')
    type_string('kdelinuxtester')
    
    # enter password
    assert_and_click('calamares_usersetting_password_input')
    type_string('1122334455')

    # confirm password
    assert_and_click('calamares_usersetting_password_repeat_input')
    type_string('1122334455')
    
    # click next button
    assert_and_click(
        'calamares_usersetting_next_btn',
        'timeout', 15,
        'button', 'left'
    )
    