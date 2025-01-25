from flask import Blueprint, request, jsonify
from services.auth_service import validate_and_create_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/validate-user", methods=["POST"])
def validate_user():
    """
    Validates an Auth0 user and creates the user in the database if they don't exist.
    ---
    tags:
      - Auth
    summary: Validate Auth0 User
    description: Accepts an Auth0 access token, verifies it, and creates the user in the database if they don’t exist.
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        required: true
        description: Bearer token obtained from Auth0 authentication.
        schema:
          type: string
          example: "Bearer eyJhbGciOi..."
    responses:
      200:
        description: User validated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "User validated successfully"
                user:
                  type: object
                  properties:
                    userId:
                      type: string
                      example: "google-oauth2|112411845598082882088"
                    email:
                      type: string
                      example: "tzaitoun16@gmail.com"
                    firstName:
                      type: string
                      example: "Tariq"
                    lastName:
                      type: string
                      example: "Zaitoun"
      401:
        description: Unauthorized or invalid token.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Invalid Auth0 token"
      500:
        description: Internal server error.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Unexpected error occurred"
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        access_token = auth_header.split("Bearer ")[1]
        user_data = validate_and_create_user(access_token)

        if not user_data:
            return jsonify({"error": "Invalid or expired Auth0 token"}), 401

        return jsonify({"message": "User validated successfully", "user": user_data}), 200

    except Exception as e:
        print(f"Error in /validate-user: {e}")
        return jsonify({"error": str(e)}), 500
