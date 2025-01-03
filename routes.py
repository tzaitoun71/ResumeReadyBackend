import os
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth import get_management_token, register_user, login_user
from services.user import update_user_resume
from services.cover_letter import generate_cover_letter
from services.interview_questions import generate_interview_questions
from services.pdf_parser import extract_text_from_pdf
from services.resume_feedback import generate_resume_feedback


def setup_routes(app, jwt):
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('firstName')
            last_name = data.get('lastName')

            if not all([email, password, first_name, last_name]):
                return jsonify({"error": "All fields are required"}), 400

            token = get_management_token()
            if not token:
                return jsonify({"error": "Failed to retrieve Auth0 Management Token"}), 500

            result = register_user(email, password, first_name, last_name)
            if 'error' in result:
                return jsonify(result), 400

            return jsonify(result), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')

            if not all([email, password]):
                return jsonify({"error": "Email and password are required"}), 400

            result = login_user(email, password)
            return jsonify(result), 200 if 'access_token' in result else 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/upload-pdf', methods=['POST'])
    @jwt_required()
    def upload_pdf():
        try:
            user_sub = get_jwt_identity()
            if not user_sub:
                return jsonify({"error": "Failed to extract user ID from token"}), 400

            file = request.files.get('file')
            if not file:
                return jsonify({"error": "No file provided"}), 400

            if not file.filename.endswith('.pdf'):
                return jsonify({"error": "Only PDF files are allowed"}), 400

            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            extracted_text = extract_text_from_pdf(file_path)
            os.remove(file_path)

            update_result = update_user_resume(user_sub, extracted_text)
            if not update_result:
                return jsonify({"error": "Failed to update user resume"}), 500

            return jsonify({"message": "Resume parsed and saved successfully.", "resumeText": extracted_text}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/resume-feedback', methods=['POST'])
    def resume_feedback():
        try:
            data = request.json
            user_resume = data.get('userResume')
            job_description = data.get('jobDescription')

            if not user_resume or not job_description:
                return jsonify({"error": "Both userResume and jobDescription are required."}), 400

            feedback = generate_resume_feedback(user_resume, job_description)
            return jsonify({"message": "Feedback generated successfully", "feedback": feedback}), 200

        except Exception as e:
            return jsonify({"error": "An error occurred while generating feedback."}), 500

    @app.route('/generate-cover-letter', methods=["POST"])
    def cover_letter():
        try:
            data = request.json
            user_resume = data.get('userResume')
            job_description = data.get('jobDescription')

            if not user_resume or not job_description:
                return jsonify({"error": "Both userResume and jobDescription are required."}), 400

            cover_letter = generate_cover_letter(user_resume, job_description)
            return jsonify({"message": "Cover Letter generated successfully", "cover_letter": cover_letter}), 200

        except Exception as e:
            return jsonify({"error": "An error occurred while generating a cover letter"}), 500

    @app.route('/generate-interview-questions', methods=['POST'])
    def interview_questions():
        try:
            data = request.json
            user_resume = data.get('userResume')
            job_description = data.get('jobDescription')

            questions = generate_interview_questions(user_resume, job_description)
            return jsonify({"message": "Questions generated successfully", "questions": questions}), 200

        except Exception as e:
            return jsonify({"error": "An error occurred while generating interview questions."}), 500
