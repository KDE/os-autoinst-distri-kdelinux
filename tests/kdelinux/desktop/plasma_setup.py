# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import array
import os
import subprocess
import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from lib.sut import openqa_junit_xml
from lib.sut.openqa_autoinst import OpenQAAutoinst
from lib.sut.atspi import find_pid_on_atspi_bus
from lib.common import user_manager

# Walks through the Plasma Setup wizard to set up the SUT.
# Fatal test - it's necessary for the system to work in later testing.


class PlasmaSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability("app", str(find_pid_on_atspi_bus('plasma-setup')))
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=options)
        self.driver.implicitly_wait(0)
        self.wait = WebDriverWait(self.driver, 10)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def _next_page(self, current_page_title, next_page_title):
        # Ensure we reliably start from the page we expect.
        self.wait.until(
            ec.presence_of_element_located(
                (AppiumBy.NAME, current_page_title)
            )
        )

        def reached_next_page(driver):
            # A prior click was accepted once the heading changes.
            try:
                if driver.find_elements(AppiumBy.NAME, next_page_title):
                    return True
            except WebDriverException as error:
                # Catch this transient backend error and ignore it.
                if "'NoneType' object is not iterable" in error.msg:
                    return False
                raise

            driver.find_element(AppiumBy.NAME, "Next").click()
            return False

        self.wait.until(reached_next_page)

    def _toggle_screen_reader(self):
        self.assertEqual(OpenQAAutoinst().call_testapi('send_key', 'super-alt-s'), 'pass',
                         'openQA failed to send the screen reader shortcut')

    def _orca_running(self, _driver=None):
        return subprocess.run(
            ['pgrep', '-u', str(os.getuid()), '-x', 'orca'],
            stdout=subprocess.DEVNULL, check=False,
        ).returncode == 0

    def test_1_screen_reader(self):
        """The screen reader works, and Orca makes audible output sound."""
        recorder = subprocess.Popen([
            'pw-record', '--raw', '--format=s16', '--rate=16000', '--channels=1',
            '--sample-count=80000', '--properties={"stream.capture.sink": true}', '-',
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self._toggle_screen_reader()
            self.wait.until(self._orca_running, 'The shortcut did not start Orca')
            audio, error = recorder.communicate(timeout=10)
            # pw-record exits 1 even when it actually works!
            self.assertEqual(len(audio), 80000 * 2,
                             f'Recording incomplete with PipeWire, exit code {recorder.returncode}: {error.decode(errors="replace")}')
            samples = array.array('h', audio)
            audible_samples = sum(abs(amplitude) > 100 for amplitude in samples)
            # Output should contain at least 100 ms above -50 dB
            self.assertGreaterEqual(audible_samples, 1600,
                                    'Orca started but there was no captured sound')
        finally:
            if recorder.poll() is None:
                recorder.kill()
            recorder.communicate()
            if self._orca_running():
                self._toggle_screen_reader()
                self.wait.until_not(self._orca_running, 'Orca did not stop')

    def test_2_setup(self):
        """Go through and set up the system through Plasma Setup."""
        # Welcome page
        setup_button = self.driver.find_element(AppiumBy.NAME, 'Begin Setup')
        setup_button.click()

        # Language page
        self._next_page("Language", "Keyboard Layout")

        # Keyboard layout page
        self._next_page("Keyboard Layout", "Before we get started…")

        # Dark mode page
        self._next_page("Before we get started…", "About You")

        # User account page
        form = self.driver.find_element(AppiumBy.CLASS_NAME, '[form | ]')

        form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[0].send_keys('Testy McTestface')
        # clear out auto-generated username testymctestface
        form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[1].clear()
        form.find_elements(AppiumBy.CLASS_NAME, '[text | ]')[1].send_keys(user_manager.installed().name)
        form.find_elements(AppiumBy.CLASS_NAME, '[password text | ]')[0].send_keys(user_manager.installed().pw)
        form.find_elements(AppiumBy.CLASS_NAME, '[password text | ]')[1].send_keys(user_manager.installed().pw)

        self._next_page("About You", "Hostname")

        # Hostname page
        self._next_page("Hostname", "Time and Date")

        # Timezone page
        # Timezone is pre-set because the TZ page is very flaky and hard to code around. Just skip it.
        self._next_page("Time and Date", "Completed!")

        # Finished page
        finish_button = self.wait.until(
            ec.element_to_be_clickable((AppiumBy.NAME, "Finish"))
        )
        finish_button.click()


if __name__ == "__main__":
    openqa_junit_xml.run(PlasmaSetupTests, "plasma_setup")
