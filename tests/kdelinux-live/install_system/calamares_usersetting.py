from testapi import *
from lib.sessions.app.calamares import CalamaresSession


def run(self):
    (
        CalamaresSession
            .ensure_active(launch_app=False)
            .expect_calamares_usersetting_screen()
            .click_calamares_usersetting_username_input()
            .type_calamares_usersetting_username()
            .click_calamares_usersetting_password_input()
            .type_calamares_usersetting_password()
            .click_calamares_usersetting_password_repeat_input()
            .type_calamares_usersetting_password_repeat()
            .click_calamares_usersetting_next_btn()
    )


    