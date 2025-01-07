from datetime import datetime
from config.database import user_collections

def update_user_resume(user_id: str, resume_text: str) -> bool:
    try:
        result = user_collections.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "resume": resume_text,
                    "updatedAt": datetime.utcnow()
                }
            }
        )

        # Check if a document was found and updated
        if result.matched_count == 0:
            print("No document matched the provided user ID.")
            return False

        if result.modified_count == 0:
            print("Document matched, but no changes were made. Possibly identical content.")
            return False

        return True

    except Exception as e:
        print(f"Error updating resume: {e}")
        return False
