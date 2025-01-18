from repositories.user_repository import (
    find_user_by_id,
    create_user,
    update_user_resume,
)

# Retrieve user details
def get_user(user_id: str):
    return find_user_by_id(user_id)

# Create a new user
def register_user(user_data):
    return create_user(user_data)

# Update user resume
def save_user_resume(user_id: str, resume_text: str) -> bool:
    return update_user_resume(user_id, resume_text)