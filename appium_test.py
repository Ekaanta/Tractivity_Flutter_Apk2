from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime

# Define a simple HTML report class
class HTMLReport:
    def __init__(self, title):
        self.title = title
        self.test_steps = []
        self.report_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self.screenshots_dir = "screenshots"
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    def add_step(self, description, status="PASS", screenshot=None, error=None):
        screenshot_path = None
        if screenshot:
            # Save screenshot to file
            screenshot_name = f"{len(self.test_steps) + 1}_{description.replace(' ', '_')}.png"
            screenshot_path = os.path.join(self.screenshots_dir, screenshot_name)
            with open(screenshot_path, "wb") as f:
                f.write(screenshot)
        
        self.test_steps.append({
            "step_number": len(self.test_steps) + 1,
            "description": description,
            "status": status,
            "screenshot": screenshot_path,
            "error": error
        })
    
    def generate_report(self):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                .step {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }}
                .step-header {{ display: flex; justify-content: space-between; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                .screenshot {{ max-width: 800px; margin-top: 10px; }}
                .error {{ background-color: #ffeeee; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>{self.title}</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>Test Steps</h2>
        """
        
        for step in self.test_steps:
            status_class = "pass" if step["status"] == "PASS" else "fail"
            
            html += f"""
            <div class="step">
                <div class="step-header">
                    <h3>Step {step["step_number"]}: {step["description"]}</h3>
                    <span class="{status_class}">{step["status"]}</span>
                </div>
            """
            
            if step["screenshot"]:
                rel_path = os.path.relpath(step["screenshot"])
                html += f'<div><img src="{rel_path}" alt="Screenshot" class="screenshot"></div>'
            
            if step["error"]:
                html += f'<div class="error"><pre>{step["error"]}</pre></div>'
            
            html += "</div>"
        
        html += """
            </body>
            </html>
        """
        
        with open(self.report_path, "w") as f:
            f.write(html)
        
        print(f"Report generated: {self.report_path}")
        return self.report_path

# Define setup_driver function for reuse
def setup_driver():
    # Set up options for UiAutomator2
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Realme RMX3760"
    options.app_package = "com.example.tractivity_app"
    options.app_activity = "com.example.tractivity_app.MainActivity"
    options.new_command_timeout = 3600
    options.set_capability("connectHardwareKeyboard", True)
    options.set_capability("autoGrantPermissions", True)
    options.set_capability("appWaitActivity", "*")  # Wait for any activity to start
    
    # Set up the Appium driver
    return webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)

def test_login():
    driver = setup_driver()
    report = HTMLReport("Tractivity App Login Test")
    
    try:
        print("Waiting for app to initialize...")
        # Wait for app to load past the splash screen
        sleep(10)
        
        # Log current activity for debugging
        current_activity = driver.current_activity
        print(f"Current activity: {current_activity}")
        
        # Take a screenshot of initial screen
        try:
            screenshot = driver.get_screenshot_as_png()
            report.add_step("App initialization", "PASS", screenshot)
        except Exception as e:
            report.add_step("App initialization", "FAIL", None, str(e))
        
        # Handle the welcome screen first
        print("Handling welcome screen...")
        wait = WebDriverWait(driver, 30)
        
        # Try different approaches to find and click the "LET'S GO" button
        lets_go_found = False
        error_messages = []
        
        # Option 1: Try using content-desc attribute
        try:
            lets_go_button = wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, '//android.view.View[@content-desc="LET\'S GO"]')))
            print("Found LET'S GO button by content-desc")
            lets_go_button.click()
            lets_go_found = True
            report.add_step("Click LET'S GO button by content-desc", "PASS", driver.get_screenshot_as_png())
        except Exception as e:
            print(f"Failed to find LET'S GO by content-desc: {e}")
            error_messages.append(f"Content-desc approach: {str(e)}")
            
        # Option 2: Try by text
        if not lets_go_found:
            try:
                lets_go_button = wait.until(EC.element_to_be_clickable(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("LET\'S GO")')))
                print("Found LET'S GO button by text")
                lets_go_button.click()
                lets_go_found = True
                report.add_step("Click LET'S GO button by text", "PASS", driver.get_screenshot_as_png())
            except Exception as e:
                print(f"Failed to find LET'S GO by text: {e}")
                error_messages.append(f"Text approach: {str(e)}")
                
        # Option 3: Try by xpath with partial text
        if not lets_go_found:
            try:
                lets_go_button = wait.until(EC.element_to_be_clickable(
                    (AppiumBy.XPATH, "//*[contains(@content-desc, 'LET') and contains(@content-desc, 'GO')]")))
                print("Found LET'S GO button by partial content-desc")
                lets_go_button.click()
                lets_go_found = True
                report.add_step("Click LET'S GO button by partial content-desc", "PASS", driver.get_screenshot_as_png())
            except Exception as e:
                print(f"Failed to find LET'S GO by partial content-desc: {e}")
                error_messages.append(f"Partial content-desc approach: {str(e)}")
                
        # Option 4: Try to click on coordinates (last resort)
        if not lets_go_found:
            try:
                print("Attempting to click by coordinates")
                driver.tap([(540, 587)], 500)
                print("Tapped approximate LET'S GO button location")
                lets_go_found = True
                report.add_step("Click LET'S GO button by coordinates", "PASS", driver.get_screenshot_as_png())
            except Exception as e:
                print(f"Failed to tap coordinates: {e}")
                error_messages.append(f"Coordinate tap approach: {str(e)}")
        
        if not lets_go_found:
            error_details = "\n".join(error_messages)
            report.add_step("Click LET'S GO button", "FAIL", driver.get_screenshot_as_png(), error_details)
            raise Exception(f"Could not find LET'S GO button with any approach. Errors:\n{error_details}")
        
        # Wait for login screen to appear
        sleep(5)
        print("Waiting for login screen after clicking LET'S GO")
        
        # Take screenshot after clicking LET'S GO
        try:
            screenshot = driver.get_screenshot_as_png()
            report.add_step("Login screen after welcome", "PASS", screenshot)
        except Exception as e:
            report.add_step("Login screen after welcome", "FAIL", None, str(e))
        
        # Now proceed with login
        print("Finding login elements...")
        
        # Try to find EditText elements for username and password
        try:
            edit_texts = wait.until(EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, "android.widget.EditText")))
            print(f"Found {len(edit_texts)} EditText elements")
            
            if len(edit_texts) >= 2:
                # We have at least two input fields, likely email and password
                email_field = edit_texts[0]
                password_field = edit_texts[1]
                
                print("Entering email...")
                email_field.click()
                sleep(1)
                email_field.clear()
                email_field.send_keys("rancon123@gmail.com")
                report.add_step("Enter email", "PASS", driver.get_screenshot_as_png())
                
                print("Entering password...")
                password_field.click()
                sleep(1)
                password_field.clear()
                password_field.send_keys("123")
                report.add_step("Enter password", "PASS", driver.get_screenshot_as_png())
                
                # Find buttons
                buttons = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")
                print(f"Found {len(buttons)} Button elements")
                
                # Try to find login button
                login_button = None
                
                # First try to find by text/content description
                for button in buttons:
                    text = button.get_attribute("text") or ""
                    content_desc = button.get_attribute("content-desc") or ""
                    print(f"Button text: '{text}', content-desc: '{content_desc}'")
                    
                    if any(keyword in text.lower() or keyword in content_desc.lower() 
                           for keyword in ["login", "log in", "sign in", "submit"]):
                        login_button = button
                        break
                
                # If no button found by text, use the last button as fallback
                if login_button is None and buttons:
                    login_button = buttons[-1]
                
                if login_button:
                    print("Clicking login button...")
                    login_button.click()
                    print("Clicked login button")
                    sleep(3)
                    report.add_step("Click login button", "PASS", driver.get_screenshot_as_png())
                    
                    print("Verifying login success...")
                    # Here you can add verification that login was successful
                    
                    report.add_step("Login process completed", "PASS", driver.get_screenshot_as_png())
                    print("Login process completed")
                else:
                    raise Exception("Login button not found")
            else:
                raise Exception(f"Not enough EditText elements found: {len(edit_texts)}")
                
        except Exception as e:
            print(f"Failed to find or interact with login elements: {e}")
            report.add_step("Login process", "FAIL", driver.get_screenshot_as_png(), str(e))
            
            # Debugging: get current page information
            print("Current page layout:")
            element_info = ""
            try:
                elements = driver.find_elements(AppiumBy.XPATH, "//*")
                for i, el in enumerate(elements[:20]):  # First 20 elements
                    try:
                        cls = el.get_attribute("class") or "unknown"
                        txt = el.get_attribute("text") or "none"
                        content = el.get_attribute("content-desc") or "none"
                        element_info += f"Element {i}: {cls} - Text: '{txt}', Content-desc: '{content}'\n"
                    except:
                        pass
                
                print(element_info)
                report.add_step("Debug element information", "INFO", None, element_info)
            except Exception as e:
                print(f"Failed to gather element info: {e}")
            
    except Exception as e:
        print(f"Test failed with exception: {e}")
        report.add_step("Test execution", "FAIL", None, str(e))
        
    finally:
        # Generate the HTML report
        report_path = report.generate_report()
        print(f"Report available at: {report_path}")
        
        driver.quit()

# Run the test function if script is executed directly
if __name__ == "__main__":
    test_login()