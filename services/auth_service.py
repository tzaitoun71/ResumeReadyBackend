from flask import request, jsonify
from functools import wraps
from jose import jwt
import requests
import os

# Load environment variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]

def get_auth0_public_keys():
    """Fetch Auth0 public keys"""
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    return jwks

# Verify JWT token from frontend
def verify_jwt(token):
    try:
        header = jwt.get_unverified_header(token)
        jwks = get_auth0_public_keys()
        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if not rsa_key:
            raise Exception("Invalid JWT key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload
    except Exception as e:
        print(f"JWT verification error: {e}")
        return None

# Decorator to enforce authentication
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Missing Authorization Header"}), 401

        user = verify_jwt(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(user, *args, **kwargs)  # Pass user data to route
    return decorated_function
