from datetime import timedelta
from flask_jwt_extended import create_access_token
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

# Connect to MongoDB Atlas
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

# Access the database and collection
db = client['resume-ready']
user_collections = db['new-users']

def register_user(first_name: str, last_name: str, email: str, password: str):
    if user_collections.find_one({"email": email}):
        return {"error": "User already exists with this email."}
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "password": hashed_password.decode('utf-8')
    }

    user_collections.insert_one(user)
    return {"message": "User registered successfully."}

def login_user(email: str, password: str):
    user = user_collections.find_one({"email": email})

    if not user:
        return {"error": "User not found."}
    
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return {"error": "Invalid password."}

    # Generate a JWT Token
    access_token = create_access_token(identity=email, expires_delta=timedelta(hours=1))

    return {
        "message": "Login successful.",
        "access_token": access_token
    }