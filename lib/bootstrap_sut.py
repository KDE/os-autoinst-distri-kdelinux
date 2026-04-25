# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib import serial_test
from lib import user_manager

REPO_URL = get_var('TEST_REPO', 'https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git')
BRANCH   = get_var('TEST_BRANCH', 'master')

def bootstrap(user):
    serial_test.session.login(user)
    serial_test.session.run('mkdir -p /tests', user=user_manager.root())
    serial_test.session.run('chmod 777 /tests', user=user_manager.root())
    serial_test.session.run(f'git clone -b {BRANCH} {REPO_URL} /tests')
    serial_test.session.run('/tests/sut/bootstrap.sh')
