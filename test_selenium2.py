"""Test Selenium"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome('/Users/matveyukoxana/Downloads/chromedriver')

def check_title():
    # import pdb; pdb.set_trace()
    driver = webdriver.Chrome('/Users/matveyukoxana/Downloads/chromedriver')
    driver.get('http://localhost:5000')
    print ("Title of the page is : ", driver.title)
    assert driver.title == 'Cinemania'
    driver.close()
    driver.quit()

def check_login():
    driver = webdriver.Chrome('/Users/matveyukoxana/Downloads/chromedriver')
    driver.get('http://localhost:5000')   
    main_window_handle = driver.current_window_handle
    
    login = driver.find_element_by_id('login-cinemania')
    login.click()
    assert ("Password" in driver.page_source) == True

    signin_window_handle = None
    while not signin_window_handle:
        for handle in driver.window_handles:
            if handle != main_window_handle:
                signin_window_handle = handle
        break

    email = driver.find_element_by_id('e-mail')
    if email.is_displayed():
        print ("Element found")
    else:
        print ("Element not found")
    #email.click()

    #email.send_keys("Fred@Fred.com")

    password = driver.find_element_by_id('password')
    password.click()
    password.send_keys("Fred25")

    submit = driver.find_element_by_id('login-submit')
    submit.click()
    assert("Login successful" in driver.page_source) == True

    driver.close()
    driver.quit()


def check_movie_page():
    driver = webdriver.Chrome('/Users/matveyukoxana/Downloads/chromedriver')
    driver.get('http://localhost:5000') 

    start = driver.find_element_by_id('start')
    start.click()

        # browser.implicitly_wait(300)
    #set_script_timeout
    #set_page_load_timeout

# def check_movie_page():
#     driver = webdriver.Chrome('/Users/matveyukoxana/Downloads/chromedriver')
#     driver.get('http://local:host:5000/movies/155')


#browser.find_element_by_id("start").click()
# browser.switch_to_window("")
# 



# RenderedWebElement webElement=findElement(By.id("element_id"));
# webElement.isDisplayed();

# WebDriver driver;

# driver.getCurrentUrl() // will returns the String value


check_title()
check_login()
# check_movie_page()