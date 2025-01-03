import os
from flask import redirect, request, jsonify, session, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth import get_management_token, register_user, login_user
from services.user import update_user_resume
from services.cover_letter import generate_cover_letter
from services.interview_questions import generate_interview_questions
from services.pdf_parser import extract_text_from_pdf
from services.resume_feedback import generate_resume_feedback
import requests

# Environment Variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")


def setup_routes(app):
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Login Route
    @app.route('/login')
    def login():
        return redirect(
            f'https://{AUTH0_DOMAIN}/authorize'
            f'?response_type=code'
            f'&client_id={AUTH0_CLIENT_ID}'
            f'&redirect_uri={AUTH0_CALLBACK_URL}'
            f'&scope=openid profile email'
            f'&audience={AUTH0_AUDIENCE}'
        )

    # Callback Route
    @app.route('/callback')
    def callback():
        code = request.args.get('code')
        if not code:
            return "Authorization code not found", 400

        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": AUTH0_CALLBACK_URL
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(token_url, json=payload, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch tokens", "details": response.json()}), 400

        tokens = response.json()
        session['access_token'] = tokens.get('access_token')
        session['id_token'] = tokens.get('id_token')

        userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            return jsonify({"error": "Failed to fetch user info"}), 400

        session['user'] = userinfo_response.json()
        return redirect(url_for('dashboard'))

    # Logout Route
    @app.route('/logout')
    def logout():
        session.clear() 
        return redirect(
            f'https://{AUTH0_DOMAIN}/v2/logout'
            f'?client_id={AUTH0_CLIENT_ID}'
            f'&returnTo={os.getenv("AUTH0_CALLBACK_URL")}'
        )

    # Protected Route
    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    # Dashboard Route
    @app.route('/dashboard')
    def dashboard():
        user = session.get('user')
        if not user:
            return redirect(url_for('login'))
        return jsonify({
            "message": "Welcome to your dashboard",
            "user": user
        })

    # Upload PDF Route
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

            return jsonify({
                "message": "Resume parsed and saved successfully.",
                "resumeText": extracted_text
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Resume Feedback Route
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

    # Cover Letter Route
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

    # Interview Questions Route
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
