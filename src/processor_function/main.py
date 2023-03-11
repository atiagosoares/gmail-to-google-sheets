import functions_framework
from base64 import b64decode
from google.cloud.firestore import Client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
from datetime import datetime
import json

SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
TOKEN = os.environ.get('TOKEN')

# Create singleton db client
# This is done for performance reasons > reinstantiating the client is expensive
db_client = None
def get_db_client():
    global db_client
    if db_client is None:
        db_client = Client(credentials=credentials, project=project_id)
    return db_client

def get_creds(): # Authenticate against Google APIs
    token_info = json.loads(TOKEN)
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = Credentials.from_authorized_user_info(token_info, scopes = scopes)
    if creds.expired:
        if not creds.refresh_token:
            raise(Exception("No refresh token"))
        creds.refresh(Request())
    return creds

# Dummy cloud function
@functions_framework.cloud_event
def handler(cloud_event):
    # Print the event data
    base64_data = cloud_event.data['message']['data']
    data = json.loads(
        b64decode(base64_data).decode('utf-8')
    )

    # Store the data in redis
    db = get_db_client()
    doc_ref = db.collection(u'email_address_info').document(data['emailAddress'])
    doc_ref.set({
        'historyId': data['historyId']
    })

    # Initialize the Gmail API
    credentials = get_creds()
    gmail = build('gmail', 'v1', credentials=credentials)
    # List the messages since the last historyId
    message_list = []
    messages = gmail.users().messages().list(
        userId = data['emailAddress'],
        q = f'after:{data["historyId"]}'
    ).execute() 
    messages.extend(messages['messages'])

    # pagination, if necessary (probalby not, most of the times)
    while 'nextPageToken' in messages:
        #TODO: implement exponential backoff
        page_token = messages['nextPageToken']
        messages = gmail.users().messages().list(
            userId = data['emailAddress'],
            q = f'after:{data["historyId"]}',
            pageToken = page_token
        ).execute()
        messages.extend(messages['messages'])
    
    # Print new messages. Enough work for today
    for message in messages:
        print(message)
    

    return "Hello world"
