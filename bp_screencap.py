from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import os
import time
import pytz # Import the pytz library

def capture_full_page_screenshot():
    # Define the Hong Kong timezone
    hkt = pytz.timezone('Asia/Hong_Kong')
    
    # Get the current time in HKT
    hkt_now = datetime.now(hkt)
    timestamp = hkt_now.strftime("%Y-%m-%d_%H-%M-%S_HKT") # Added HKT for clarity
    
    # Configure Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Initialize driver
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.bastillepost.com/hongkong")
        driver.implicitly_wait(10)

        print("Waiting 30 seconds for popup ads to disappear...")
        time.sleep(30)
        print("Proceeding with screenshot capture...")
        
        width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        
        driver.set_window_size(width, height)
        
        body = driver.find_element(By.TAG_NAME, "body")
        filename = f"bastillepost_screenshot_{timestamp}.png"
        body.screenshot(filename)
        
        print(f"Screenshot saved as: {filename}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_full_page_screenshot()
