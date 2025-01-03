from flask import Flask, session, redirect, url_for
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from jwt import PyJWKClient

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Auth0 and JWT configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
JWKS_URL = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'

app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_DECODE_AUDIENCE'] = AUTH0_AUDIENCE
app.config['JWT_IDENTITY_CLAIM'] = 'sub'

# Fetch JWKS dynamically
try:
    jwks_client = PyJWKClient(JWKS_URL)
    signing_key = jwks_client.get_signing_key_from_jwt(
        os.getenv('AUTH0_SAMPLE_TOKEN')
    ).key
    app.config['JWT_PUBLIC_KEY'] = signing_key
    print("✅ Successfully configured JWT_PUBLIC_KEY from Auth0 JWKS.")
except Exception as e:
    print(f"❌ Failed to configure JWT_PUBLIC_KEY: {e}")
    exit(1)

# Initialize JWT Manager
jwt = JWTManager(app)

# Import and setup routes
from routes import setup_routes
setup_routes(app, jwt)

# Root Route (Sanity Check)
@app.route('/')
def home():
    return "✅ Flask App is Running!"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
