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
