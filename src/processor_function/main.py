import functions_framework
from base64 import b64decode
from google.cloud.firestore import Client
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
    credentials, project_id = default()
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