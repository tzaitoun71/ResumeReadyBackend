from repositories.user_repository import (
    find_user_by_id,
    create_user,
    update_user_resume,
)
from models.application_model import Application

# Retrieve user details
def get_user(user_id: str):
    return find_user_by_id(user_id)

# Create a new user
def register_user(user_data):
    return create_user(user_data)

# Update user resume
def save_user_resume(user_id: str, resume_text: str) -> bool:
    return update_user_resume(user_id, resume_text)

# Add job application to user's list
def save_application(user_id: str, application_data: Application) -> bool:
    return add_application_to_user(user_id, application_data)