import functions_framework
from base64 import b64decode
# Dummy cloud function
@functions_framework.cloud_event
def handler(cloud_event):
    # Print the event data
    base64_data = cloud_event.data['message']['data']
    data = b64decode(base64_data).decode('utf-8')
    print(f"Received message: {data}")
    return "Hello world"