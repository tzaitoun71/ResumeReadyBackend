import os
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# MongoDB Setup
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['resume-ready']
user_collections = db['new-users']

# Auth0 Setup
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')


### ✅ Fetch Management API Token ###
def get_management_token():
    """
    Fetch Auth0 Management API Token
    """
    try:
        url = f"https://{AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "audience": f"https://{AUTH0_DOMAIN}/api/v2/"
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        token = response.json().get("access_token")
        print(f"✅ Auth0 Management Token Acquired: {token[:10]}...")  # Debug token (partial)
        return token
    except Exception as e:
        print(f"❌ Error fetching management token: {e}")
        return None



### ✅ Register User ###
def register_user(email: str, password: str, first_name: str, last_name: str):
    try:
        # Fetch Auth0 Management API Token
        token = get_management_token()
        if not token:
            return {"error": "Failed to get management token"}

        # Create User in Auth0
        url = f"https://{AUTH0_DOMAIN}/api/v2/users"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "password": password,
            "connection": "Username-Password-Authentication",
            "user_metadata": {
                "firstName": first_name,
                "lastName": last_name
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code != 201:
            return {"error": response_data.get("message", "Failed to create user in Auth0")}

        auth0_user_id = response_data.get("user_id")
        if not auth0_user_id:
            return {"error": "Failed to retrieve user_id from Auth0"}

        # Save User in MongoDB
        user_data = {
            "_id": auth0_user_id,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "createdAt": datetime.utcnow()
        }
        user_collections.update_one(
            {"_id": auth0_user_id},
            {"$setOnInsert": user_data},
            upsert=True
        )

        return {"message": "User registered successfully"}

    except Exception as e:
        print(f"Error in register_user: {e}")
        return {"error": str(e)}


### ✅ Login User ###
def login_user(email: str, password: str):
    try:
        url = f"https://{AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "audience": AUTH0_AUDIENCE,
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "scope": "openid profile email"
        }

        response = requests.post(url, json=payload)
        response_data = response.json()

        if response.status_code != 200:
            return {"error": response_data.get("error_description", "Login failed")}

        access_token = response_data["access_token"]
        id_token = response_data["id_token"]

        user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info = requests.get(user_info_url, headers=headers).json()

        auth0_user_id = user_info.get("sub")
        user = user_collections.find_one({"_id": auth0_user_id})
        if not user:
            return {"error": "User not found in the database."}

        return {
            "access_token": access_token,
            "id_token": id_token,
            "user": {
                "email": user.get("email"),
                "firstName": user.get("firstName"),
                "lastName": user.get("lastName")
            }
        }

    except Exception as e:
        print(f"Error in login_user: {e}")
        return {"error": str(e)}
