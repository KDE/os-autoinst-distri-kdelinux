# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Philip Grant <pg_kde_invent@runbox.com>

import unittest
from pathlib import Path

from lib.sut import openqa_junit_xml

# Paths of the files which were modified/deleted in the preupgrade test
TEST_MODIFIED_FILE = 'papersize'
TEST_DELETED_FILE = 'paperspecs'

TEST_CONTENT = '# QA testing for etc_factory'

ETC = Path('/etc')


class EtcFactoryPostUpgradeTests(unittest.TestCase):
    def test_01_etc_factory_ignores_user_modified_file(self) -> None:
        # Verify that the test file kept the modification made to it in etc_factory_preupgrade.py
        with open(ETC / TEST_MODIFIED_FILE) as f:
            etc_content = f.read()
        self.assertEqual(etc_content, TEST_CONTENT)

    def test_02_etc_factory_ignores_user_deleted_file(self) -> None:
        # Verify that the file deleted in etc_factory_preupgrade.py stayed deleted
        self.assertFalse((ETC / TEST_DELETED_FILE).exists())


if __name__ == '__main__':
    openqa_junit_xml.run(EtcFactoryPostUpgradeTests, 'etc_factory_preupgrade')