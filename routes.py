import os
from flask import redirect, request, jsonify, session, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.application_service import process_application
from services.auth import exchange_code_for_tokens, fetch_user_info, save_user_to_db
from services.user import update_user_resume
from services.cover_letter import generate_cover_letter
from services.interview_questions import generate_interview_questions
from services.pdf_parser import extract_text_from_pdf
from services.resume_feedback import generate_resume_feedback

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
        try:
            code = request.args.get('code')
            if not code:
                return jsonify({"error": "Authorization code not provided"}), 400

            tokens = exchange_code_for_tokens(code)
            if not tokens:
                return jsonify({"error": "Failed to exchange code for tokens"}), 500

            user_info = fetch_user_info(tokens["access_token"])
            if not user_info:
                return jsonify({"error": "Failed to fetch user info"}), 500

            save_user_to_db(user_info)

            session['user'] = {
                "sub": user_info.get("sub"),
                "email": user_info.get("email"),
                "first_name": user_info.get("given_name", ""),
                "last_name": user_info.get("family_name", "")
            }
            session['tokens'] = {
                "access_token": tokens.get("access_token"),
                "id_token": tokens.get("id_token")
            }

            return jsonify({"message": "User logged in successfully"}), 200

        except Exception as e:
            print(f"Error in /callback: {e}")
            return jsonify({"error": str(e)}), 500
        
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
    
    # Temporary endpoint for development only
    @app.route('/tokens', methods=['GET'])
    def get_tokens():
        if 'user' not in session:
            return jsonify({"error": "User not logged in"}), 401

        tokens = session.get('tokens')
        if not tokens:
            return jsonify({"error": "No tokens found in session"}), 400

        return jsonify({
            "access_token": tokens.get("access_token"),
            "id_token": tokens.get("id_token")
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

    # Process Application Route
    @app.route('/process-application', methods=['POST'])
    def process_application_endpoint():
        try:
            # Parse request JSON
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400
            
            user_resume = data.get('userResume')
            job_description = data.get('jobDescription')
            question_type = data.get('questionType', 'Technical')
            num_questions = data.get('numQuestions', 3)
            
            # Validate required fields
            if not user_resume or not job_description:
                return jsonify({"error": "Both 'userResume' and 'jobDescription' fields are required."}), 400
            
            # Call the process_application function
            application_result = process_application(
                user_resume=user_resume,
                job_description=job_description,
                question_type=question_type,
                num_questions=num_questions
            )
            
            return jsonify(application_result), 200
        
        except Exception as e:
            print(f"Error in /process-application: {e}")
            return jsonify({"error": str(e)}), 500