from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from typing import Dict

load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_resume_feedback(user_resume: str, job_description: str) -> dict:
    try:
        # Construct the prompt
        resume_feedback_prompt = f"""
        You are an expert in resume analysis and job matching. Given the following resume and job description, provide an in-depth evaluation of how the resume can be refined to better match the job description.

        Your analysis should be detailed and specific, covering the following aspects. Ensure each piece of feedback is separated by the word "POINT" to distinguish different suggestions. Provide at least 8-12 unique and constructive points to thoroughly enhance the resume:
        - Identify specific sections of the resume that align well with the job description and explain why they are effective in detail.
        - Highlight any missing skills, experiences, or qualifications that are crucial for the job. Suggest specific additions that would significantly improve the match with the job description.
        - Point out any irrelevant sections or details in the resume that could detract from the application, and recommend their removal, explaining the impact.
        - Provide thorough suggestions for enhancing particular projects or experiences on the resume. Include advice on how to better detail, expand upon, or clarify these areas to align more closely with the job requirements.

        Additionally, provide a concise summary of the job description that captures its main requirements and expectations, including the job location, the key skills required, and what the company is specifically looking for in a candidate. Extract all relevant details such as the company name, position, and location. Format all outputs strictly in the following JSON format, using "POINT" to separate each piece of feedback:

        {{
          "companyName": "Company Name Here",
          "position": "Position Here",
          "location": "Location Here",
          "jobDescription": "Concise summary of the job description highlighting the location, key skills required, and specific qualities the company is looking for in a candidate",
          "resumeFeedback": "Describe how your experience in X aligns with the job requirements by detailing specific projects and outcomes, POINT Add metrics to the Y project to highlight its impact, such as the percentage increase in user engagement or cost savings, POINT Remove references to outdated technologies that are not relevant to the job, POINT Improve the description of your role at Z by specifying your leadership skills and any mentorship you provided, etc."
        }}

        **Resume**:
        {user_resume}

        **Job Description**:
        {job_description}

        **JSON Response (plain text only)**:
        """

        # Call OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a resume analysis assistant."},
                {"role": "user", "content": resume_feedback_prompt}
            ],
            max_tokens=2500,
            temperature=0.7
        )

        # Extract and parse the response content
        response_content = completion.choices[0].message.content.strip()
        parsed_response = json.loads(response_content)

        return parsed_response
    
    except json.JSONDecodeError as json_error:
        print(f"Error parsing JSON from OpenAI response: {json_error}")
        return {"error": "Failed to parse OpenAI response."}
    except Exception as e:
        print(f"Error generating resume feedback: {e}")
        return {"error": str(e)}
