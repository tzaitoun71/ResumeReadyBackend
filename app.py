from flask import Flask
from routes import setup_routes
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

setup_routes(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)