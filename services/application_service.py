from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4
from datetime import datetime
from typing import Dict
from services.cover_letter import generate_cover_letter
from services.resume_feedback import generate_resume_feedback
from services.interview_questions import generate_interview_questions


def process_application(user_resume: str, job_description: str, question_type: str = "Technical", num_questions: int = 3) -> Dict:
    try:
        # Define tasks for concurrent execution
        tasks = {
            "resumeFeedback": (generate_resume_feedback, (user_resume, job_description)),
            "coverLetter": (generate_cover_letter, (user_resume, job_description)),
            "interviewQuestions": (generate_interview_questions, (user_resume, job_description, question_type, num_questions))
        }

        results = {}
        errors = {}

        # Run tasks concurrently with a ThreadPoolExecutor
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

        # Build the application object
        application = {
            "id": str(uuid4()),  # Generate a unique application ID
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

        return application

    except Exception as e:
        print(f"Error processing application: {e}")
        return {"error": str(e), "status": "Failure", "dateCreated": datetime.utcnow().isoformat()}
