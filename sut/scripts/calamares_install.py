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
        self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="CalamaresApplication.mainApp.viewManager.viewManagerStack.QStackedWidget.ChoicePage.QComboBox").click()
        options = wait.until(ec.presence_of_all_elements_located((AppiumBy.ACCESSIBILITY_ID, "CalamaresApplication.mainApp.viewManager.viewManagerStack.QStackedWidget.ChoicePage.QComboBox.QComboBoxListView")))
        # Click the last disk in the list view
        options[-1].click() # TODO doesn't work, clicking this does nothing and neither does a myriad of other approaches. can't use actionchains because can't run calamares in nested kwin - it's root. everything past this is untested
        self.driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@name, 'Erase disk')]")
        self.driver.find_element(by=AppiumBy.NAME, value="Install").click()
        ## We will now be at the finished page, but we don't want to restart, just shut down. This is handled in the next OpenQA test.

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(CalamaresTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
