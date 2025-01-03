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

        # Check if a document was found and updated
        if result.matched_count == 0:
            print("No document matched the provided email.")
            return False

        if result.modified_count == 0:
            print("Document matched, but no changes were made. Possibly identical content.")
            return False

        return True

    except Exception as e:
        print(f"Error updating resume: {e}")
        return False
