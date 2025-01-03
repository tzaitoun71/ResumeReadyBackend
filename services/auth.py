import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import requests

# Load Environment Variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

# MongoDB Setup
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['resume-ready']
user_collections = db['new-users']

def exchange_code_for_tokens(code: str):
    try:
        token_url = f'https://{AUTH0_DOMAIN}/oauth/token'
        payload = {
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": AUTH0_CALLBACK_URL
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(token_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error exchanging code for tokens: {e}")
        return None

def fetch_user_info(access_token: str):
    try:
        userinfo_url = f'https://{AUTH0_DOMAIN}/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None

def save_user_to_db(user_info: dict):
    try:
        user_data = {
            "_id": user_info.get("sub"),
            "email": user_info.get("email"),
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", ""),
            "created_at": datetime.utcnow()
        }
        user_collections.update_one(
            {"_id": user_data["_id"]},
            {"$setOnInsert": user_data},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving user to MongoDB: {e}")
