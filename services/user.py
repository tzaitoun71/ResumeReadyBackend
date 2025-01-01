from datetime import datetime
from services.auth import user_collections

def update_user_resume(email: str, resume_text: str) -> bool:
    try:
        result = user_collections.update_one(
            {"email": email},
            {
                "$set": {
                    "resume": resume_text,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating resume: {e}")
        return False