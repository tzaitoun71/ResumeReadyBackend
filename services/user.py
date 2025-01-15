from datetime import datetime
from models.user_model import User
from models.application_model import Application
from config.database import user_collections

# Retrieve a user by ID.
def find_user_by_id(user_id: str):
    try:
        return user_collections.find_one({"userId": user_id})
    except Exception as e:
        print(f"Error finding user: {e}")
        return None
    
# Create a new user in the database.
def create_user(user_data: User):
    try:
        result = user_collections.insert_one(user_data.to_dict())
        return result.inserted_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

# Update the user's resume.
from datetime import datetime

# Update the user's resume in the database
def update_user_resume(user_id: str, resume_text: str) -> bool:
    try:
        # Update the user document in MongoDB
        result = user_collections.update_one(
            {"userId": user_id},  # Match the user by userId
            {
                "$set": {
                    "resume": resume_text,  # Update the resumeText field
                    "updatedAt": datetime.utcnow()  # Optionally update the timestamp
                }
            }
        )
        return result.modified_count > 0  # Return True if a document was updated
    except Exception as e:
        print(f"Error updating user resume: {e}")
        return False


# Add an application to a user's applications array
def add_application_to_user(user_id: str, application_data: Application) -> bool:
    try:
        result = user_collections.update_one(
            {"userId": user_id},
            {
                "$push": {
                    "applications": application_data.to_dict()
                },
                "$set": {
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error adding application: {e}")
        return False
