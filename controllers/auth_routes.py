import os
from flask import Blueprint, redirect, request, jsonify, session
from dotenv import load_dotenv
from services.auth_service import exchange_code_for_tokens, fetch_user_info, save_user_to_db

load_dotenv()

# Environment Variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    """
    Initiates the login process by redirecting the user to Auth0.
    ---
    tags:
      - Auth
    summary: Initiate login
    description: Redirects the user to the Auth0 login page to start the authentication process.
    responses:
      302:
        description: Redirects to Auth0 login page.
    """
    return redirect(
        f'https://{AUTH0_DOMAIN}/authorize'
        f'?response_type=code'
        f'&client_id={AUTH0_CLIENT_ID}'
        f'&redirect_uri={AUTH0_CALLBACK_URL}'
        f'&scope=openid profile email'
        f'&audience={AUTH0_AUDIENCE}'
    )

@auth_bp.route('/callback', methods=['GET'])
def callback():
    """
    Handles the Auth0 callback after user login.
    ---
    tags:
      - Auth
    summary: Handle login callback
    description: Handles the callback from Auth0 after login, exchanges the authorization code for tokens, and retrieves the user's information.
    parameters:
      - in: query
        name: code
        type: string
        required: true
        description: Authorization code returned by Auth0.
    responses:
      200:
        description: Login successful, returns user information and tokens.
        schema:
          type: object
          properties:
            message:
              type: string
            accessToken:
              type: string
            idToken:
              type: string
            user:
              type: object
              properties:
                sub:
                  type: string
                email:
                  type: string
                firstName:
                  type: string
                lastName:
                  type: string
      400:
        description: Authorization code not provided.
      500:
        description: Internal server error.
    """
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({"error": "Authorization code not provided"}), 400

        tokens = exchange_code_for_tokens(code)
        user_info = fetch_user_info(tokens["access_token"])
        save_user_to_db(user_info)

        return jsonify({
            "message": "Login successful",
            "accessToken": tokens.get("access_token"),
            "idToken": tokens.get("id_token"),
            "user": {
                "sub": user_info.get("sub"),
                "email": user_info.get("email"),
                "firstName": user_info.get("given_name", ""),
                "lastName": user_info.get("family_name", "")
            }
        }), 200

    except Exception as e:
        print(f"Error in /callback: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """
    Logs out the user and clears the session.
    ---
    tags:
      - Auth
    summary: Logout
    description: Logs out the user by redirecting them to the Auth0 logout endpoint and clears the session.
    responses:
      302:
        description: Redirects to the Auth0 logout page.
    """
    session.clear()
    return redirect(
        f'https://{AUTH0_DOMAIN}/v2/logout'
        f'?client_id={AUTH0_CLIENT_ID}'
        f'&returnTo={AUTH0_CALLBACK_URL}'
    )
