import boto3
import os
import io
from botocore.exceptions import NoCredentialsError

# Load environment variables
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

# S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

# Uploads a file to the S3 bucket.
def upload_file_to_s3(file_path: str, user_id: str) -> str:
    try:
        s3_key = f"resumes/{user_id}-resume.pdf"
        s3_client.upload_file(file_path, AWS_S3_BUCKET, s3_key)
        return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise

# Fetches a file from the S3 bucket and returns it as an in-memory file.
def fetch_file_from_s3(user_id: str) -> io.BytesIO:
    try:
        s3_key = f"resumes/{user_id}-resume.pdf"
        s3_response = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=s3_key)
        pdf_content = s3_response["Body"].read()
        return io.BytesIO(pdf_content)
    except Exception as e:
        print(f"Error fetching file from S3: {e}")
        raise
