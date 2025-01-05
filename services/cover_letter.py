from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_cover_letter(user_resume: str, job_description: str) -> dict:
    try:
        # Construct the prompt
        cover_letter_prompt = f"""
        You are an expert in writing professional cover letters. Given the following resume and job description, generate a personalized cover letter body for the applicant.

        **Cover Letter Requirements:**
        - Start with "Dear Hiring Manager,".
        - Introduce the applicant and express interest in the position and company.
        - Highlight key qualifications, skills, and experiences aligning with the job requirements.
        - Explain why the applicant is a great fit for the company and how they can contribute to the company's goals.
        - Ensure it is professionally written, concise, and formatted into 2-3 short paragraphs.

        **Resume**:
        {user_resume}

        **Job Description**:
        {job_description}

        Return your response strictly in JSON format with the following structure:
        {{
          "companyName": "Company Name Here",
          "position": "Position Here",
          "coverLetterBody": "Dear Hiring Manager, [Cover letter content in paragraphs]."
        }}
        """

        # Call OpenAI API with structured JSON output
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert cover letter writer. Return your response in strict JSON format."},
                {"role": "user", "content": cover_letter_prompt}
            ],
            max_tokens=1000,
            temperature=0.5,
            response_format={"type": "json_object"}  # Structured JSON output
        )

        # Extract and parse the response content
        response_content = completion.choices[0].message.content.strip()
        print("✅ Raw JSON Response from OpenAI:")
        print(response_content)

        parsed_response = json.loads(response_content)
        print("✅ Parsed JSON Response:")
        print(parsed_response)

        return parsed_response

    except json.JSONDecodeError as json_error:
        print(f"JSON Parsing Error: {json_error}")
        return {"error": "Failed to parse OpenAI JSON response."}

    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return {"error": str(e)}