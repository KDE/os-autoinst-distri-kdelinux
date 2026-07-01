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
# Fatal test as it's necessary for the system to work in later testing.


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

    def _fill_account(self, form):
        """Fill the account page's form."""
        form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[0].send_keys('Testy McTestface')
        username = form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[1]
        username.clear()
        username.send_keys(user_manager.installed().name)
        for field in form.find_elements(AppiumBy.CLASS_NAME, '[password text | ]'):
            field.send_keys(user_manager.installed().pw)

    def test_setup(self):
        """Go through and set up the system through Plasma Setup."""
        wait = WebDriverWait(self.driver, 60)
        wait.until(ec.element_to_be_clickable((AppiumBy.NAME, "Begin Setup"))).click()

        account_filled = False
        while True:
            # We're on the final page, so finish up.
            finish = self.driver.find_elements(AppiumBy.NAME, "Finish")
            if finish and finish[0].is_displayed():
                wait.until(ec.element_to_be_clickable((AppiumBy.NAME, "Finish"))).click()
                return

            # The account page is the only step that disables Next until we input something into it (for obvious reasons), so fill it out.
            if not account_filled:
                form = self.driver.find_elements(AppiumBy.CLASS_NAME, '[form | ]')
                if form:
                    self._fill_account(form[0])
                    account_filled = True

            # Now just keep spamming next after all these checks to progress quickly.
            wait.until(ec.element_to_be_clickable((AppiumBy.NAME, "Next"))).click()


if __name__ == "__main__":
    openqa_junit_xml.run(PlasmaSetupTests, "plasma_setup")
