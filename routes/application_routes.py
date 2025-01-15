from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.application_model import Application
from services.application_service import process_application
from services.resume_feedback import generate_resume_feedback
from services.cover_letter import generate_cover_letter
from services.interview_questions import generate_interview_questions
from services.user import add_application_to_user

application_bp = Blueprint('application', __name__)

# Resume Feedback Route
@application_bp.route('/resume-feedback', methods=['POST'])
def resume_feedback():
    """
    Generates resume feedback based on the user's resume and the job description.
    ---
    tags:
      - Application
    summary: Generate resume feedback
    description: Generates feedback on the user's resume to match the job description.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            userResume:
              type: string
              description: The content of the user's resume.
            jobDescription:
              type: string
              description: The job description.
    responses:
      200:
        description: Resume feedback generated successfully.
        schema:
          type: object
          properties:
            feedback:
              type: object
      400:
        description: Invalid input data.
    """
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    feedback = generate_resume_feedback(user_resume, job_description)
    return jsonify({"feedback": feedback}), 200

# Cover Letter Route
@application_bp.route('/generate-cover-letter', methods=['POST'])
def cover_letter():
    """
    Generates a cover letter based on the user's resume and the job description.
    ---
    tags:
      - Application
    summary: Generate cover letter
    description: Generates a tailored cover letter for the user.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            userResume:
              type: string
              description: The content of the user's resume.
            jobDescription:
              type: string
              description: The job description.
    responses:
      200:
        description: Cover letter generated successfully.
        schema:
          type: object
          properties:
            cover_letter:
              type: string
      400:
        description: Invalid input data.
    """
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    cover_letter = generate_cover_letter(user_resume, job_description)
    return jsonify({"cover_letter": cover_letter}), 200

# Interview Questions Route
@application_bp.route('/generate-interview-questions', methods=['POST'])
def interview_questions():
    """
    Generates interview questions based on the user's resume and the job description.
    ---
    tags:
      - Application
    summary: Generate interview questions
    description: Generates interview questions relevant to the user's resume and the job description.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            userResume:
              type: string
              description: The content of the user's resume.
            jobDescription:
              type: string
              description: The job description.
    responses:
      200:
        description: Interview questions generated successfully.
        schema:
          type: object
          properties:
            questions:
              type: array
              items:
                type: string
      400:
        description: Invalid input data.
    """
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    questions = generate_interview_questions(user_resume, job_description)
    return jsonify({"questions": questions}), 200

# Process Application Route
@application_bp.route('/process-application', methods=['POST'])
@jwt_required()
def process_application_endpoint():
    """
    Processes the application by generating feedback, a cover letter, and interview questions.
    ---
    tags:
      - Application
    summary: Process application
    description: Processes the user's application and generates feedback, a cover letter, and interview questions.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            userResume:
              type: string
              description: The content of the user's resume.
            jobDescription:
              type: string
              description: The job description.
    responses:
      200:
        description: Application processed successfully.
        schema:
          type: object
          properties:
            message:
              type: string
            application:
              type: object
      401:
        description: Unauthorized access.
      500:
        description: Internal server error.
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "Unauthorized access"}), 401

        data = request.get_json()
        user_resume = data.get('userResume')
        job_description = data.get('jobDescription')
        question_type = data.get('questionType', 'Technical')
        num_questions = data.get('numQuestions', 3)

        if not user_resume or not job_description:
            return jsonify({"error": "Missing required fields: 'userResume', 'jobDescription'"}), 400

        application_result = process_application(
            user_resume=user_resume,
            job_description=job_description,
            question_type=question_type,
            num_questions=num_questions
        )

        if 'error' in application_result:
            return jsonify({"error": "Failed to process application", "details": application_result['error']}), 500

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
            return jsonify({
                "message": "Application processed and saved successfully",
                "application": application_data.to_dict()
            }), 200
        else:
            return jsonify({"error": "Failed to save the application to the user document"}), 500

    except Exception as e:
        print(f"Error in /process-application: {e}")
        return jsonify({"error": str(e)}), 500
