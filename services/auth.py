import os
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['resume-ready']
user_collections = db['new-users']

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CONNECTION = "Username-Password-Authentication"
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

def register_user(first_name: str, last_name: str, email: str, password: str):
    try:
        url = f"https://{AUTH0_DOMAIN}/dbconnections/signup"
        payload = {
            "client_id": AUTH0_CLIENT_ID,
            "email": email,
            "password": password,
            "connection": AUTH0_CONNECTION,
            "user_metadata": {
                "firstName": first_name,
                "lastName": last_name
            }
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # Save user to MongoDB
            user_data = {
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "createdAt": datetime.utcnow()
            }
            user_collections.insert_one(user_data)
            return {"message": "User registered successfully."}
        else:
            return {"error": response.json().get('message', 'Registration failed')}
    except Exception as e:
        print(f"Error registering user: {e}")
        return {"error": str(e)}