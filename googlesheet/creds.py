from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import os


SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets']


def get_creds():
    """
    Gets credentials from google using google Oauth.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('./googlesheet/creds/token.json'):
        creds = Credentials.from_authorized_user_file('./googlesheet/creds/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './googlesheet/creds/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./googlesheet/creds/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds



