from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_upload_service import handle_file_upload

user_bp = Blueprint('user', __name__)

@user_bp.route('/upload-pdf', methods=['POST'])
@jwt_required()
def upload_pdf():
    """
    Upload a PDF file for the user's resume.
    ---
    tags:
      - User
    summary: Upload a PDF
    description: Allows the user to upload a PDF file containing their resume.
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The PDF file to upload.
    responses:
      200:
        description: Resume uploaded successfully.
        schema:
          type: object
          properties:
            message:
              type: string
            resumeUrl:
              type: string
      400:
        description: Invalid input or error occurred during upload.
      500:
        description: Internal server error.
    security:
      - BearerAuth: []
    """
    try:
        user_sub = get_jwt_identity()
        if not user_sub:
            return jsonify({"error": "Failed to extract user ID from token"}), 400

        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file provided"}), 400

        result = handle_file_upload(user_sub, file)
        if result.get("error"):
            return jsonify({"error": result["error"]}), 400

        return jsonify({
            "message": "Resume uploaded successfully.",
            "resumeUrl": result["resumeUrl"]
        }), 200

    except Exception as e:
        print(f"Error in upload_pdf: {e}")
        return jsonify({"error": str(e)}), 500
