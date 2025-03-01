# backend/app/utils/google_auth.py

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes for Google Calendar and Drive APIs
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
]

def authenticate_google_calendar():
    """
    Authenticate the user and return Google Calendar API credentials.
    """
    creds = None
    token_path = "token.json"

    # Load existing credentials from token.json
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def authenticate_google_drive():
    """
    Authenticate the user and return Google Drive API credentials.
    """
    return authenticate_google_calendar()  # Reuse the same credentials