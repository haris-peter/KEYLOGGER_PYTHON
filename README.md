# Keylogger with Google Drive Sync

## Overview

This project is a keylogger that captures keyboard inputs and logs them into a file. The log file is automatically synced to Google Drive when changes are detected. The log file is deleted at midnight to start fresh each day.

## Features

- Captures keyboard inputs and logs them into a file.
- Automatically uploads the log file to Google Drive when changes are detected.
- Deletes the log file at midnight.
- Continuously appends a newline to the log file every second.

## Requirements

- Python 3.x
- pynput library
- google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client libraries

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/keylogger-google-drive-sync.git
   cd keylogger-google-drive-sync
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install pynput google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

4. **Set up Google API credentials**:
   - Go to the [Google Cloud Console](https://console.developers.google.com/).
   - Create a new project.
   - Enable the Google Drive API for your project.
   - Create OAuth 2.0 credentials and download the `client_secret_file.json`.
   - Place the `client_secret_file.json` in the root directory of the project.

## Usage

1. **Run the script**:
   ```bash
   python keylogger.py
   ```

2. **Authenticate with Google Drive**:
   - The first time you run the script, you will be prompted to authenticate with your Google account.
   - Follow the instructions to grant the necessary permissions.
   - The credentials will be saved in `token.json` for future use.

## File Structure

```
keylogger-google-drive-sync/
├── client_secret_file.json  # Google API credentials file
├── keylogger.py             # Main script
├── README.md                # This README file
└── token.json               # Token file for Google API (generated after authentication)
```

## Main Script Breakdown

### Imports and Global Variables
- **Imports**: Import necessary libraries.
- **Global Variables**: Define paths for credentials, scopes, and file paths.

### Functions
- **`authenticate_google_drive`**: Authenticates with Google Drive and returns the service object.
- **`delete_existing_file`**: Deletes an existing file on Google Drive to prevent duplicates.
- **`upload_file`**: Uploads the log file to Google Drive.
- **`autosync`**: Automatically syncs the log file to Google Drive when changes are detected.
- **`keyPressed`**: Handles key press events and logs them to the file.
- **`delete_file_at_midnight`**: Deletes the log file at midnight.
- **`create_newline`**: Continuously appends a newline to the log file every second.

### Main Execution
- **Threads**: Start threads for autosync, file deletion at midnight, and newline creation.
- **Keyboard Listener**: Start the keyboard listener to capture key presses.

## Notes

- This script captures keyboard inputs and logs them. Use it responsibly and only on systems where you have explicit permission to do so.
- The keylogging functionality may trigger antivirus warnings due to its nature.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
