# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
class OpenStrategy:
    def open_app(self, app_name):
        raise NotImplementedError('Session Class need to implement at least one open strategy.')
