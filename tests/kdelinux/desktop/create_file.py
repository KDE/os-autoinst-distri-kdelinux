# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from testapi import *
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession


def run(self):
    (
        PlasmaDesktopSession
            .ensure_active()
            .right_click_empty_desktop()
            .expect_plasma_desktop_right_click_menu()
            .click_plasma_desktop_right_click_menu_create_new()
            .expect_plasma_desktop_right_click_create_new_menu()
            .click_plasma_desktop_right_click_create_new_menu_text_file()
            .expect_plasma_desktop_create_file_popup()
            .click_plasma_desktop_create_file_popup_ok_btn()
            .expect_plasma_desktop_new_file_created()
    )
