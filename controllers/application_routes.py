from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.application_service import (
    process_application,
    get_user_applications,
    get_application_details,
    get_application_cover_letter,
    get_application_interview_questions,
    delete_application_by_user_id,
)
from services.resume_feedback_service import generate_resume_feedback
from services.cover_letter_service import generate_cover_letter
from services.interview_questions_service import generate_interview_questions

application_bp = Blueprint('application', __name__)

@application_bp.route('/resume-feedback', methods=['POST'])
def resume_feedback():
    """
    Generates resume feedback based on the user's resume and the job description.
    ---
    tags:
      - Application
    summary: Generate resume feedback
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            userResume:
              type: string
            jobDescription:
              type: string
    responses:
      200:
        description: Resume feedback generated successfully.
      400:
        description: Invalid input data.
    """
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    feedback = generate_resume_feedback(user_resume, job_description)
    return jsonify({"feedback": feedback}), 200

@application_bp.route('/generate-cover-letter', methods=['POST'])
def cover_letter():
    """
    Generates a cover letter based on the user's resume and job description.
    ---
    tags:
      - Application
    summary: Generate cover letter
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            userResume:
              type: string
            jobDescription:
              type: string
    responses:
      200:
        description: Cover letter generated successfully.
      400:
        description: Invalid input data.
    """
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    cover_letter = generate_cover_letter(user_resume, job_description)
    return jsonify({"cover_letter": cover_letter}), 200

@application_bp.route('/generate-interview-questions', methods=['POST'])
def interview_questions():
    """
    Generates interview questions based on the user's resume and job description.
    ---
    tags:
      - Application
    summary: Generate interview questions
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            userResume:
              type: string
            jobDescription:
              type: string
    responses:
      200:
        description: Interview questions generated successfully.
      400:
        description: Invalid input data.
    """
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    questions = generate_interview_questions(user_resume, job_description)
    return jsonify({"questions": questions}), 200

@application_bp.route('/process-application', methods=['POST'])
@jwt_required()
def process_application_endpoint():
    """
    Processes the application and generates feedback, a cover letter, and interview questions.
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "Unauthorized access"}), 401

        data = request.get_json()
        user_resume = data.get('userResume')
        job_description = data.get('jobDescription')

        if not user_resume or not job_description:
            return jsonify({"error": "Missing required fields"}), 400

        application_result = process_application(user_id, user_resume, job_description)

        if 'error' in application_result:
            return jsonify({"error": "Failed to process application"}), 500

        return jsonify({"message": "Application processed", "application": application_result}), 200

    except Exception as e:
        print(f"Error in /process-application: {e}")
        return jsonify({"error": str(e)}), 500

@application_bp.route('/<user_id>/applications', methods=['GET'])
@jwt_required()
def get_applications(user_id):
    """
    Retrieves all applications for a user.
    ---
    tags:
      - Application
    summary: Get all applications for a user
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: A list of applications.
      404:
        description: No applications found.
    """
    applications = get_user_applications(user_id)

    if applications:
        return jsonify({"applications": applications}), 200
    return jsonify({"error": "No applications found"}), 404

@application_bp.route('/<user_id>/application/<application_id>', methods=['GET'])
@jwt_required()
def get_application(user_id, application_id):
    """
    Retrieves details of a specific application.
    ---
    tags:
      - Application
    summary: Get application details
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - name: application_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Application details retrieved successfully.
      404:
        description: Application not found.
    """
    application = get_application_details(user_id, application_id)

    if application:
        return jsonify(application), 200
    return jsonify({"error": "Application not found"}), 404

@application_bp.route('/<user_id>/application/<application_id>/cover-letter', methods=['GET'])
@jwt_required()
def get_cover_letter(user_id, application_id):
    """
    Retrieves the cover letter for a given application.
    ---
    tags:
      - Application
    summary: Get cover letter by application ID
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - name: application_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Cover letter retrieved successfully.
      404:
        description: Cover letter not found.
    """
    cover_letter = get_application_cover_letter(user_id, application_id)

    if cover_letter:
        return jsonify(cover_letter), 200
    return jsonify({"error": "Cover letter not found"}), 404

@application_bp.route('/<user_id>/application/<application_id>/interview-questions', methods=['GET'])
@jwt_required()
def get_interview_questions(user_id, application_id):
    """
    Retrieves interview questions for a given application.
    ---
    tags:
      - Application
    summary: Get interview questions by application ID
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - name: application_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Interview questions retrieved successfully.
      404:
        description: No interview questions found.
    """
    questions = get_application_interview_questions(user_id, application_id)

    if questions:
        return jsonify(questions), 200
    return jsonify({"error": "No interview questions found"}), 404

# Delete an application
@application_bp.route('/<user_id>/application/<application_id>', methods=['DELETE'])
@jwt_required()
def delete_application(user_id, application_id):
    """
    Deletes a specific application.
    ---
    tags:
      - Application
    summary: Delete an application
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - name: application_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Application deleted successfully.
      404:
        description: Application not found.
      500:
        description: Internal server error.
    """
    success = delete_application_by_user_id(user_id, application_id)
    if success:
        return jsonify({"message": "Application deleted successfully"}), 200
    return jsonify({"error": "Application not found or could not be deleted"}), 404