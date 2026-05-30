# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from testapi import *
from lib.openqa.sessions.base import BaseSession


class PlasmaDesktopSession(BaseSession):

    @classmethod
    def ensure_active(cls):
        instance = cls()
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=100):
        """
        Use the bottom panel as an indicator of desktop readiness.

        This may not be entirely accurate, but based on my observation, the bottom panel tends to load last.
        So if it's visible, the entire desktop environment is likely ready.
        """
        self.expect('kickoff_icon_on_panel', timeout)

