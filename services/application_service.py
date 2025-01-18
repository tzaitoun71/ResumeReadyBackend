from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4
from datetime import datetime
from typing import Dict
from models.application_model import Application
from services.cover_letter_service import generate_cover_letter
from services.resume_feedback_service import generate_resume_feedback
from services.interview_questions_service import generate_interview_questions
from repositories.application_repository import (
    delete_application_by_id,
    save_application,
    get_application_by_id,
    get_applications_by_user,
    get_cover_letter_by_app_id,
    get_interview_questions_by_app_id
)

# Process a job application
def process_application(user_id: str, user_resume: str, job_description: str, question_type: str = "Technical", num_questions: int = 3) -> Dict:
    try:
        # Define tasks for concurrent execution
        tasks = {
            "resumeFeedback": (generate_resume_feedback, (user_resume, job_description)),
            "coverLetter": (generate_cover_letter, (user_resume, job_description)),
            "interviewQuestions": (generate_interview_questions, (user_resume, job_description, question_type, num_questions))
        }

        results = {}
        errors = {}

        # Run tasks concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(func, *args): key for key, (func, args) in tasks.items()}

            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    errors[key] = str(e)
                    print(f"Error in task '{key}': {e}")
                    results[key] = {"error": str(e)}

        # Build application object
        application = {
            "id": str(uuid4()),
            "companyName": results.get("resumeFeedback", {}).get("companyName", "Not specified"),
            "position": results.get("resumeFeedback", {}).get("position", "Not specified"),
            "location": results.get("resumeFeedback", {}).get("location", "Not specified"),
            "jobDescription": results.get("resumeFeedback", {}).get("jobDescription", "Not specified"),
            "resumeFeedback": results.get("resumeFeedback", {}),
            "coverLetter": results.get("coverLetter", {}),
            "interviewQuestions": results.get("interviewQuestions", []),
            "status": "Application Submitted" if not errors else "Partial Failure",
            "errors": errors if errors else None,
            "dateCreated": datetime.utcnow().isoformat()
        }

        # Save application to database
        success = save_application_to_user(user_id, application)
        if not success:
            return {"error": "Failed to save application", "status": "Failure", "dateCreated": datetime.utcnow().isoformat()}

        return application

    except Exception as e:
        print(f"Error processing application: {e}")
        return {"error": str(e), "status": "Failure", "dateCreated": datetime.utcnow().isoformat()}


# Retrieve all applications for a user
def get_user_applications(user_id: str):
    return get_applications_by_user(user_id)


# Retrieve details of a specific application
def get_application_details(user_id: str, application_id: str):
    return get_application_by_id(user_id, application_id)


# Retrieve the cover letter for a given application
def get_application_cover_letter(user_id: str, application_id: str):
    return get_cover_letter_by_app_id(user_id, application_id)


# Retrieve interview questions for a given application
def get_application_interview_questions(user_id: str, application_id: str):
    return get_interview_questions_by_app_id(user_id, application_id)

def save_application_to_user(user_id: str, application_data: Application) -> bool:
    return save_application(user_id, application_data)

def delete_application_by_user_id(user_id: str, application_id: str):
    return delete_application_by_id(user_id, application_id)