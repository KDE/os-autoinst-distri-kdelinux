# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

from testapi import *
from lib.openqa.cli_session import session
from lib import user_manager

def run(self):
    system_build = session.run('source /etc/os-release; echo $IMAGE_VERSION')
    test_build = get_var('BUILD')
    assert system_build.strip() == test_build.strip(), f"Both IMAGE_VERSION={system_build} and BUILD={test_build} do not match, upgrade possibly failed"
