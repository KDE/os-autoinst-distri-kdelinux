# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
import unittest
import xmlrunner
import os
import sys

RESULTS_DIR = '/var/log/kde-linux-openqa'

def run(test_class: type, name: str):
    """Run a unittest class and write JUnit XML to the expected results dir"""
    output_dir  = f'{RESULTS_DIR}/{name}'
    output_path = f'{output_dir}/junit.xml'
    os.makedirs(output_dir, exist_ok=True)
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    with open(output_path, 'wb') as f:
        runner = xmlrunner.XMLTestRunner(output=f, verbosity=2)
        result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
