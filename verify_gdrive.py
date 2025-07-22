# verify_gdrive.py
import os
import pytz
import base64
from email.message import EmailMessage
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def check_for_todays_screenshot(folder_id, creds):
    """Checks Google Drive for a screenshot file from today."""
    try:
        service = build('drive', 'v3', credentials=creds)
        
        # Get today's date in Hong Kong time
        hkt = pytz.timezone('Asia/Hong_Kong')
        today_str = datetime.now(hkt).strftime('%Y-%m-%d')
        
        # Search for files created today in the specified folder
        query = f"'{folder_id}' in parents and name contains 'bastillepost_screenshot_{today_str}' and trashed=false"
        
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            pageSize=1
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            print(f"Verification FAILED: No screenshot found for {today_str}.")
            return False, False # File not found
        else:
            print(f"Verification SUCCESS: Found screenshot for today: {items[0]['name']}")
            return True, False # File found

    except Exception as e:
        print(f"An error occurred while checking Google Drive: {e}")
        return False, True # Error occurred, assume file exists

def send_failure_notification(creds):
    """Sends an email alert using the Gmail API."""
    colleague_email = os.getenv('COLLEAGUE_EMAIL')
    sender_email = os.getenv('SENDER_EMAIL') # This should be your own gmail address

    if not all([colleague_email, sender_email]):
        print("Error: Missing COLLEAGUE_EMAIL or SENDER_EMAIL environment variables.")
        return

    try:
        service = build('gmail', 'v1', credentials=creds)
        today_str = datetime.now(pytz.timezone('Asia/Hong_Kong')).strftime('%Y-%m-%d')
        
        message = EmailMessage()
        message.set_content(f"""
        Hello,

        The automated check has failed to find the Bastille Post homepage screenshot for {today_str} in the Google Drive folder.

        Please capture and upload the screenshot manually as soon as possible.

        Thank you,
        Automated Verification System
        """)
        message['To'] = colleague_email
        message['From'] = sender_email
        message['Subject'] = f"URGENT: Bastille Post Screenshot Missing for {today_str}"

        # Encode the message in base64url
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(f"Successfully sent failure notification to {colleague_email}. Message ID: {send_message['id']}")

    except HttpError as error:
        print(f"Failed to send email notification: {error}")
    except Exception as e:
        print(f"An unexpected error occurred during email sending: {e}")

if __name__ == "__main__":
    # Add Gmail scope. drive.readonly is for checking, gmail.send is for alerting.
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/gmail.send']
    creds = None

    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Before refreshing, check if the scopes match. If not, force re-authentication.
            if set(creds.scopes) != set(SCOPES):
                 creds = None # Force re-auth to get new scopes
            else:
                 creds.refresh(Request())
        
        if not creds:
             # IMPORTANT: Delete your old token.json before running this locally
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the new credentials with updated scopes for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    
    if not gdrive_folder_id:
        print("Error: GDRIVE_FOLDER_ID environment variable not set.")
    else:
        file_found, error_occurred = check_for_todays_screenshot(gdrive_folder_id, creds)
        
        if not file_found and not error_occurred:
            send_failure_notification(creds)
