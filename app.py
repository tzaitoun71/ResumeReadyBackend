import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from jwt import PyJWKClient

# Load Environment Variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# App Configuration
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

# JWT Setup
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

# Register Blueprints
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.application_routes import application_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(application_bp, url_prefix='/application')

# Swagger UI Setup
SWAGGER_URL = '/docs'  
SWAGGER_FILE = '/static/swagger.yaml'  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  
    SWAGGER_FILE,  
    config={
        'app_name': "ResumeReady API" 
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Start Flask Server
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
