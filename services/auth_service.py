import os
import requests
from services.user_service import register_user, get_user
from models.user_model import User  

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")

def verify_auth0_token(access_token):
    try:
        url = f"https://{AUTH0_DOMAIN}/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None

        return response.json()
    except Exception as e:
        print(f"Error verifying Auth0 token: {e}")
        return None

def validate_and_create_user(access_token):
    user_info = verify_auth0_token(access_token)
    if not user_info:
        return None

    user_id = user_info.get("sub")
    email = user_info.get("email")
    first_name = user_info.get("given_name", "")
    last_name = user_info.get("family_name", "")

    if not user_id or not email:
        return None

    existing_user = get_user(user_id) 
    if not existing_user:
        new_user = User(
            userId=user_id,
            email=email,
            firstName=first_name,
            lastName=last_name,
            resume="",
            applications=[]
        )

        register_user(new_user)  # Save to DB 

    return {
        "userId": user_id,
        "email": email,
        "firstName": first_name,
        "lastName": last_name
    }
