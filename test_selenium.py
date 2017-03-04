"""Test Selenium"""

from selenium import webdriver

browser = webdriver.Firefox()
browser.get('http://localhost:5000')

assert browser.title == 'Cinemania'
