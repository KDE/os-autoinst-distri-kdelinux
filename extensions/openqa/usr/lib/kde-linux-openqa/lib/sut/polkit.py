# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Helper for answering the KDE polkit authentication agent's prompts.

import subprocess
from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import selenium.common.exceptions
from lib.sut.atspi import find_pid_on_atspi_bus
from lib import user_manager


class PolkitAgent:
    """Authenticates through the KDE polkit prompt."""
    def __init__(self):
        self.driver = None

    def _attach(self):
        if self.driver is not None:
            try:
                self.driver.quit()
            except selenium.common.exceptions.WebDriverException:
                pass

        options = AppiumOptions()
        options.set_capability('app', str(find_pid_on_atspi_bus('polkit-kde-authentication-agent-1')))
        options.set_capability('timeouts', {'implicit': 5000})
        self.driver = webdriver.Remote(command_executor='http://127.0.0.1:4723', options=options)

    def quit(self):
        if self.driver is not None:
            self.driver.quit()

    def _set_text(self, text, element=None):
        # QML text fields seem to not implement AT-SPI EditableText in QT versions older than 6.11
        # and synthesised keystrokes get garbled, so we fall back to using the clipboard here.
        # https://qt-project.atlassian.net/browse/QTBUG-142132
        # With no element (e.g. an external dialog not in our a11y tree) paste blind into
        # whatever currently has focus.
        subprocess.run(['wl-copy', text], check=True)
        if element is not None:
            element.click()
            WebDriverWait(self.driver, 10).until(
                lambda _: element.is_selected(), message='field never gained focus')
        ActionChains(self.driver).key_down(Keys.CONTROL).pause(0.5).send_keys('v').pause(0.5).key_up(Keys.CONTROL).perform()

    def authenticate(self, password=None):
        """Wait for a single authentication prompt to appear and answer it."""
        self._attach()
        if password is None:
            password = user_manager.installed().pw
        field = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((AppiumBy.XPATH, '//password_text')))
        self._set_text(password, field)
        field.send_keys(Keys.RETURN)
