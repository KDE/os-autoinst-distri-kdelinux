# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
import unittest
import xmlrunner
import xml.etree.ElementTree as ET
import os
import sys
from pathlib import Path

_RESULTS_DIR = '/var/log/kde-linux-openqa'
_TEST_BASE_DIR = '/extensions/openqa'


def _label(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    for testcase in root.iter("testcase"):
        original_path = testcase.get("file", "")
        if original_path:
            testcase.set(
                "file",
                str(Path(_TEST_BASE_DIR) / original_path.lstrip("/")),
            )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def run(test_class: type, name: str):
    """Run a unittest class and write JUnit XML to the expected results dir"""
    output_dir  = f'{_RESULTS_DIR}/{name}'
    output_path = f'{output_dir}/junit.xml'
    os.makedirs(output_dir, exist_ok=True)
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    with open(output_path, 'wb') as f:
        runner = xmlrunner.XMLTestRunner(output=f, verbosity=2)
        result = runner.run(suite)

    # Set correct file paths for tests
    try:
        with open(output_path, 'rb') as xml:
            labelled_xml = _label(xml.read())
        with open(output_path, 'wb') as xml:
            xml.write(labelled_xml)
    except ET.ParseError as error:
        print(f"skipping {name!r}: {error}")

    sys.exit(0 if result.wasSuccessful() else 1)
