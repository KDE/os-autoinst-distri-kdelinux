# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import unittest
import subprocess
from lib.sut import openqa_junit_xml
from lib.sut import secret_service

# Looks up credentials set in the secret service before reboot.
# These were set in secret_service_persistence_get.py


class SecretServicePersistenceGetTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        secret_service.activate()

    def test_1_secret_service_provider_is_ksecretd(self):
        """Check that the org.freedesktop.secrets provider is ksecretd."""
        exe = secret_service.process_exe()
        self.assertEqual(
            exe,
            "ksecretd",
            f"{secret_service.SECRETS_BUS_NAME} is provided by {exe!r} "
            f"(pid {secret_service.pid()}), expected ksecretd",
        )

    def test_2_persistent_credentials(self):
        """Check that credentials stored before upgrade persisted."""
        result = subprocess.run(
            [
                "secret-tool",
                "lookup",
                "kde-linux-openqa-secret_service_persistence",
                "kde-linux-openqa-secret_service_persistence",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(
            result.stdout.strip(),
            "kde-linux-openqa-secret_service_persistence",
        )


if __name__ == "__main__":
    openqa_junit_xml.run(
        SecretServicePersistenceGetTests,
        "secret_service_persistence_get",
    )
