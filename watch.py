from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime
import sys
import json

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.metadata'
]

def get_args():
    # Checks if the user has provided a argument
    # This argument must be a json string
    # Must contain the keys "processor_svc_key" and "topic_name"
    # Prints the correct usage if the user has not provided a argument

    try:
        terraform_output = json.loads(sys.argv[1])
        assert("processor_svc_key" in terraform_output)
        assert("topic_name" in terraform_output)
        return terraform_output
    except:
        print('Incorrect argument passed.\nUsage: python watch.py "$(terraform output -json)"')
        sys.exit(1)

def main():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    # Load the terraform output
    terraform_output = get_args()

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(terraform_output["processor_svc_key"], SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        gmail = build('gmail', 'v1', credentials=creds)
        servicerequest = {
          'labelIds': ['INBOX'],
          'topicName': TOPIC_NAME
        }
        watch_response = gmail.users().watch(userId='me', body=request).execute()
        exp_time = datetime.fromtimestamp(watch_response['expiration']//1000)
        print(f"Watch request successfull. Valid until {exp_time}") 

    except HttpError as err:
        print(err)

if __name__ == '__main__':
    main();
