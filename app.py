import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

# Load Environment Variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Enable CORS
CORS(app)

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
JWKS_URL = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'

# JWT Configuration
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_DECODE_AUDIENCE'] = AUTH0_AUDIENCE
app.config['JWT_IDENTITY_CLAIM'] = 'sub'

# Initialize JWT Manager
jwt = JWTManager(app)

# Register Blueprints
from controllers.auth_routes import auth_bp
from controllers.user_routes import user_bp
from controllers.application_routes import application_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(application_bp, url_prefix='/application')

# Swagger UI Setup
SWAGGER_URL = '/docs'  
API_URL = '/spec'  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, 
    API_URL,  
    config={'app_name': "Resume Ready API"}  
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Swagger JSON Endpoint
@app.route('/spec')
def spec():
    from flask_swagger import swagger
    spec = swagger(app)
    spec['info']['title'] = "Resume Ready API"
    spec['info']['description'] = "API for Resume Ready application"
    spec['info']['version'] = "1.0"
    spec['securityDefinitions'] = {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter 'Bearer <your_access_token>'"
        }
    }
    return jsonify(spec)

# Start Flask Server
if __name__ == '__main__':
    app.run(debug=True)
