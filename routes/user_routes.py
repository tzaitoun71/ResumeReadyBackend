import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user import update_user_resume
from services.s3_service import upload_file_to_s3

user_bp = Blueprint('user', __name__)

# Define a local upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

@user_bp.route('/upload-pdf', methods=['POST'])
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

        # Save the file temporarily
        temp_folder = "/tmp"
        os.makedirs(temp_folder, exist_ok=True)  # Ensure the /tmp folder exists
        file_path = os.path.join(temp_folder, file.filename)
        file.save(file_path)

        # Upload to S3
        file_url = upload_file_to_s3(file_path, user_sub)

        # Update the database with the file URL
        update_result = update_user_resume(user_sub, file_url)
        if not update_result:
            return jsonify({"error": "Failed to update user resume"}), 500

        # Clean up the temp file
        os.remove(file_path)

        return jsonify({
            "message": "Resume uploaded successfully.",
            "resumeUrl": file_url
        }), 200

    except Exception as e:
        print(f"Error in upload_pdf: {e}")
        return jsonify({"error": str(e)}), 500