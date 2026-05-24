# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from lib.sessions.syscore.krunner import KRunnerSession
from lib.strategies.base import OpenStrategy


class KRunnerOpenStrategy(OpenStrategy):
    def open_app(self, app_name, **kwargs):
        (
            KRunnerSession
                .ensure_active()
                .type_and_submit(app_name, **kwargs)
        )