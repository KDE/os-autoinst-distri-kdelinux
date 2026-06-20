# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import os
import unittest
import subprocess
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from lib.sut import openqa_junit_xml
from lib.sut import flatpak

# Launches Firefox and checks page loading, and that the Plasma Integration extension is active.

URL = 'https://linux.kde.org'
EXPECTED_ELEMENT_NAME = 'KDE Linux — Mozilla Firefox'
FIREFOX_APP_ID = 'org.mozilla.firefox'


class FirefoxTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.firefox, pid = flatpak.launch(FIREFOX_APP_ID, 'Firefox', URL)
        options = AppiumOptions()
        options.set_capability("app", str(pid))
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        flatpak.kill(FIREFOX_APP_ID)

    def test_1_navigate_to_kde_linux(self):
        """Open the KDE Linux site in Firefox and ensure the page loads."""
        # The page is loaded enough once we can see the frame named "KDE Linux — Mozilla Firefox".
        WebDriverWait(self.driver, 30).until(
            ec.presence_of_element_located((AppiumBy.NAME, EXPECTED_ELEMENT_NAME)),
            message=f'element named {EXPECTED_ELEMENT_NAME!r} did not load')

    def test_2_plasma_integration_extension_active(self):
        """Check that the Plasma Integration browser extension native host is running."""
        # The Plasma Integration extension is installed and working if its native host runs.
        WebDriverWait(self.driver, 30).until(
            lambda _: subprocess.run(
                ['pgrep', '-u', str(os.getuid()), '-f', '/usr/bin/plasma-browser-integration-host'],
                capture_output=True).returncode == 0,
            message='plasma-browser-integration-host is not running; '
                    'the Plasma Integration extension is missing or disabled')


if __name__ == "__main__":
    openqa_junit_xml.run(FirefoxTests, "firefox")
