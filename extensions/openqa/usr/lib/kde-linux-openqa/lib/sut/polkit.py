# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Helper for answering the KDE polkit authentication agent's prompts.

import time
from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions
from lib.sut.atspi import find_pid_on_atspi_bus
from lib import user_manager


class PolkitAgent:
    """Authenticates through the KDE polkit prompt."""

    def __init__(self):
        self.driver = None

    def _attach(self):
        if self.driver is not None:
            return
        options = AppiumOptions()
        options.set_capability('app', str(find_pid_on_atspi_bus('polkit-kde-authentication-agent-1')))
        options.set_capability('timeouts', {'implicit': 10000})
        self.driver = webdriver.Remote(command_executor='http://127.0.0.1:4723', options=options)
        self.driver.implicitly_wait(0)

    def quit(self):
        if self.driver is not None:
            self.driver.quit()

    def _prompt_field(self):
        """Return the agent's password field if there is a prompt, otherwise None."""
        fields = self.driver.find_elements(AppiumBy.XPATH, '//password_text')
        return fields[0] if fields else None

    def authenticate(self, password=None, timeout=30):
        """Wait for a single authentication prompt to appear and answer it."""
        self._attach()
        if password is None:
            password = user_manager.installed().pw
        deadline = time.time() + timeout
        while time.time() < deadline:
            field = self._prompt_field()
            if field is not None:
                field.send_keys(password + Keys.RETURN)
                return
            time.sleep(0.5)
        raise TimeoutError('polkit authentication prompt did not appear')

    def answer_prompts(self, proc, password=None, timeout=90):
        """Answer every authentication prompt until it exits."""
        self._attach()
        if password is None:
            password = user_manager.installed().pw
        deadline = time.time() + timeout
        while proc.poll() is None and time.time() < deadline:
            field = self._prompt_field()
            if field is None:
                time.sleep(0.5)
                continue
            try:
                field.send_keys(password + Keys.RETURN)
            except selenium.common.exceptions.WebDriverException:
                continue  # the prompt vanished as we typed, check again
            # Wait for this prompt to close so we don't answer the same one twice.
            gone = time.time() + 15
            while time.time() < gone and self._prompt_field() is not None:
                time.sleep(0.5)
