# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# TODO needs https://invent.kde.org/sdk/selenium-webdriver-at-spi/-/merge_requests/69

import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
import selenium.common.exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from lib.sut import openqa_junit_xml
import sys

class DisableScreenDimAndScreenOffTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability("app", str(sys.argv[1])) # pid passed in by openqa-selenium-webdriver-at-spi-run
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def test_disable_screen_dim_and_screen_off(self):
        self.driver.find_element(by=AppiumBy.NAME, value="Search").send_keys("Power Management")
        self.driver.find_element(by=AppiumBy.XPATH, value="//list_item[@name='Power Management' and not(contains(@states, 'focused'))]")
        ActionChains(self.driver).send_keys(Keys.DOWN).perform()
        self.driver.find_element(by=AppiumBy.XPATH, value="//list_item[@name='Power Management' and contains(@states, 'focused')]")
        ActionChains(self.driver).send_keys(Keys.RETURN).perform()
        # These offsets are a code smell and don't work properly. TODO
        # Maybe https://invent.kde.org/sdk/selenium-webdriver-at-spi/-/merge_requests/69 will help
        ActionChains(self.driver).move_to_element_with_offset(self.driver.find_element(by=AppiumBy.NAME, value="Action to perform when the system is idle"), 100, 100).click().perform()
        ActionChains(self.driver).move_to_element_with_offset(self.driver.find_element(by=AppiumBy.NAME, value="Do nothing"), 100, 100).click().perform()
        ActionChains(self.driver).move_to_element_with_offset(self.driver.find_element(by=AppiumBy.NAME, value="Dim automatically:"), 250, 100).click().perform() # 250 offset on X should get us onto the combobox reliably
        ActionChains(self.driver).move_to_element_with_offset(self.driver.find_element(by=AppiumBy.NAME, value="Never"), 100, 100).click().perform()
        ActionChains(self.driver).move_to_element_with_offset(self.driver.find_element(by=AppiumBy.NAME, value="Apply"), 100, 100).click().perform()

if __name__ == "__main__":
     openqa_junit_xml.run(DisableScreenDimAndScreenOffTests, "disable_screen_dim_and_screen_off")
