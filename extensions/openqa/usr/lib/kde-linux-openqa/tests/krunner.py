# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import unittest
from appium import webdriver
from appium.options.common.base import AppiumOptions
from lib.sut import openqa_junit_xml
from lib.sut.atspi import find_pid_on_atspi_bus

# Searches for and launches an application through KRunner.


class KRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability("app", str(find_pid_on_atspi_bus('krunner')))
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def test_search_and_launch_app(self):
        """Search for an app in KRunner, launch it, and verify it started."""
        # TODO type an app name, verify result appears, press enter, verify app launched
        self.skipTest("not yet implemented")


if __name__ == "__main__":
    openqa_junit_xml.run(KRunnerTests, "krunner")
