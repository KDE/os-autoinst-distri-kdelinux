from testapi import *

def switch_to_tty(login=True, user_role='root'):
    send_key('ctrl-alt-f3')
    if login:
        if user_role == 'root':
            type_string('root')
        else:
            type_string(user_role)
        send_key('ret')
        assert_screen('tty-login-prompt', timeout=10)
        type_string('password')

def type_and_submit(text):
    type_string(text)
    send_key('ret')
