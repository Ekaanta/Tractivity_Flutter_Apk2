from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up options for UiAutomator2
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "Realme RMX3930"
options.app_package = "com.example.tractivity_app"
options.app_activity = "com.example.tractivity_app.MainActivity"
options.new_command_timeout = 3600
options.set_capability("connectHardwareKeyboard", True)

# Set up the Appigitum driver
driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)

try:
    # Wait for the app to load
    sleep(5)
    
    # Find and enter email
    email_field = driver.find_element(AppiumBy.XPATH, '//android.widget.ScrollView/android.widget.EditText[1][@text="bawop41170@cxnlab.com"]')
    email_field.click()
    email_field.send_keys("bawop41170@cxnlab.com")
    
    # Find and enter password
    password_field = driver.find_element(AppiumBy.XPATH, '//android.widget.ScrollView/android.widget.EditText[2][@text="12345678"]')
    password_field.click()
    password_field.send_keys("12345678")
    
    # Check "Remember me" checkbox
   #remember_me = driver.find_element(AppiumBy.XPATH, '//android.widget.CheckBox[@content-desc="Remember me"]')
    #remember_me.click()
    
    # Click Log In button
    login_button = driver.find_element(AppiumBy.XPATH, '//android.view.View[@content-desc="Log in"]="Log In"]')
    login_button.click()
    
    # Wait for login process
    sleep(3)
    
    # Verify login success (you may need to adjust this based on your app's behavior)
    WebDriverWait(driver, 10).until(
        #EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[contains(@content-desc, "success")]'))
    )
    print("Login successful!")
    
except Exception as e:
    print(f"Test failed: {e}")
    
finally:
    # Close the session
    driver.quit()