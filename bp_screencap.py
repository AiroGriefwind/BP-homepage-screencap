from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import os
import time
def capture_full_page_screenshot():
    # Get current timestamp for filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Configure Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Initialize driver
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to the website
        driver.get("https://www.bastillepost.com/hongkong")
        
        # Wait for page to load
        driver.implicitly_wait(10)

        # Sleep for 30 seconds to allow popup ads to disappear
        print("Waiting 30 seconds for popup ads to disappear...")
        time.sleep(30)
        print("Proceeding with screenshot capture...")
        
        # Get full page dimensions
        width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        
        # Set window size to capture full page
        driver.set_window_size(width, height)
        
        # Take screenshot of entire page
        body = driver.find_element(By.TAG_NAME, "body")
        filename = f"bastillepost_screenshot_{timestamp}.png"
        body.screenshot(filename)
        
        print(f"Screenshot saved as: {filename}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_full_page_screenshot()
