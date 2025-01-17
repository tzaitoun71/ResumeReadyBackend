from config.database import user_collections

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

# Get Cover Letter for a specific application
def get_cover_letter_by_app_id(user_id, app_id):
    application = get_application_by_id(user_id, app_id)
    return application.get("coverLetter") if application else None

# Get Interview Questions for a specific application
def get_interview_questions_by_app_id(user_id, app_id):
    application = get_application_by_id(user_id, app_id)
    return application.get("interviewQuestions") if application else None
