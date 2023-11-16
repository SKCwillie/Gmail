import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
ATTEMPTS_ALLOWED = 10


def get_confirmation_code(email_address):
    """
    Reads emails from talentreef.qa@gmail.com
    Matches email address used to create hire
    Returns confirmation code to be used to activate account
    :param: email_address (str) talentreef.qa+{timestamp}@gmail.com
    :return: confirmation code (int)
  """

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', []);

        if not messages:
            print('No new messages.')
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email = msg['payload']['headers'][0]['value']
                code = msg['snippet'].split()[-1][:-1]
                if email == email_address:
                    return code


                # msg = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

    except Exception as error:
        print(f'An error occurred: {error}')


if __name__ == "__main__":
    print(get_confirmation_code('talentreef.qa+1@gmail.com'))
