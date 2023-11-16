import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]
ATTEMPTS_ALLOWED = 12


def get_confirmation_code(email_address):
    """
    Reads emails from talentreef.qa@gmail.com
    Matches email address used to create hire
    Returns confirmation code to be used to activate account
    Then marks email as read
    :param: email_address (str) talentreef.qa+{timestamp}@gmail.com
    :return: confirmation code (int)
  """
    def helper(email_to_check, gmail_messages, attempts=0):
        """
        Helper to take messages from inbox and recursively call itself to loop over messages.
        If the email matches the email_to_check, return confirmation code associated with that email
        :param: email_to check: email used to create confirmation code
        :param gmail_messages: unread messages from inbox generated main function
        :param attempts: number of attempts so this function doesn't run forever if no code is received
        :return:
        """
        return_code = None
        for message in gmail_messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email = msg['payload']['headers'][0]['value']
            code = msg['snippet'].split()[-1][:-1]
            if email == email_to_check:
                return_code = code

        if return_code:
            msg = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
            return return_code
        elif attempts == ATTEMPTS_ALLOWED:
            return
        else:
            attempts += 1
            print(f'Could not find code. {ATTEMPTS_ALLOWED - attempts} attempts left')
            time.sleep(60/ATTEMPTS_ALLOWED)
            helper(email_to_check, gmail_messages, attempts)





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
            return helper(email_address, messages)

    except Exception as error:
        print(f'An error occurred: {error}')


if __name__ == "__main__":
    print(get_confirmation_code('talentreef.qa+1@gmail.com'))
