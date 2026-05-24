# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from testapi import *
from lib.openqa.sessions.syscore.plasma_desktop import PlasmaDesktopSession


def run(self):
    (
        PlasmaDesktopSession
            .ensure_active()
            .click_plasma_panel_system_tray_icon()
            .expect_plasma_panel_system_tray_default_popup()
    )
