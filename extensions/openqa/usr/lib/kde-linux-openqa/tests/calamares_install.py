# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
import selenium.common.exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from lib.sut import openqa_junit_xml
import sys

class CalamaresTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability("app", "/opt/local/bin/calamares")
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        #self.driver.quit()
        # fails because calamares is root? TODO
        pass

    def test_install(self):
        ## Welcome page
        wait = WebDriverWait(self.driver, 20)
        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()
        ## Partitions page
        self.driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@name, 'Erase disk')]").click()
        next_button.click()
        ## Finished page
        wait = WebDriverWait(self.driver, 300)
        wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Done"))
        )

if __name__ == "__main__":
     openqa_junit_xml.run(CalamaresTests, "calamares_install")
