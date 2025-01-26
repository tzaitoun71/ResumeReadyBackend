from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

# Load Environment Variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Enable CORS
CORS(app)

# Register Blueprints
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.application_controller import application_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(application_bp, url_prefix='/application')

# Swagger UI Setup
SWAGGER_URL = ''
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
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
