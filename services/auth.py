import os
from datetime import datetime
import requests
from config.database import user_collections
from models.user_model import User

# Load Environment Variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

# Exchange authorization code for tokens
def exchange_code_for_tokens(code: str):
    try:
        # Auth0 token URL
        token_url = f'https://{AUTH0_DOMAIN}/oauth/token'

        # Payload for the token exchange request
        payload = {
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": AUTH0_CALLBACK_URL
        }

        # Headers for HTTP request
        headers = {'Content-Type': 'application/json'}

        # Sending POST request to Auth0 for token exchange
        response = requests.post(token_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error exchanging code for tokens: {e}")
        return None

# Fetches user info using the access token
def fetch_user_info(access_token: str):
    try:
        userinfo_url = f'https://{AUTH0_DOMAIN}/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}

        # Using the userinfo url and the bearer authentication token, user data is fetched
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None

# Function to save the user to MongoDB
def save_user_to_db(user_info: dict) -> bool:
    try:
        user_id = user_info.get("sub")
        email = user_info.get("email")
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")
        
        # Check if the user already exists
        existing_user = user_collections.find_one({"userId": user_id})
        if existing_user:
            print("User already exists in the database.")
            return True  # Return early if user exists

        # Create a new user object
        new_user = User(
            userId=user_id,
            email=email,
            firstName=first_name,
            lastName=last_name,
            resume="",
            applications=[]
        )
        
        # Save the user to MongoDB
        result = user_collections.insert_one(new_user.to_dict())
        return result.acknowledged

    except Exception as e:
        print(f"Error saving user to DB: {e}")
        return False
