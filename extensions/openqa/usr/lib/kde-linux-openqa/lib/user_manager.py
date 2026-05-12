# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from dataclasses import dataclass

@dataclass
class User:
    name: str
    pw: str | None

def live():
    return User(name="live", pw=None)

def installed():
    return User(name="user", pw="user")

def root():
    return User(name="root", pw=None)

def plasma_setup():
    return User(name="plasma-setup", pw=None)
