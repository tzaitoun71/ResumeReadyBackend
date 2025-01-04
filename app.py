import os
from flask import Flask, session
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from jwt import PyJWKClient

# Load Environment Variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
JWKS_URL = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'

# JWT Configuration
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_DECODE_AUDIENCE'] = AUTH0_AUDIENCE
app.config['JWT_IDENTITY_CLAIM'] = 'sub'

# Fetch Public Key for JWT Validation
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

# Initialize JWT Manager
jwt = JWTManager(app)

# Import Routes
from routes import setup_routes
setup_routes(app)

# Run Server
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
