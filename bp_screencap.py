from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import os
import time
import pytz
# --- New imports for Google Drive ---
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_gdrive(filename, folder_id):
    """Uploads a file to a specific Google Drive folder."""
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        SERVICE_ACCOUNT_FILE = 'credentials.json'

        # Authenticate using the service account file
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': os.path.basename(filename),
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(filename, mimetype='image/png')
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"File '{filename}' uploaded successfully to Google Drive with File ID: {file.get('id')}")

    except FileNotFoundError:
        print(f"Error: The credentials file '{SERVICE_ACCOUNT_FILE}' was not found.")
        print("Ensure the GDRIVE_CREDENTIALS secret is set up correctly in GitHub Actions.")
    except Exception as e:
        print(f"An error occurred during Google Drive upload: {e}")

def capture_full_page_screenshot():
    hkt = pytz.timezone('Asia/Hong_Kong')
    hkt_now = datetime.now(hkt)
    timestamp = hkt_now.strftime("%Y-%m-%d_%H-%M-%S_HKT")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    filename = f"bastillepost_screenshot_{timestamp}.png"

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
        body.screenshot(filename)
        print(f"Screenshot saved as: {filename}")
        
    finally:
        driver.quit()

    # --- Call the upload function ---
    folder_id = os.getenv('GDRIVE_FOLDER_ID')
    if folder_id:
        if os.path.exists(filename):
            print("Attempting to upload screenshot to Google Drive...")
            upload_to_gdrive(filename, folder_id)
        else:
            print(f"Error: Screenshot file '{filename}' not found for upload.")
    else:
        print("GDRIVE_FOLDER_ID environment variable not set. Skipping Google Drive upload.")

if __name__ == "__main__":
    capture_full_page_screenshot()
