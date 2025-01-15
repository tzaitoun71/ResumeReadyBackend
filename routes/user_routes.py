from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_upload_service import handle_file_upload

user_bp = Blueprint('user', __name__)

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
