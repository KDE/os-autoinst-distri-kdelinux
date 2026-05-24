# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from testapi import *
from lib.sessions.syscore.tty import TTYSession
from lib.strategies.base import OpenStrategy


class TTYOpenStrategy(OpenStrategy):
    def open_app(self, app_name, tty_number=3):
        (
            TTYSession
                .ensure_active(tty_number=3)
                .type_and_submit(app_name)
        )