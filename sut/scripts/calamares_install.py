import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
from selenium.webdriver.support.ui import WebDriverWait

class CalamaresTests(unittest.TestCase):
    pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CalamaresTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

 @classmethod
    def setUpClass(self):
        options = AppiumOptions()
        options.set_capability("app", "/usr/local/bin/calamares")
        self.driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723',
            options=options)
        self.driver.implicitly_wait = 10

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
