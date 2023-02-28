import functions_framework
from base64 import b64decode
import redis
import os
from datetime import datetime

# Create sigleton redis client
redis_client = None
def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(host=os.environ['REDISHOST'], port=os.environ['REDISPORT'])
    return redis_client

# Dummy cloud function
@functions_framework.cloud_event
def handler(cloud_event):
    # Print the event data
    base64_data = cloud_event.data['message']['data']
    data = b64decode(base64_data).decode('utf-8')
    now = datetime.now()

    # Store the data in redis
    redis_client = get_redis_client()
    redis_client.set(now, data)
    
    return "Hello world"