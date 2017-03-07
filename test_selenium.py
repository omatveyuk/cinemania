import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
 
class CheckTitle(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome('/Users/matveyukoxana/Downloads/chromedriver')
    
    def check_title(self):
        driver = self.driver    
        driver.get('http://localhost:5000')
        print ("Title of the page is : ", driver.title)
        assert driver.title == 'Cinemania'

    def tearDown(self):
        self.driver.close()
        # driver.quit() 

class CheckLogin(unittest.TestCase):
 
    def setUp(self):
        self.driver = webdriver.Chrome('/Users/matveyukoxana/Downloads/chromedriver')
 
    def check_login(self):
        driver = self.driver
        driver.get('http://localhost:5000')
 
        #get the window handles using window_handles( ) method
        window_before = driver.window_handles[0]
        driver.find_element_by_id('login-cinemania').click()
        assert ("Password" in driver.page_source) == True
       
        #get the window handle after a new window has opened
        window_after = driver.window_handles[1]
 
        #switch on to new child window
        driver.switch_to.window(window_after)

        email = driver.find_element_by_id('e-mail')
        if email.is_displayed():
            print ("Element found")
        else:
            print ("Element not found")
        #email.click()

        #email.send_keys("Fred@Fred.com")

        #password.click()
        #password.send_keys("Fred25")

        #submit = driver.find_element_by_id('login-submit')
        #submit.click()
        #assert("Login successful" in driver.page_source) == True
 
           #assert that main window and child window title don't match
           # self.assertNotEqual(str1,str2)
           # print('This window has a different title')
 
           #switch back to original window
           # driver.switch_to.window(window_before)
 
           #assert that the title now match
           # self.assertEqual(str1,driver.title)
           # print('Returned to parent window. Title now match')
      
    def tearDown(self):
        self.driver.close()
 
if __name__ == "__main__":
    unittest.main()
