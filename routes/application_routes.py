from flask import Blueprint, request, jsonify
from services.application_service import process_application
from services.resume_feedback import generate_resume_feedback
from services.cover_letter import generate_cover_letter
from services.interview_questions import generate_interview_questions
from services.job_summary import summarize_job_description

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
    data = request.json
    user_resume = data.get('userResume')
    job_description = data.get('jobDescription')

    result = process_application(user_resume, job_description)
    return jsonify(result), 200

# Summarize Job Route
@application_bp.route('/summarize-job', methods=['POST'])
def summarize_job():
    data = request.json
    job_description = data.get('jobDescription')

    summary = summarize_job_description(job_description)
    return jsonify({"summary": summary}), 200