from datetime import datetime
from models.user_model import User
from config.database import user_collections

# Retrieve a user by ID
def find_user_by_id(user_id: str):
    try:
        return user_collections.find_one({"userId": user_id})
    except Exception as e:
        print(f"Error finding user: {e}")
        return None
    
# Create a new user in the database
def create_user(user_data: User):
    try:
        result = user_collections.insert_one(user_data.to_dict())
        return result.inserted_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

# Update the user's resume in the database
def update_user_resume(user_id: str, resume_text: str) -> bool:
    try:
        result = user_collections.update_one(
            {"userId": user_id},
            {
                "$set": {
                    "resume": resume_text,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating user resume: {e}")
        return False

# Save a user fetched from Auth0 to MongoDB
def save_user(user_info: dict) -> bool:
    try:
        user_id = user_info.get("sub")
        email = user_info.get("email")
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")

        # Check if the user already exists
        if find_user_by_id(user_id):
            print("User already exists in the database.")
            return True  # Return early if user exists

        # Create new user object
        new_user = User(
            userId=user_id,
            email=email,
            firstName=first_name,
            lastName=last_name,
            resume="",
            applications=[]
        )

        # Save user to MongoDB
        result = user_collections.insert_one(new_user.to_dict())
        return result.acknowledged

    except Exception as e:
        print(f"Error saving user to DB: {e}")
        return False