# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *

class SerialTest:
    script = None
    timeout = 120

    def run(self):
        assert_script_run(
            f'~/tests/venv/bin/python scripts/{self.script}',
            timeout=self.timeout
        )

    def test_flags(self):
        return {'fatal': 1}

    def post_fail_hook(self):
        upload_logs('/tmp/test_output.log')
