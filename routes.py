from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.auth import login_user, register_user
from services.cover_letter import generate_cover_letter
from services.interview_questions import generate_interview_questions
from services.pdf_parser import extract_text_from_pdf
from services.resume_feedback import generate_resume_feedback
import os

from services.user import update_user_resume

def setup_routes(app):
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    @app.route('/upload-pdf', methods=['POST'])
    @jwt_required()
    def upload_pdf():
        # Upload a PDF file, extract its text, and return it.
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file provided"}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        try:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Extract text from PDF
            extracted_text = extract_text_from_pdf(file_path)

            # Clean up the uploaded file
            os.remove(file_path)

            # Get user's identity
            user_email = get_jwt_identity()

            # Update user's resume in MongoDB
            update_result = update_user_resume(user_email, extracted_text)

            if not update_result:
                return jsonify({"error": "Failed to update user resume"}), 500

            return jsonify({
                "message": "Resume parsed and saved successfully.",
                "resumeText": extracted_text
            }), 200
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/resume-feedback', methods=['POST'])
    def resume_feedback():
        try:
            data = request.json

            # Extract fields from request
            user_resume = data.get('userResume')
            job_descrption = data.get('jobDescription')

            if not user_resume or not job_descrption:
                return jsonify({"error": "Both userResume and jobDescription are required."}), 400
            
            # Generate resume feedback
            feedback = generate_resume_feedback(user_resume, job_descrption)

            return jsonify({"message": "Feedback generated successfully", "feedback": feedback}), 200
        
        except Exception as e:
            print(f"Error in /resume-feedback: {e}")
            return jsonify({"error": "An error occurred while generating feedback."}), 500
        
    @app.route('/generate-cover-letter', methods=["POST"])
    def cover_letter():
        try:
            data = request.json
            user_resume = data.get('userResume')
            job_description = data.get('jobDescription')

            if not user_resume or not job_description:
                return jsonify({"error": "Both userResume and jobDescription are required."}), 400
            
            # Generate cover letter
            cover_letter = generate_cover_letter(user_resume, job_description)

            return jsonify({"message": "Cover Letter generated successfully", "cover_letter": cover_letter}), 200
        
        except Exception as e:
            print(f"Error in /generate-cover-letter: {e}")
            return jsonify({"error": "An error occured while generating a cover letter"})
    
    @app.route('/generate-interview-questions', methods=['POST'])
    def interview_questions():
        try:
            data = request.json
            user_resume = data.get('userResume')
            job_description = data.get('jobDescription')
            question_type = data.get('questionType', 'Technical')
            num_questions = data.get('numQuestions', 3)

            if not user_resume or not job_description:
                return jsonify({"error": "Both userResume and jobDescription are required."}), 400
            
            questions = generate_interview_questions(user_resume, job_description, question_type, num_questions)

            return jsonify({
                "message": "Interview questions generated successfully",
                "interviewQuestions": questions
            }), 200
        
        except Exception as e:
            print(f"Error in /generate-interview-questions: {e}")
            return jsonify({"error": "An error occurred while generating interview questions."}), 500
    
    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.json
            first_name = data.get('firstName')
            last_name = data.get('lastName')
            email = data.get('email')
            password = data.get('password')

            if not all([first_name, last_name, email, password]):
                return jsonify({"error": "All fields are required"}), 400
            
            result = register_user(first_name, last_name, email, password)
            return jsonify(result), 201 if 'message' in result else 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/login', methods=["POST"])
    def login():
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')
            
            if not all([email, password]):
                return jsonify({"error": "Email and password are required."}), 400
            
            result = login_user(email, password)
            if "access_token" in result:
                return jsonify({
                    "message": "Login successful",
                    "access_token": result["access_token"],
                    "id_token": result["id_token"],
                    "user": result["user"]
                }), 200
            else:
                return jsonify(result), 400
        
        except Exception as e:
            print(f"Error in /login: {e}")
            return jsonify({"error": "An error occurred during login."}), 500