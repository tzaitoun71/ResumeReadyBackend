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
        You are an expert in writing professional cover letters. Create a personalized and polished cover letter tailored specifically to the job description and the applicant's resume.

        ### **Cover Letter Requirements:**
        - Start with "Dear Hiring Manager,".
        - Write a strong opening paragraph introducing the applicant, expressing interest in the position, and mentioning the company name.
        - Highlight the applicant's **education** (e.g., degree, university) and explain how it aligns with the job.
        - In the main body:
        - Highlight key **skills, achievements, and experiences** from both university and professional roles.
        - Provide **specific examples** from their resume to support these points.
        - Use **simple, clear, and natural language** that feels conversational yet professional.
        - End with a confident closing paragraph expressing enthusiasm for the opportunity and a willingness to discuss the role further.
        - **Avoid jargon, overly complex words, or repetitive phrases.**
        - Use simple words
        - Ensure the letter has a smooth flow, with 3–4 short, well-structured paragraphs.
        - Include **relevant keywords from the job description** naturally.

        ### **Resume:**
        {user_resume}

        ### **Job Description:**
        {job_description}

        ### **Return your response in JSON format:**
        {{
        "companyName": "Company Name Here",
        "position": "Position Here",
        "coverLetterBody": "Dear Hiring Manager, [A simple, clear, and professional cover letter in 3–4 well-structured paragraphs. Highlight the applicant's education, key skills, and achievements using examples from their resume. Keep it ATS-friendly and easy to read.]"
        }}

        """



        # Call OpenAI API with structured JSON output
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert cover letter writer. Return your response in strict JSON format."},
                {"role": "user", "content": cover_letter_prompt}
            ],
            max_tokens=750,
            temperature=0.5,
            response_format={"type": "json_object"}  # Structured JSON output
        )

        # Extract and parse the response content
        response_content = completion.choices[0].message.content.strip()
        # print("Raw JSON Response from OpenAI:")
        # print(response_content)

        parsed_response = json.loads(response_content)
        # print("Parsed JSON Response:")
        # print(parsed_response)

        return parsed_response

    except json.JSONDecodeError as json_error:
        print(f"JSON Parsing Error: {json_error}")
        return {"error": "Failed to parse OpenAI JSON response."}

    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return {"error": str(e)}