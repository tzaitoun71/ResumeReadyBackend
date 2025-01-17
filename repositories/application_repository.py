from config.database import user_collections
from datetime import datetime

# Save application to database
def save_application(user_id, application_data):
    try:
        result = user_collections.update_one(
            {"userId": user_id},
            {
                "$push": {"applications": application_data},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error saving application: {e}")
        return False

# Get all applications for a user
def get_applications_by_user(user_id):
    user = user_collections.find_one({"userId": user_id}, {"applications": 1})
    return user.get("applications", []) if user else []

# Get application details by application ID
def get_application_by_id(user_id, app_id):
    user = user_collections.find_one({"userId": user_id})
    if not user:
        return None
    return next((app for app in user.get("applications", []) if str(app["id"]) == app_id), None)

# Get cover letter for a specific application
def get_cover_letter_by_app_id(user_id, app_id):
    application = get_application_by_id(user_id, app_id)
    return application.get("coverLetter") if application else None

# Get interview questions for a specific application
def get_interview_questions_by_app_id(user_id, app_id):
    application = get_application_by_id(user_id, app_id)
    return application.get("interviewQuestions") if application else None
