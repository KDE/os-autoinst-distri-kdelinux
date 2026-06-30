# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Helpers for driving the Plasma panel's system tray.

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def expand(driver, timeout=10):
    """Open the collapsed system tray so its hidden entries become accessible."""
    arrow = WebDriverWait(driver, timeout).until(
        ec.element_to_be_clickable((AppiumBy.NAME, "Show hidden icons")),
        message="system tray expander arrow not found on the panel")
    arrow.click()


def entry(driver, name, timeout=10):
    """Return a clickable system tray entry by name once the tray is open."""
    return WebDriverWait(driver, timeout).until(
        ec.element_to_be_clickable((AppiumBy.NAME, name)),
        message=f"system tray entry {name!r} not found")


def collapse(driver):
    """Close the open system tray popup."""
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
