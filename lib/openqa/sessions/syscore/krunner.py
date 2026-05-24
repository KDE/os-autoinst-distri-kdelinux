# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from testapi import *
from lib.openqa.sessions.base import BaseSession


class KRunnerSession(BaseSession):
    @classmethod
    def ensure_active(cls):
        """
        krunner cannot open itself. So the open function must be overridden.
        :param method:
        :return:
        """
        send_key("alt-spc")
        # KRunner somehow stores the previously executed app, so a backspace is needed to clear it.
        send_key('backspace')
        instance = cls()
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=30):
        self.expect('empty_krunner', timeout=timeout)
        return self
