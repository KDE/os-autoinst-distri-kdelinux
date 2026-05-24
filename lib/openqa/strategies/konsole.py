# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
from lib.sessions.app.konsole import KonsoleSession
from lib.strategies.base import OpenStrategy


class KonsoleOpenStrategy(OpenStrategy):
    def open_app(self, app_name, **kwargs):
        (
            KonsoleSession
                .ensure_active(open_strategy='krunner', **kwargs)
                .type_and_submit(app_name)
        )