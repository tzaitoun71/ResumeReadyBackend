from flask import Blueprint, request, jsonify
from models.application_model import Application
from services.application_service import process_application
from services.resume_feedback import generate_resume_feedback
from services.cover_letter import generate_cover_letter
from services.interview_questions import generate_interview_questions
from services.job_summary import summarize_job_description
from services.user import add_application_to_user

application_bp = Blueprint('application', __name__)

# Resume Feedback Route
@application_bp.route('/resume-feedback', methods=['POST'])
def resume_feedback():
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    feedback = generate_resume_feedback(user_resume, job_description)
    return jsonify({"feedback": feedback}), 200

# Cover Letter Route
@application_bp.route('/generate-cover-letter', methods=['POST'])
def cover_letter():
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    cover_letter = generate_cover_letter(user_resume, job_description)
    return jsonify({"cover_letter": cover_letter}), 200

# Interview Questions Route
@application_bp.route('/generate-interview-questions', methods=['POST'])
def interview_questions():
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    questions = generate_interview_questions(user_resume, job_description)
    return jsonify({"questions": questions}), 200

# Process Application Route
@application_bp.route('/process-application', methods=['POST'])
def process_application_endpoint():
    try:
        # Parse request JSON
        data = request.get_json()
        user_id = data.get('userId')
        user_resume = data.get('userResume')
        job_description = data.get('jobDescription')
        question_type = data.get('questionType', 'Technical')
        num_questions = data.get('numQuestions', 3)

        if not user_id or not user_resume or not job_description:
            return jsonify({"error": "Missing required fields"}), 400

        # Process the application
        application_result = process_application(
            user_resume=user_resume,
            job_description=job_description,
            question_type=question_type,
            num_questions=num_questions
        )

        # Add the application to the user's document in MongoDB
        application_data = Application(
            companyName=application_result.get("companyName", "Not specified"),
            position=application_result.get("position", "Not specified"),
            location=application_result.get("location", "Not specified"),
            jobDescription=application_result.get("jobDescription", "Not specified"),
            resumeFeedback=application_result.get("resumeFeedback", {}),
            coverLetter=application_result.get("coverLetter", {}),
            interviewQuestions=application_result.get("interviewQuestions", []),
            status=application_result.get("status", "Application Submitted")
        )

        success = add_application_to_user(user_id, application_data)

        if success:
            return jsonify({"message": "Application processed and saved successfully"}), 200
        else:
            return jsonify({"error": "Failed to save the application to the user document"}), 500

    except Exception as e:
        print(f"Error in /process-application: {e}")
        return jsonify({"error": str(e)}), 500