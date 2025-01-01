from flask import Flask
from flask_jwt_extended import JWTManager
from routes import setup_routes
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

jwt_secret_key = os.getenv('JWT_SECRET_KEY')

app.config['JWT_SECRET_KEY'] = jwt_secret_key

jwt = JWTManager(app)

setup_routes(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)