from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

# MongoDB Setup
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['resume-ready']
user_collections = db['new-users']