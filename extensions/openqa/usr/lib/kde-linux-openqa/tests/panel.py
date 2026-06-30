# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from lib.sut import openqa_junit_xml
from lib.sut import flatpak
from lib.sut import systemtray
from lib.sut.atspi import find_pid_on_atspi_bus

# Checks if apps can be launched from Kickoff search, Kickoff favorites, and the task manager.
# Checks if the correct apps are pinned to task manager.
# Ensures that the system tray works and displays entries.

FIREFOX_APP_ID = 'org.mozilla.firefox'


class PanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability('app', str(find_pid_on_atspi_bus('plasmashell')))
        self.driver = webdriver.Remote(command_executor='http://127.0.0.1:4723', options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        flatpak.kill(FIREFOX_APP_ID)

    def setUp(self):
        # Close any Firefox we launch at the end of each test. Otherwise a lingering
        # Firefox steals focus and dismisses the next test's kickoff popup.
        self.addCleanup(flatpak.kill, FIREFOX_APP_ID)

    def _panel_child(self, name):
        """Locator for a named element under the panel."""
        return (AppiumBy.XPATH,
                f'//*[@accessibility-id="QApplication.PanelView"]//*[@name="{name}"]')

    def _favorites_entry(self, name):
        """Locator for a favorites entry."""
        return (AppiumBy.XPATH,
                f'//filler/table_cell[@name="{name}"]')

    def _assert_firefox_launched(self):
        try:
            find_pid_on_atspi_bus('Firefox', timeout=30)
        except RuntimeError as error:
            self.fail(f'Firefox did not launch: {error}')

    def test_1_system_tray_present(self):
        """The panel must have a system tray, and its arrow must open the tray popup."""
        systemtray.expand(self.driver)
        # Vaults should reliably be present in the tray.
        systemtray.entry(self.driver, "Vaults")
        systemtray.collapse(self.driver)

    def test_2_task_manager_pinned_apps(self):
        """The task manager must have the expected apps pinned."""
        expected = ["System Settings", "Discover", "Dolphin", "Firefox"]
        missing = [name for name in expected
                   if not self.driver.find_elements(*self._panel_child(name))]
        self.assertFalse(
            missing, f'apps not pinned to the task manager: {", ".join(missing)}')

    def test_3_launch_firefox_from_kickoff_search(self):
        """Open the application launcher, search for Firefox, launch it from the results."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Application Launcher")),
            message='kickoff launcher button not found on the panel').click()
        search = wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Search")),
            message='kickoff search field not found')
        search.send_keys('Firefox')

        # Launch the Firefox search result.
        wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Firefox")),
            message='Firefox did not appear in the kickoff search results').click()
        self._assert_firefox_launched()

    def test_4_launch_firefox_from_kickoff_favorite(self):
        """Open the application launcher and launch Firefox from its favorites entry."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Application Launcher")),
            message='kickoff launcher button not found on the panel').click()

        # Launch the Firefox favorites entry.
        wait.until(
            ec.element_to_be_clickable(self._favorites_entry("Firefox")),
            message='Firefox favorite not found in kickoff').click()
        self._assert_firefox_launched()

    def test_5_launch_firefox_from_task_manager(self):
        """Launch Firefox from its pinned entry in the task manager."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            ec.element_to_be_clickable(self._panel_child("Firefox")),
            message='Firefox is not pinned to the task manager').click()
        self._assert_firefox_launched()


if __name__ == "__main__":
    openqa_junit_xml.run(PanelTests, "panel")
