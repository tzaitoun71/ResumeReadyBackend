import os
from werkzeug.utils import secure_filename
from services.pdf_parser import extract_text_from_pdf
from services.s3_service import download_file_from_s3, upload_file_to_s3
from services.user import update_user_resume

MAX_FILE_SIZE_KB = 400  # File size limit
ALLOWED_MIME_TYPE = "application/pdf"

def handle_file_upload(user_id: str, file) -> dict:
    try:
        # Validate file extension and MIME type
        if not file.filename.endswith('.pdf') or file.mimetype != ALLOWED_MIME_TYPE:
            return {"error": "Only PDF files are allowed"}

        # Limit file size
        file.seek(0, os.SEEK_END)
        file_size_kb = file.tell() / 1024  # File size in KB
        file.seek(0)  # Reset file pointer
        if file_size_kb > MAX_FILE_SIZE_KB:
            return {"error": f"File size exceeds the limit of {MAX_FILE_SIZE_KB} KB"}

        # Save the file temporarily
        temp_folder = "/tmp"
        os.makedirs(temp_folder, exist_ok=True)  # Ensure /tmp exists
        file_path = os.path.join(temp_folder, secure_filename(file.filename))
        file.save(file_path)

        # Upload the original file to S3
        s3_url = upload_file_to_s3(file_path, user_id)

        # Extract text from the PDF
        resume_text = extract_text_from_pdf(file_path)

        # Update the database with the parsed text
        update_result = update_user_resume(user_id, resume_text)
        if not update_result:
            return {"error": "Failed to update user resume"}

        # Clean up the temp file
        os.remove(file_path)

        return {"resumeUrl": s3_url}

    except Exception as e:
        print(f"Error in handle_file_upload: {e}")
        return {"error": str(e)}

    
def fetch_pdf_from_s3(user_id: str, destination_path: str) -> str:
    """
    Fetches a PDF file from S3 based on the user_id.
    """
    try:
        s3_key = f"resumes/{user_id}-resume.pdf"
        download_file_from_s3(s3_key, destination_path)
        return destination_path
    except Exception as e:
        print(f"Error fetching PDF from S3: {e}")
        return {"error": str(e)}
