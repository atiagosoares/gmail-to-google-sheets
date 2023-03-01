import functions_framework
from base64 import b64decode
from google.cloud.firestore import Client
import os
from datetime import datetime

# Create singleton db client
# This is done for performance reasons > reinstantiating the client is expensive
db_client = None
def get_db_client():
    global db_client
    if db_client is None:
        db_client = Client()
    return db_client

# Dummy cloud function
@functions_framework.cloud_event
def handler(cloud_event):
    # Print the event data
    base64_data = cloud_event.data['message']['data']
    data = b64decode(base64_data).decode('utf-8')
    now = datetime.now()

    # Store the data in redis
    db = get_db_client()
    doc_ref = db.collection(u'events').document(now.strftime("%Y%m%d%H%M%S"))
    doc_ref.set({
        u'data': data
    })
    
    return "Hello world"