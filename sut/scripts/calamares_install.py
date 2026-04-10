# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
import selenium.common.exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class CalamaresTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability("app", "/usr/local/bin/calamares")
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        # oddly enough doesn't work'
        #self.driver.quit()

    def test_welcome(self):
        wait = WebDriverWait(self.driver, 20)
        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()

    def test_partitioning(self):
        pass

if __name__ == "__main__":
    unittest.main()
