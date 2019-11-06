#!/usr/local/bin python 
"""
A simple selenium test example written by python
"""

import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class TestTemplate(unittest.TestCase):
    """Include test cases on a given url"""

    def setUp(self):
        """Start web driver"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def tearDown(self):
        """Stop web driver"""
        self.driver.quit()

    def test_case_1(self):
        """Load Page"""
        try:
            web_path = os.getenv("web_path")
            try:
                self.driver.get(web_path)
                self.driver.find_element_by_class_name('title')
            except NoSuchElementException as ex:
                self.fail(ex.msg)
        except:
            print("environment variable missing: web_path")
        


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTemplate)
    unittest.TextTestRunner(verbosity=2).run(suite)
