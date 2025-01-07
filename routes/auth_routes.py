import os
from flask import Blueprint, redirect, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth import exchange_code_for_tokens, fetch_user_info, save_user_to_db
from dotenv import load_dotenv

load_dotenv()

# Environment Variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

auth_bp = Blueprint('auth', __name__)

# Login Route
@auth_bp.route('/login')
def login():
    return redirect(
        f'https://{AUTH0_DOMAIN}/authorize'
        f'?response_type=code'
        f'&client_id={AUTH0_CLIENT_ID}'
        f'&redirect_uri={AUTH0_CALLBACK_URL}'
        f'&scope=openid profile email'
        f'&audience={AUTH0_AUDIENCE}'
    )


# Callback Route
@auth_bp.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({"error": "Authorization code not provided"}), 400

        tokens = exchange_code_for_tokens(code)
        user_info = fetch_user_info(tokens["access_token"])
        save_user_to_db(user_info)

        session['user'] = {
            "sub": user_info.get("sub"),
            "email": user_info.get("email"),
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", "")
        }
        session['tokens'] = {
            "access_token": tokens.get("access_token"),
            "id_token": tokens.get("id_token")
        }

        return jsonify({"message": "User logged in successfully"}), 200

    except Exception as e:
        print(f"Error in /callback: {e}")
        return jsonify({"error": str(e)}), 500

# Logout Route
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{AUTH0_DOMAIN}/v2/logout'
        f'?client_id={AUTH0_CLIENT_ID}'
        f'&returnTo={AUTH0_CALLBACK_URL}'
    )

# Protected Route
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Temporary Token Route
@auth_bp.route('/tokens', methods=['GET'])
def get_tokens():
    if 'user' not in session:
        return jsonify({"error": "User not logged in"}), 401

    tokens = session.get('tokens')
    return jsonify({
        "access_token": tokens.get("access_token"),
        "id_token": tokens.get("id_token")
    })
