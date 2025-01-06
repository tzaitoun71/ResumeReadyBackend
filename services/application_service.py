from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4
from datetime import datetime
from typing import Dict

# Import the three functions
from services.cover_letter import generate_cover_letter
from services.resume_feedback import generate_resume_feedback
from services.interview_questions import generate_interview_questions


def process_application(user_resume: str, job_description: str, question_type: str = "Technical", num_questions: int = 3) -> Dict:
    """
    Run resume feedback, cover letter, and interview question generation simultaneously.
    Store the results in an 'applications' array.
    """
    try:
        # Define tasks for concurrent execution
        tasks = {
            "resumeFeedback": lambda: generate_resume_feedback(user_resume, job_description),
            "coverLetter": lambda: generate_cover_letter(user_resume, job_description),
            "interviewQuestions": lambda: generate_interview_questions(user_resume, job_description, question_type, num_questions)
        }

        results = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit tasks to the thread pool
            futures = {executor.submit(task): key for key, task in tasks.items()}

            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    results[key] = {"error": str(e)}
                    print(f"Error in task {key}: {e}")

        # Build the application object
        application = {
            "id": str(uuid4()),  # Generate a unique ID for the application
            "companyName": results.get("resumeFeedback", {}).get("companyName", "Not specified"),
            "position": results.get("resumeFeedback", {}).get("position", "Not specified"),
            "location": results.get("resumeFeedback", {}).get("location", "Not specified"),
            "jobDescription": results.get("resumeFeedback", {}).get("jobDescription", "Not specified"),
            "resumeFeedback": results.get("resumeFeedback", {}),
            "coverLetter": results.get("coverLetter", {}),
            "interviewQuestions": results.get("interviewQuestions", []),
            "status": "Application Submitted",
            "dateCreated": datetime.utcnow().isoformat()
        }

        return application

    except Exception as e:
        print(f"Error processing application: {e}")
        return {"error": str(e)}