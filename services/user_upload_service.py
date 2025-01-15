import os
from werkzeug.utils import secure_filename
from services.s3_service import upload_file_to_s3
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

        # Upload to S3
        file_url = upload_file_to_s3(file_path, user_id)

        # Update the database with the file URL
        update_result = update_user_resume(user_id, file_url)
        if not update_result:
            return {"error": "Failed to update user resume"}

        # Clean up the temp file
        os.remove(file_path)

        return {"resumeUrl": file_url}

    except Exception as e:
        print(f"Error in handle_file_upload: {e}")
        return {"error": str(e)}
