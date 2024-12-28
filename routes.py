from flask import request, jsonify
from services.pdf_parser import extract_text_from_pdf
import os

def setup_routes(app):
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    @app.route('/upload-pdf', methods=['POST'])
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

            return jsonify({"message": "Text extracted successfully", "text": extracted_text})
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
