from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_upload_service import fetch_pdf_from_s3, handle_file_upload

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
        if "error" in result:
            return jsonify({"error": result["error"]}), 400

        return jsonify({
            "message": "Resume uploaded successfully.",
            "resumeUrl": result.get("resumeUrl", "No URL available")
        }), 200

    except Exception as e:
        print(f"Error in upload_pdf: {e}")
        return jsonify({"error": str(e)}), 500

@user_bp.route('/fetch-pdf', methods=['GET'])
@jwt_required()
def fetch_pdf():
    """
    Fetch the uploaded PDF from S3.
    ---
    tags:
      - User
    summary: Fetch PDF
    description: Retrieves the PDF file for the user's resume from S3.
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Access token.
    responses:
      200:
        description: PDF fetched successfully.
        schema:
          type: string
          example: "PDF downloaded to /path/to/local/file.pdf"
      400:
        description: Failed to fetch the PDF file.
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        temp_path = f"/tmp/{user_id}-resume.pdf"
        fetch_result = fetch_pdf_from_s3(user_id, temp_path)

        if isinstance(fetch_result, dict) and "error" in fetch_result:
            return jsonify(fetch_result), 400

        return jsonify({"message": f"PDF downloaded to {temp_path}"}), 200

    except Exception as e:
        print(f"Error in fetch_pdf: {e}")
        return jsonify({"error": str(e)}), 500
