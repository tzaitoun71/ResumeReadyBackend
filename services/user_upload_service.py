import os
from werkzeug.utils import secure_filename
from utils.pdf_parser import extract_text_from_pdf
from repositories.storage_repository import upload_file_to_s3
from services.user_service import update_user_resume

MAX_FILE_SIZE_KB = 400
ALLOWED_MIME_TYPE = "application/pdf"

# Handles file validation, uploads to S3, extracts text, and updates the user's resume.
def handle_file_upload(user_id: str, file) -> dict:
    try:
        # Ensures the uploaded file is a valid PDF
        if not file.filename.endswith(".pdf") or file.mimetype != ALLOWED_MIME_TYPE:
            return {"error": "Only PDF files are allowed"}

        # Check the file size
        file.seek(0, os.SEEK_END)
        file_size_kb = file.tell() / 1024 # Get file size in KB
        file.seek(0) # Reset file pointer
        if file_size_kb > MAX_FILE_SIZE_KB:
            return {"error": f"File size exceeds {MAX_FILE_SIZE_KB} KB"}

        # Create a temporary folder if it doesn't exist
        temp_folder = "/tmp"
        os.makedirs(temp_folder, exist_ok=True)

        # Secure the file name and save it temporarily
        file_path = os.path.join(temp_folder, secure_filename(file.filename))
        file.save(file_path)

        # Upload file to S3 and get the file URL
        s3_url = upload_file_to_s3(file_path, user_id)

        # Extract text from the uploaded PDF
        resume_text = extract_text_from_pdf(file_path)

        # Update the user's resume text in the database
        update_result = update_user_resume(user_id, resume_text)
        if not update_result:
            return {"error": "Failed to update user resume"}

        # Remove the temporary file
        os.remove(file_path)

        # Return the S3 file URL
        return {"resumeUrl": s3_url}
    except Exception as e:
        print(f"Error in handle_file_upload: {e}")
        return {"error": str(e)}
