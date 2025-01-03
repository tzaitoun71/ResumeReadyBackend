from flask import Flask, jsonify, redirect, request, session, url_for
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from jwt import PyJWKClient

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
JWKS_URL = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'

app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_DECODE_AUDIENCE'] = AUTH0_AUDIENCE
app.config['JWT_IDENTITY_CLAIM'] = 'sub'

try:
    jwks_client = PyJWKClient(JWKS_URL)
    signing_key = jwks_client.get_signing_key_from_jwt(
        os.getenv('AUTH0_SAMPLE_TOKEN')
    ).key
    app.config['JWT_PUBLIC_KEY'] = signing_key
    print("JWT Public Key Configured Successfully")
except Exception as e:
    print(f"Failed to configure JWT: {e}")
    exit(1)

jwt = JWTManager(app)

from routes import setup_routes
setup_routes(app)

@app.route('/')
def home():
    return "Welcome to the Auth0-Integrated Flask App!"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
