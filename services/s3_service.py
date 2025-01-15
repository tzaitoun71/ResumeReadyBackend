import boto3
import os
from botocore.exceptions import NoCredentialsError

AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

# S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION
)

def upload_file_to_s3(file_path: str, user_id: str) -> str:
    try:
        # Construct the S3 key directly under the "resumes" folder
        s3_key = f"resumes/{user_id}-resume.pdf"

        # Upload the file to S3
        s3_client.upload_file(file_path, AWS_S3_BUCKET, s3_key)

        # Return the file's public URL
        return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    except NoCredentialsError as e:
        print(f"Credentials not available: {e}")
        raise e
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise e

def download_file_from_s3(s3_key: str, download_path: str):
    try:
        s3_client.download_file(AWS_S3_BUCKET, s3_key, download_path)
    except NoCredentialsError as e:
        print(f"Credentials not available: {e}")
        raise e
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        raise e
