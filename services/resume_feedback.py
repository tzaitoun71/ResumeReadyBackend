from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_resume_feedback(user_resume: str, job_description: str) -> dict:
    try:
        # Construct the prompt
        resume_feedback_prompt = f"""
        You are an expert in resume analysis and job matching. Given the following resume and job description, provide an in-depth evaluation of how the resume can be refined to better match the job description.

        Your analysis should include:
        - Specific sections of the resume that align well with the job description.
        - Missing skills, experiences, or qualifications that are crucial.
        - Irrelevant sections that should be removed.
        - Suggestions for enhancing particular projects or experiences.
        - job description must include all key details and summarize them into one clear and concise paragraph.
        job description should include:
        - Required skills and technologies  
        - Preferred skills (if mentioned)  
        - Key responsibilities (in brief)  
        - Years of experience required  
        - Salary details (if mentioned)  
        - Any unique attributes about the company or role 

        Return your response strictly in JSON format with the following structure:
        {{
          "companyName": "Company Name Here",
          "position": "Position Here",
          "location": "Location Here",
          "jobDescription": "Brief summary of the job description",
          "resumeFeedback": "Detailed and actionable feedback"
        }}

        **Resume**:
        {user_resume}

        **Job Description**:
        {job_description}
        """

        # Call OpenAI API with proper `response_format` as an object
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a resume analysis assistant. Return your response in strict JSON format."},
                {"role": "user", "content": resume_feedback_prompt}
            ],
            max_tokens=750,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        # Parse the response
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
        print(f"Error generating resume feedback: {e}")
        return {"error": str(e)}