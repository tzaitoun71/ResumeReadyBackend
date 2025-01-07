import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.pdf_parser import extract_text_from_pdf
from services.user import update_user_resume

user_bp = Blueprint('user', __name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@user_bp.route('/upload-pdf', methods=['POST'])
@jwt_required()
def upload_pdf():
    try:
        user_sub = get_jwt_identity()
        if not user_sub:
            return jsonify({"error": "Failed to extract user ID from token"}), 400

        file = request.files.get('file')
        if not file or not file.filename.endswith('.pdf'):
            return jsonify({"error": "A valid PDF file is required"}), 400

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
