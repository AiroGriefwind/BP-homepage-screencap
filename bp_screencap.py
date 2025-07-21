from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import os
import time
import pytz
# --- Imports for Google Drive OAuth 2.0 ---
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def upload_to_gdrive(filename, folder_id):
    """Uploads a file to a specific Google Drive folder using OAuth 2.0."""
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    creds = None
    
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use client_secrets.json for the first-time authorization
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
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
