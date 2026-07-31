# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
from testapi import *
from lib.test import cli_test
from lib.test.cli_session import session
from lib.common import user_manager


def test_flags(self):
    return {'always_run': 1}


def run(self):
    test = cli_test.CliTest('collect_logs', artifacts=['/tmp/kde-linux-collected-logs.tar.zst'], timeout=400)
    # This test is always_run, so installation might have failed while still in
    # the live account or setup account.
    users = (
        user_manager.installed(),
        user_manager.plasma_setup(),
        user_manager.live(),
    )
    user = next(
        candidate
        for candidate in users
        if session.run(f'id -u {candidate.name} || true').strip()
    )
    test.run_selenium(user=user)
