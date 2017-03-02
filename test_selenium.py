    """Test Selenium"""

import unittest
from selenium import webdriver

class CinemaniaSeleniumTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
 
    def test_title(self):
        self.browser.get('http://localhost:5000/')
        self.assertEqual(self.browser.title, 'Cinemania')