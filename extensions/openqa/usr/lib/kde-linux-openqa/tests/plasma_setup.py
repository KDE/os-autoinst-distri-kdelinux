# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

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
from lib.sut.atspi import find_pid_on_atspi_bus
from lib import user_manager
import sys
import time
import subprocess

# Walks through the Plasma Setup wizard to set up the SUT.
# Fatal test - it's necessary for the system to work in later testing.

class PlasmaSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability("app", str(find_pid_on_atspi_bus('plasma-setup')))
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        pass

    def test_setup(self):
        """Go through and set up the system through Plasma Setup."""
        ## Welcome page
        wait = WebDriverWait(self.driver, 5)
        setup_button = self.driver.find_element(AppiumBy.NAME, 'Begin Setup')
        setup_button.click()

        ## Language page
        search = self.driver.find_element(AppiumBy.NAME, 'Search')
        search.send_keys('American English')
        time.sleep(1) # animations race with our test
        ActionChains(self.driver).move_to_element(self.driver.find_element(AppiumBy.NAME, 'American English (United States)')).click().perform()
        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()

        ## Keyboard layout page
        time.sleep(1)
        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()

        ## Dark mode page
        time.sleep(1)
        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()

        ## User account page
        form = self.driver.find_element(AppiumBy.CLASS_NAME, '[form | ]')

        form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[0].send_keys('Testy McTestface')
        # clear out auto-generated username testymctestface
        form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[1].clear()
        form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[1].send_keys(user_manager.installed().name)
        form.find_elements(AppiumBy.CLASS_NAME, '[password text | ]')[0].send_keys(user_manager.installed().pw)
        form.find_elements(AppiumBy.CLASS_NAME, '[password text | ]')[1].send_keys(user_manager.installed().pw)

        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()

        ## Hostname page
        time.sleep(1)
        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()

        ## Timezone page
        time.sleep(1)
        # Timezone is pre-set because the TZ page is very flakey and hard to code around. Just skip it.
        next_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Next"))
        )
        next_button.click()

        ## Finished page
        time.sleep(2)
        finish_button = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Finish"))
        )
        finish_button.click()


if __name__ == "__main__":
    openqa_junit_xml.run(PlasmaSetupTests, "plasma_setup")
