# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import os
import subprocess
import unittest
from pathlib import Path
from lib.sut import openqa_junit_xml
from lib.sut.polkit import PolkitAgent

# Tests the dev tools shipped in the image, toggle-developer-mode and set-up-system-development.

TOGGLE_DEVELOPER_MODE     = '/usr/bin/toggle-developer-mode'
SET_UP_SYSTEM_DEVELOPMENT = '/usr/bin/set-up-system-development'
OPT_APPS = Path('/opt/local/share/applications')


class SystemDevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # toggle-developer-mode elevates via polkit, so we attach to the agent to answer it.
        self.polkit = PolkitAgent()

    @classmethod
    def tearDownClass(self):
        self.polkit.quit()

    def _dev_mode_enabled(self) -> bool:
        return (OPT_APPS / 'GammaRay.desktop').exists()

    def _toggle(self):
        proc = subprocess.Popen(
            [TOGGLE_DEVELOPER_MODE],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.polkit.answer_prompts(proc)
        try:
            _, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            _, stderr = proc.communicate()
            self.fail(f'{TOGGLE_DEVELOPER_MODE} timed out, was the polkit prompt unanswered?: {stderr.strip()}')
        self.assertEqual(
            proc.returncode, 0,
            f'{TOGGLE_DEVELOPER_MODE} failed: {stderr.strip()}')

    def test_1_developer_mode_script_present(self):
        """The developer mode toggle must be installed and executable."""
        self.assertTrue(
            os.access(TOGGLE_DEVELOPER_MODE, os.X_OK),
            f'{TOGGLE_DEVELOPER_MODE} is missing or not executable')

    def test_2_toggle_developer_mode(self):
        """Toggling must show/hide the bundled developer app launchers."""
        started_enabled = self._dev_mode_enabled()

        # First toggle flips the state.
        self._toggle()
        self.assertEqual(
            self._dev_mode_enabled(), not started_enabled,
            'toggling developer mode did not flip its state')

        if not started_enabled:
            for app in [
                'GammaRay.desktop',
                'org.kde.heaptrack.desktop',
                'org.kde.plasma.lookandfeelexplorer.desktop',
                'org.kde.plasma.themeexplorer.desktop',
                'org.kde.plasmaengineexplorer.desktop',
            ]:
                path = OPT_APPS / app
                self.assertTrue(
                    path.is_file(), f'{path} was not installed by enabling developer mode')
                self.assertNotIn(
                    'NoDisplay=true', path.read_text(),
                    f'{path} is still hidden by NoDisplay=true after enabling')

        # Second toggle leaves the system as we found it.
        self._toggle()
        self.assertEqual(
            self._dev_mode_enabled(), started_enabled,
            'developer mode did not return to its original state')

    def test_3_set_up_system_development(self):
        """Setting up system development must install kde-builder and configure."""
        self.assertTrue(
            os.access(SET_UP_SYSTEM_DEVELOPMENT, os.X_OK),
            f'{SET_UP_SYSTEM_DEVELOPMENT} is missing or not executable')

        # Downloads and installs kde-builder, so it needs network and some time.
        result = subprocess.run(
            [SET_UP_SYSTEM_DEVELOPMENT], capture_output=True, text=True, timeout=300)
        self.assertEqual(
            result.returncode, 0,
            f'{SET_UP_SYSTEM_DEVELOPMENT} failed: {result.stderr.strip()}')
        kde_builder = Path.home() / '.local' / 'bin' / 'kde-builder'
        config = Path.home() / '.config' / 'kde-builder.yaml'
        self.assertTrue(kde_builder.is_file(), f'{kde_builder} was not installed')
        self.assertTrue(config.is_file(), f'{config} was not created')

        # A second run must find everything already in place and do nothing.
        rerun = subprocess.run(
            [SET_UP_SYSTEM_DEVELOPMENT], capture_output=True, text=True, timeout=300)
        self.assertEqual(
            rerun.returncode, 0,
            f'second {SET_UP_SYSTEM_DEVELOPMENT} run failed: {rerun.stderr.strip()}')
        self.assertIn(
            'Nothing to do!', rerun.stdout,
            'set-up-system-development was not idempotent on a second run')


if __name__ == '__main__':
    openqa_junit_xml.run(SystemDevelopmentTests, 'system_development')
