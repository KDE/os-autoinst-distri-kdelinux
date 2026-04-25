import unittest
import xmlrunner
import os
import sys

RESULTS_DIR = '/tests/sut/openqa-junit-results'

def run(test_class: type, name: str):
    """Run a unittest class and write JUnit XML to the expected results dir"""
    output_path = f'{RESULTS_DIR}/{name}-results.xml'
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(output_path, 'wb') as f:
        unittest.main(
            module=test_class.__module__,
            testRunner=xmlrunner.XMLTestRunner(output=f),
            argv=[sys.argv[0]],
            exit=True
        )
