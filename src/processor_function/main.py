import functions_framework
from base64 import b64decode
from google.cloud.firestore import Client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials, credentials
from google.auth import default
from googleapiclient.discovery import build
import os
from datetime import datetime
import json

SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

# Create singleton db client
# This is done for performance reasons > reinstantiating the client is expensive
db_client = None
def get_db_client():
    global db_client
    if db_client is None:
        credentials, project_id = default()
        db_client = Client(credentials=credentials, project=project_id)
    return db_client

def get_creds(token): # Authenticate against Google APIs
    token_info = json.loads(token)
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
    event_data = json.loads(
        b64decode(base64_data).decode('utf-8')
    )
    print(f"Received event: {event_data}")

    # Initializing db client...
    print("Connecting to firestore...")
    db = get_db_client()
    print("Fetching document...")
    doc_ref = db.collection(u'email_address_info').document(event_data['emailAddress'])
    doc = doc_ref.get().to_dict()

    # Updating creds
    creds = get_creds(doc['token'])
    doc_ref.set({'token': creds.to_json()}, merge = True)
    # Update historyId
    doc_ref.set({'historyId': event_data['historyId']}, merge = True)

    # Initialize the Gmail API
    print("Initializing Gmail Client...")
    gmail = build('gmail', 'v1', credentials=creds)
    # List the messages since the last historyId
    print("Getting list of messages...")
    page_counter = 1
    messages = []
    print(f"Fetching page {page_counter}...")
    response = gmail.users().messages().list(
        userId = event_data['emailAddress'],
        q = f'after:{doc["historyId"]}'
    ).execute() 
    messages.extend(response['messages'])
    page_counter += 1

    # pagination, if necessary (probalby not, most of the times)
    while 'nextPageToken' in response:
        print(f"Fetching page {page_counter}...")
        page_token = response['nextPageToken']
        response = gmail.users().messages().list(
            userId = event_data['emailAddress'],
            q = f'after:{doc["historyId"]}',
            pageToken = page_token
        ).execute()
        messages.extend(response['messages'])
        page_counter += 1

    # Get the messages by id 
    print('Fetching messges')
    for message in messages:
        print(f"message id: {message['id']}")
        response = gmai.users().messages().get(
                userId = event_data['email_address'],
                id = message['id']
        ).execute()
        print(response)
    
    # Print new messages. Enough work for today
    for message in messages:
        print(message)
    

    return "Hello world"
