# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import os
import unittest
import subprocess
from lib.sut import openqa_junit_xml

SECRETS_BUS_NAME = 'org.freedesktop.secrets'


class EnsureSecretServiceProviderTests(unittest.TestCase):

    def _activate_secret_service(self):
        # The Secret Service is D-Bus activated, bring it up if it isn't already'
        subprocess.run(['secret-tool', 'lookup', 'kde-linux-openqa', 'probe'],
                       capture_output=True, text=True)

    def _secret_service_pid(self) -> int:
        out = subprocess.check_output(
            ['busctl', '--user', 'status', SECRETS_BUS_NAME], text=True)
        for line in out.splitlines():
            if line.strip().startswith('PID='):
                return int(line.split('=', 1)[1].strip())
        self.fail(f'could not determine PID owning {SECRETS_BUS_NAME}')

    def _process_exe(self, pid: int) -> str:
        return os.path.basename(os.readlink(f'/proc/{pid}/exe'))

    def test_secret_service_provider_is_kwallet(self):
        """Check that the org.freedesktop.secrets provider is KWallet."""
        self._activate_secret_service()
        pid = self._secret_service_pid()
        exe = self._process_exe(pid)
        self.assertEqual(
            exe, 'kwalletd6',
            f'{SECRETS_BUS_NAME} is provided by {exe!r} (pid {pid}), expected kwalletd6'
        )

    # TODO write a GUI keepsecret test so we can see if the wallet actually works
    # and meshes nicely with the keepsecret GUI


if __name__ == "__main__":
    openqa_junit_xml.run(EnsureSecretServiceProviderTests, "ensure_secret_service_provider")
