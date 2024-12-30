from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_cover_letter(user_resume: str, job_description: str) -> str:
    try:
        cover_letter_prompt = f"""
        You are an expert in writing professional cover letters. Given the following resume and job description, generate a personalized cover letter body for the applicant starting from "Dear Hiring Manager,". Do not include any contact details or closing statements. Focus only on the content that would go in the main paragraphs of a cover letter.

        The cover letter body should:
        - Start with "Dear Hiring Manager,".
        - Introduce the applicant and express interest in the position and company.
        - Highlight the applicant's key qualifications, skills, and experiences that align with the job requirements.
        - Discuss why the applicant is a great fit for the company and how they can contribute to the company's goals.

        Ensure the cover letter body is formatted correctly with appropriate spacing and paragraphs, and is concise and use simple words.

        **Resume**:
        {user_resume}

        **Job Description**:
        {job_description}

        **Cover Letter Body**:
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert cover letter writer."},
                {"role": "user", "content": cover_letter_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        response_content = completion.choices[0].message.content.strip()
        return response_content
    
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return {"error": str(e)}